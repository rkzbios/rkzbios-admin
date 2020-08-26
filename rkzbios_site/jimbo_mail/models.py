import re
import json
import uuid


from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from persistent.serializer import JsonUnSerializer, JsonSerializer

#@todo: using the django 1.6.6 validator
email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    # quoted-string, see also http://tools.ietf.org/html/rfc2822#section-3.2.5
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'
    r')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$)'  # domain
    r'|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$', re.IGNORECASE)  # literal form, ipv4 address (SMTP 4.1.3)

TOKEN_LENGTH = 36


SEND_FAILED_NO_RETRY = "FN"
SEND_FAILED_RETRY = "FR"
READY_TO_SEND = 'RE'
SENDING = 'SE'
SENT = 'ST'


MAIL_QUEUE_ITEM_STATUS_CHOICES = (
    (READY_TO_SEND, _("Ready")),
    (SENDING, _("Sending")),
    (SEND_FAILED_RETRY,_("Send failed retry")),
    (SEND_FAILED_NO_RETRY,_("Send failed, no retry")),
)


def _sanitize_email(email):
    return email.strip().lower()


def _email_is_valid(email):
    return email_re.match(email)


class BaseContainer(models.Model):
    """
    Basecontainer provides the base fields for its descendents
    id: unique id, a uid is used for generating an id
    """
    id = models.CharField(max_length=36, primary_key=True)
    clazzName = models.CharField(null=False, blank=False, max_length=125)
    data = models.TextField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    deletedAt = models.DateTimeField(null=True, blank=True)  # NOT USED FOR NOW, DO REAL DELETION

    class Meta:
        abstract = True


    """
    Sets and gets a object, expects a self.data property
    """

    def set_object(self, _object):
        setattr(self, "__object", _object)
        self.data = JsonSerializer().serialize(_object)

    def get_object(self):
        try:
            return getattr(self, "__object")
        except AttributeError:
            if self.data:
                _object = JsonUnSerializer().unserialize(self.data)
                _object._container = self
            else:
                _object = None
            setattr(self, "__object", _object)
            return _object

    def save(self, force_insert=False, force_update=False, using=None):
        if not self.id:
            self.id = str(uuid.uuid4())
        super(BaseContainer, self).save(force_insert=force_insert, force_update=force_update, using=using)


class SharedMailTemplate(BaseContainer):
    """
    Contains shared mail content, for example template that is used to generate the mail
    """
    pass


class MailQueue(BaseContainer):
    # the data contains embedded mail

    sharedMailTemplate = models.ForeignKey(SharedMailTemplate, null=True, blank=True, on_delete=models.SET_NULL)          # or its mailcontent
    senderName = models.CharField(max_length=64)
    mailFrom = models.CharField(max_length=256)
    mailTo = models.EmailField()
    userId = models.CharField(max_length=64, null=True, blank=True)
    organisationId = models.CharField(max_length=64, null=True, blank=True)
    unsubscribeUrl = models.CharField(max_length=150, null=True, blank=True)
    nrOfSendAttempts = models.IntegerField(default=0)
    status = models.CharField(max_length=3, choices=MAIL_QUEUE_ITEM_STATUS_CHOICES, default=READY_TO_SEND)
    sentAt = models.DateTimeField(blank=True, null=True)
    preferredSendTime = models.DateTimeField(default=timezone.now)
    deleteAfterSend = models.BooleanField(default=False)
    sendResponse = models.TextField(null=True)
    # SMTPException = models.CharField(max_length=32, null=True, blank=True)
    # SMTPCode  = models.CharField(max_length=8, null=True, blank=True)
    # SMPTError = models.CharField(max_length=128, null=True, blank=True)






class BouncedEmailAddress(models.Model):
    emailAddress = models.EmailField()
    isProcessed = models.BooleanField(default=False)


class MailServerConnection(BaseContainer):
    name = models.CharField(max_length=48, unique=True)


class MailSender(models.Model):
    name = models.CharField(max_length=48, unique=True)
    mailServerConnection = models.ForeignKey(MailServerConnection, on_delete=models.SET_NULL, null=True)