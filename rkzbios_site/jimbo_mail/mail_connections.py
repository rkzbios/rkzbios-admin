import requests

from persistent import models, fields, related
from smtplib import SMTPException
from smtplib import SMTPServerDisconnected, SMTPResponseException, SMTPSenderRefused, \
                SMTPRecipientsRefused, SMTPConnectError,SMTPHeloError, SMTPAuthenticationError

from django.core.mail import EmailMessage


class MailSendError(models.Model):

    class Meta:
        abstract = True

    shouldRetry = fields.BooleanField()


class MailSendResponse(models.Model):
    ok = fields.BooleanField()
    error = related.OneOf(MailSendError, null=True)


class MailGunSendError(MailSendError):
    errorMessage = fields.TextField()
    httpStatusCode = fields.IntegerField()


class ConnectionException(Exception):
    pass

class MailConnection(object):

    def open(self):
        pass

    def close(self):
        pass

    def send_message(self, from_email, to, cc=None, bcc=None,
                     subject=None, text=None, html=None, user_variables=None,
                     reply_to=None, headers=None, inlines=None, attachments=None, campaign_id=None):
        pass

class MailGunConnection(MailConnection):
    BASE_URL = 'https://api.eu.mailgun.net/v3'

    def __init__(self, domain, private_key, public_key=None):
        self.domain = domain
        self.private_key = private_key
        self.public_key = public_key
        self.auth = ('api', private_key)
        self.base_url = '{0}/{1}'.format(self.BASE_URL, domain)

    def open(self):
        pass

    def close(self):
        pass

    def post(self, path, data, auth=None, files=None, include_domain=True):
        mail_send_response = MailSendResponse()
        url = self.base_url if include_domain else self.BASE_URL
        response = requests.post(url + path, auth=auth or self.auth, data=data, files=files)

        if response.ok:
            mail_send_response.ok = True
        else:
            mail_send_response.ok = False
            mail_send_response.error = MailGunSendError(
                shouldRetry=False,
                errorMessage=response.text,
                httpStatusCode=response.status_code
            )

        return mail_send_response


    def get(self, path, params=None, auth=None, include_domain=True, path_includes_domain=False):
        url = self.base_url if include_domain else self.BASE_URL
        if path_includes_domain:
            url = ""
        return requests.get(url + path, auth=auth or self.auth, params=params)

    def delete(self, path, params=None, auth=None, include_domain=True):
        url = self.base_url if include_domain else self.BASE_URL
        return requests.delete(url + path, auth=auth or self.auth, params=params)

    def send_message(self, from_email, to, cc=None, bcc=None,
                     subject=None, text=None, html=None, user_variables=None,
                     reply_to=None, headers=None, inlines=None, attachments=None, campaign_id=None):
        # sanity checks
        assert (text or html)
        data = {
            'from': from_email,
            'to': to,
            'cc': cc or [],
            'bcc': bcc or [],
            'subject': subject or '',
            'text': text or '',
            'html': html or '',
        }
        if reply_to:
            data['h:Reply-To'] = reply_to
        if headers:
            for k, v in headers.items():
                data["h:%s" % k] = v
        if campaign_id:
            data['o:campaign'] = campaign_id
        if user_variables:
            for k, v in user_variables.items():
                data['v:%s' % k] = v

        files = []
        if inlines:
            for filename in inlines:
                files.append(('inline', open(filename, mode="rb")))
        if attachments:
            for filename in attachments:
                files.append(('attachment', open(filename, mode="rb")))
        return self.post('/messages', data, files=files)

    def get_bounces(self, nextBounces=None):

        if not nextBounces:
            bounces_response = self.get('/bounces')
        else:
            bounces_response = self.get(nextBounces, path_includes_domain=True)

        if bounces_response.status_code == 200:
            return bounces_response.json()
        else:
            raise Exception("")

    def delete_bounce(self, address):
        bounces_response = self.delete('/bounces/%s' % address)

        if bounces_response.status_code == 200:
            return bounces_response.json()


class SMTPSendError(MailSendError):
    SMTPException = fields.TextField()
    SMTPCode = fields.CharField(max_length=8, null=True, blank=True)
    SMTPError = fields.CharField(max_length=128, null=True, blank=True)

CONNECTION_ERROR_EXCEPTION_CLASSES = [SMTPServerDisconnected, SMTPConnectError,SMTPHeloError, SMTPAuthenticationError]


