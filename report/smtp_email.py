# coding: utf-8
import smtplib
from email.mime.text import MIMEText

from .email import Email


class SMTPEmail(Email):
    """ Send dashboard by email using SMTP protocol """

    def __init__(self, subject, email_from, email_to, credentials):
        Email.__init__(self, subject, email_from, email_to)
        self._create_smtp_server(credentials)

    def _create_smtp_server(self, credentials):
        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        self.server.starttls()
        self.server.login(credentials.get('email'), credentials.get('password'))

    def send(self, html):
        msg_html = MIMEText(html, 'html', 'utf-8')
        self.msg_alternative.attach(msg_html)
        self.server.sendmail(self.email_from, self.email_to, self.msg.as_string())
