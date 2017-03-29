# -*- coding: utf-8 -*-
import base64
import uuid
import email

import boto3


class Email(object):
    """ Base class for sending dashboard by email """

    def __init__(self, subject, email_from="", email_to=""):
        self.email_from = email_from
        self.email_to = email_to

        self.msg = email.mime.Multipart.MIMEMultipart('related')
        self.msg['Subject'] = subject
        self.msg['From'] = email_from
        self.msg['To'] = ", ".join([email_to])
        self.msg_alternative = email.mime.Multipart.MIMEMultipart('alternative')
        self.msg.attach(self.msg_alternative)

    def add_graphs(self, graphs):
        for graph in graphs:
            self.add_image(
                base64.b64decode(graph["image_base64"]),
                title=graph["Title"],
                cid=graph["uuid"]
            )

    def add_alarms(self, alarms):
        for an in [1, 2]:
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
        msg_image = email.mime.Image.MIMEImage(image, name=title)
        self.msg.attach(msg_image)
        msg_image.add_header('Content-ID', '<{}>'.format(cid))

    def send(self, html):
        raise NotImplementedError
