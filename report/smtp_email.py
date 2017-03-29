# coding: utf-8
import smtplib
import email

from .localemail import Email


class SMTPEmail(Email):
    """ Send dashboard by email using SMTP protocol """

    def __init__(self, subject, email_from, email_to, credentials):
        Email.__init__(self, subject, email_from, email_to)
        self._create_smtp_server(credentials)

    def _create_smtp_server(self, credentials):
        self.server = smtplib.SMTP(credentials.get("host"), credentials.get("port"))
        self.server.starttls()
        self.server.login(credentials.get('user'), credentials.get('password'))

    def send(self, html):
        msg_html = email.mime.Text.MIMEText(html, 'html', 'utf-8')
        self.msg_alternative.attach(msg_html)
        self.server.sendmail(self.email_from, self.email_to, self.msg.as_string())

