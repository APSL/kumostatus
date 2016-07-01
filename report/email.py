# -*- coding: utf-8 -*-
import cgi
import uuid
import os
import boto3
import base64
import pprint
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.image     import MIMEImage
from email.header         import Header

class EMAIL(object):

    test = 1

    def __init__(self, subject, email_from="", email_to=""):

        self.test = 2

        self.email_from = email_from
        self.email_to = email_to

        self.client = boto3.client('ses')

        self.msg = MIMEMultipart('related')
        self.msg['Subject'] = Header(subject, 'utf-8')
        self.msg['From'] = email_from
        self.msg['To'] = ", ".join([email_to])
        self.msg_alternative = MIMEMultipart('alternative')
        self.msg.attach(self.msg_alternative)

    def add_graphs(self, graphs):

        for graph in graphs:
            self.add_image(
                base64.b64decode(graph["image_base64"]),
                title=graph["Title"],
                cid=graph["uuid"]
            )

    def add_alarms(self, alarms):
        for an in [1,2]:
            for alarm in alarms.alarms[an]:
                self._load_alarm(alarm)

            for alarm in alarms.warnings[an]:
                self._load_alarm(alarm)

    def _load_alarm(self, alarm):
        if alarm['image_base64'] != "":
            self.add_image(
                base64.b64decode(alarm["image_base64"]),
                title=alarm["name"],
                cid=alarm["uuid"]
            )

    def add_image(self, image, title="", cid=""):
        msg_image = MIMEImage(image, name=title)
        self.msg.attach(msg_image)
        msg_image.add_header('Content-ID', '<{}>'.format(cid))

    def send(self, html):

        msg_html = MIMEText(html,'html', 'utf-8')
        self.msg_alternative.attach(msg_html)

        self.client.send_raw_email(
            Source = self.email_from,
            Destinations = [ self.email_to, ],
            RawMessage = {
                "Data": self.msg.as_string()
            }
        )