class SmtpRestoreConnectionException(ConnectionException):

    def __init__(self, smtp_exception):
        super(SmtpRestoreConnectionException, self).__init__()
        self.smtp_exception = smtp_exception


class SmtpConnectionWrapper(MailConnection):

    def __init__(self, connection):
        self.connection = connection

    def handle_and_store_exception(self, smtp_exception):
        smpt_send_error = SMTPSendError(
            SMTPException =smtp_exception.__class__.__name__,
            shouldRetry=True
        )
        if isinstance(smtp_exception, SMTPResponseException):
            smpt_send_error.SMTPCode = smtp_exception.smtp_code
            smpt_send_error.SMTPError = smtp_exception.smtp_error

        if isinstance(smtp_exception, SMTPRecipientsRefused):
            smpt_send_error.SMTPError = "%s" % smtp_exception.recipients  # RecipientsRefused
            smpt_send_error.shouldRetry = False

        if isinstance(smtp_exception, SMTPSenderRefused):
            smpt_send_error.SMTPError = "%s" % smtp_exception.sender  # SenderRefused
            smpt_send_error.shouldRetry = False

        if smtp_exception in CONNECTION_ERROR_EXCEPTION_CLASSES:
            # the connection is the problem so sending the mail must be stopped
            raise SmtpRestoreConnectionException()

        return smpt_send_error

    def send_message(self, from_email, to, cc=None, bcc=None,
                     subject=None, text=None, html=None, user_variables=None,
                     reply_to=None, headers=None, inlines=None, attachments=None, campaign_id=None):

        try:

            headers = {'Reply-To': reply_to}
            recipient_list = (to,)
            message = EmailMessage(subject, body=text, from_email=from_email, to=recipient_list, headers=headers)
            for attachment in attachments:
                message.attach_file(attachment)

            message.connection = self.connection
            message.send()
        except SMTPException as smtpException:
            return self.handle_and_store_exception(smtpException)
        except Exception as e:
            return SMTPSendError(
                SMTPException=e.message,
                shouldRetry=False
            )


class MailGunConnectionSettings(models.Model):
    domain = fields.CharField()
    privateKey = fields.CharField()
    publicKey = fields.CharField()
    maxNumberMailPerMonth = fields.IntegerField(default=5000)

    def create_connection(self):
        return MailGunConnection(self.domain, self.privateKey, public_key=self.publicKey)


class SMTPServerConnectionSettings(models.Model):
    """Configuration of a SMTP server"""
    name = fields.CharField(max_length=255)
    host = fields.CharField(max_length=255)
    user = fields.CharField(max_length=128, blank=True)
    password = fields.CharField(max_length=128, blank=True)
    port = fields.IntegerField(default=25)
    tls = fields.BooleanField()

    headers = fields.TextField(blank=True)
    # help_text=_('key1: value1 key2: value2, splitted by return line.\n'\
    #             'Useful for passing some tracking headers if your provider allows it.'))
    mails_hour = fields.IntegerField(default=0)


    def create_connection(self):
        pass # todo

    def connect(self):
        from smtplib import SMTP
        from django.utils.encoding import smart_str

        """Connect the SMTP Server"""
        smtp = SMTP(smart_str(self.host), int(self.port))
        smtp.ehlo_or_helo_if_needed()
        if self.tls:
            smtp.starttls()
            smtp.ehlo_or_helo_if_needed()

        if self.user or self.password:
            smtp.login(smart_str(self.user), smart_str(self.password))
        return smtp

    def delay(self):
        """compute the delay (in seconds) between mails to ensure mails
        per hour limit is not reached

        :rtype: float
        """
        if not self.mails_hour:
            return 0.0
        else:
            return 3600.0 / self.mails_hour

    def credits(self):
        """Return how many mails the server can send"""
        MAILER_HARD_LIMIT = 10000
        if not self.mails_hour:
            return MAILER_HARD_LIMIT

    """
        last_hour = datetime.now() - timedelta(hours=1)
        sent_last_hour = ContactMailingStatus.objects.filter(
            models.Q(status=ContactMailingStatus.SENT) |
            models.Q(status=ContactMailingStatus.SENT_TEST),
            newsletter__server=self,
            creation_date__gte=last_hour).count()
        return self.mails_hour - sent_last_hour
    """

    @property
    def custom_headers(self):
        if self.headers:
            headers = {}
            for header in self.headers.splitlines():
                if header:
                    key, value = header.split(':')
                    headers[key.strip()] = value.strip()
            return headers
        return {}

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.host)