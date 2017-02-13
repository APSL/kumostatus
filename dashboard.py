#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getopt
import os
import sys
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import boto3
import config
import plot
import uuid

import get_stadistics
import alarms
import report

THIS_DIR = os.path.dirname(os.path.abspath(__file__)) + '/templates/'

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')

if __name__ == "__main__":
    save_filename = False
    email = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["hours=", "config=", "file=", "email=",])
    except getopt.GetoptError:
        print ('dashboard.py --config <config yaml> --hours <hours> --file <file>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--hours"):
            hours = int(arg)
        elif opt in ("-c", "--config"):
            config.Get(config=arg)
        elif opt in ("-f", "--file"):
            save_filename = arg
        elif opt in ("-e", "--email"):
            email = arg

    boto3.setup_default_session(
        aws_access_key_id=config.cfg['Credentials']['AWS_ID'],
        aws_secret_access_key=config.cfg['Credentials']['AWS_PASS'],
        region_name=config.cfg['Credentials']['region']
    )
    graphs = []

    for graphs_list in config.cfg["Graphs"]:

        for graph_key in graphs_list:

            graph_metrics = get_stadistics.Metric()
            graph_params = graphs_list[graph_key]

            for s in graph_params["metrics"]:
                metric = s["metric"]

                _dimensions = metric.get("dimensions", [])

                graph_metrics.add(get_stadistics.Get(
                    label=metric["label"],
                    hours=hours,
                    namespace=metric["namespace"],
                    name=metric["name"],
                    dimensions=_dimensions,
                    statistics=metric["statistics"],
                    unit=metric["unit"],
                    yaxis=metric["yaxis"]
                ))

                if "compare" in metric and type(metric["compare"]) is list and len(metric["compare"]) > 0:
                    for compare in metric["compare"]:
                        graph_metrics.add(get_stadistics.Get(
                            label="%s (-%sh)" % (metric["label"], compare),
                            hours=hours,
                            namespace=metric["namespace"],
                            name=metric["name"],
                            dimensions=_dimensions,
                            statistics=metric["statistics"],
                            unit=metric["unit"],
                            yaxis=metric["yaxis"],
                            compare=compare
                        ))


            graphs.append({
                "Title": graph_params["title"],
                "Timeframe": hours,
                "Generate tiem": datetime.utcnow().strftime("%Y"),
                "image_base64": plot.PNG(graph_metrics.metrics).image_base64(),
                "metrics": graph_metrics.metrics,
                "uuid": str(uuid.uuid4())
            })

    alarms_list = alarms.Get(hours=hours)

    if save_filename:
        j2_env = Environment(loader=FileSystemLoader(THIS_DIR),
                             trim_blocks=True)
        html = j2_env.get_template('overview.html').render(
            title=config.cfg["Template"]['title'],
            graphs=graphs,
            alarms=alarms_list,
            gentime=datetime.utcnow().strftime("%Y/%h/%d %H:%M:%S"),
        )

        f = open(save_filename, 'w')
        f.write(html)
        f.close()

    if email:
        if "smtp" in config.cfg['Credentials']:
            email_class = report.SMTPEmail
            email_credentials = config.cfg['Credentials']['smtp']

        elif "ses" in config.cfg['Credentials']:
            email_class = report.SESEmail
            email_credentials = config.cfg['Credentials']['ses']

        j2_env = Environment(loader=FileSystemLoader(THIS_DIR),
                             trim_blocks=True)
        html = j2_env.get_template('email.html').render(
            title=config.cfg["Template"]['title'],
            graphs=graphs,
            alarms=alarms_list,
            gentime=datetime.utcnow().strftime("%Y/%h/%d %H:%M:%S"),
        )

        mail_report = email_class(
            subject=config.cfg["Template"]['title'],
            email_from=config.cfg["Template"]["from"],
            email_to=email,
            credentials=email_credentials
        )
        mail_report.add_graphs(graphs)
        mail_report.add_alarms(alarms_list)
        mail_report.send(html)
