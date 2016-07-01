import datetime

import boto3
import numpy
import re
import json
import plot
import get_stadistics
import uuid
from pprint import pprint

class Get(object):

    hours = 1
    alarms = {}
    warnings = {}
    stable = {}

    def __init__(self, hours=1):

        self.hours = hours

        self.utcnow = datetime.datetime.utcnow()
        self.fromutc = self.utcnow - datetime.timedelta(minutes=self.hours * 60)


        self.alarms = {
            1: [],
            2: [],
        }

        self.warnings = {
            1: [],
            2: [],
        }

        self.stable = {
            1: [],
            2: [],
        }


        self.cloudwatch = boto3.client("cloudwatch")
        alarms_raw = self.cloudwatch.describe_alarms(
            MaxRecords=100
        )

        for alarm_raw in alarms_raw['MetricAlarms']:

            if not self.prepare(alarm_raw):
                continue

            if self.record['status'] == 'ALARM':
                self.record['image_base64'] = self.generate_graph(self.record['raw'])

                if self.record['level'] <= 1:
                    self.alarms[ self.record['level'] ].append(self.record)
                else:
                    self.warnings[ self.record['level'] ].append(self.record)

            else:
                if self.record['hadalarms']:
                    self.record['image_base64'] = self.generate_graph(self.record['raw'])
                    self.warnings[ self.record['level'] ].append(self.record)
                else:
                    self.stable[ self.record['level'] ].append(self.record)


    def prepare(self, alarm_raw):
        m = re.search('^([^\_]+)_(.+)?__(.+)_L([0-9])$', alarm_raw['AlarmName'])
        if not m:
            return False

        try:
            reasondata = json.loads(alarm_raw['StateReasonData'])
            count = len(reasondata['recentDatapoints'])
            current_value = sum(reasondata['recentDatapoints']) / count
        except:
            reasondata = {}
            current_value = 0;

        response = self.cloudwatch.describe_alarm_history(
            AlarmName=alarm_raw['AlarmName'],
            HistoryItemType='StateUpdate',
            StartDate=self.fromutc,
            EndDate=self.utcnow,
            MaxRecords=10,
        )

        # print pprint(response)

        new_history_items = []
        for history in response['AlarmHistoryItems']:
            history['HistoryData'] = json.loads(history['HistoryData'])
            if history['HistoryData']['newState']['stateValue'] == 'ALARM':
                new_history_items.append(history)

        hadalarms = False
        if len(new_history_items) > 0:
            hadalarms = True

        if "AlarmDescription" in alarm_raw:
            _description = alarm_raw["AlarmDescription"]
        else:
            _description = "[no description]"

        self.record = {
            'level': int(m.group(4)),
            'status': alarm_raw['StateValue'],
            'group': m.group(1),
            'name': m.group(2),
            'metric': m.group(3),
            'statereason': alarm_raw['StateReason'],
            'reasondata': reasondata,
            'current_value': current_value,
            '_name': alarm_raw['AlarmName'],
            'description': _description,
            'history': new_history_items,
            'hadalarms': hadalarms,
            'raw': alarm_raw,
            'uuid': str(uuid.uuid4()),
        }

        return True


    def generate_graph(self, alarm_raw):

        unit = "None"
        if alarm_raw["MetricName"] == 'CPUUtilization':
            unit = "Percent"
        elif alarm_raw["MetricName"] == 'Latency':
            unit = "Seconds"
        elif alarm_raw["MetricName"] == 'RequestCount':
            unit = "Count"
        elif alarm_raw["MetricName"] == 'NetworkOut':
            unit = "Bytes"
        elif alarm_raw["MetricName"] == "UnHealthyHostCount":
            unit = "Count"
        elif alarm_raw["MetricName"] == "HealthyHostCount":
            unit = "Count"
        elif alarm_raw["MetricName"] == "AuroraReplicaLag":
            unit = "Milliseconds"

        graph_metrics = get_stadistics.Metric()

        graph_metrics.add(get_stadistics.Get(
            hours=self.hours,
            namespace=alarm_raw["Namespace"],
            name=alarm_raw["MetricName"],
            dimensions=alarm_raw['Dimensions'],
            statistics=alarm_raw["Statistic"],
            unit=unit,
            yaxis=False
        ))

        return plot.PNG(graph_metrics.metrics).image_base64()
