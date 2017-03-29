# coding: utf-8
import boto3
from .localemail import Email
import email


class SESEmail(Email):
    """ Send dashboard by email using Amazon SES """

    def __init__(self, subject, email_from, email_to, credentials):
        Email.__init__(self, subject, email_from, email_to)
        boto3.setup_default_session(
            aws_access_key_id=credentials['AWS_ID'],
            aws_secret_access_key=credentials['AWS_PASS'],
            region_name=credentials['region']
        )
        self.client = boto3.client('ses')

    def send(self, html):
        msg_html = email.mime.Text.MIMEText(html, 'html', 'utf-8')
        self.msg_alternative.attach(msg_html)

        self.client.send_raw_email(
            Source=self.email_from,
            Destinations=[self.email_to, ],
            RawMessage={
                "Data": self.msg.as_string()
            }
        )
