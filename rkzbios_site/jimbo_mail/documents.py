import os
from urllib import parse

from django.conf import settings

from persistent.models import Model as Document, DataAspect
from persistent import fields, related

from kiini.core.jinja import render_frto_string, render_to_string

JS_URL_VALIDATION_REGEX = '^(((ftp|http|https)(:[/][/]){1})|((www.){1}))[-a-zA-Z0-9@:%_\+.~#?&//=]+$'
JS_EMAIL_VALIDATION_REGEX = '^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$'


class FileReference(DataAspect):
    href = fields.CharField(blank=True)
    fileName = fields.CharField(blank=True)

    @property
    def file_path(self):
        p = parse(self.href)
        path = p.path

        media_url = settings.MEDIA_URL
        media_root = settings.MEDIA_ROOT + "/"

        file_path = path.replace(media_url, media_root)
        return file_path

    @property
    def extention(self):
        try:
            return os.path.splitext(self.fileName)[1]
        except:
            return ""


class LocalFileReference(FileReference):

    @property
    def file_path(self):
        return self.fileName

    @property
    def extention(self):
        try:
            return os.path.splitext(self.fileName)[1]
        except:
            return ""





class BaseMail(Document):

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shared_template = None

    def set_shared_template(self, shared_template):
        self.shared_template = shared_template

    def get_subject(self):
        pass

    def get_text(self):
        pass

    def get_html(self):
        pass

    def get_from_email(self):
        pass

    def get_reply_to_email(self):
        pass

    def get_attachments(self):
        return []


class Mail(BaseMail):
    subject = fields.CharField(verbose_name={"nl": "Onderwerp"})
    mailText = fields.TextField(verbose_name={"nl": "Inhoud"})
    htmlText = fields.TextField(verbose_name={"nl": "Html Inhoud"}, null=True, blank=True)
    # emailSender = fields.CharField(
    #     null=False,
    #     blank=False,
    #     verbose_name={"nl": "Email afzender"},
    #     js_validate_regex=JS_EMAIL_VALIDATION_REGEX)
    attachments = related.ListOf(FileReference, blank=True, null=True, verbose_name={"nl": "Bijlages"})

    def get_subject(self):
        return self.subject

    def get_text(self):
        return self.mailText

    def get_html(self):
        return self.htmlText

    # def get_from_email(self):
    #     return self.emailSender
    #
    # def get_reply_to_email(self):
    #     return self.emailSender

    def get_attachments(self):
        result = []
        if self.attachments:
            for attachment in self.attachments:
                result.append(attachment.file_path)
        return result


class MailBatchItem(Document):
    mail = related.OneOf(BaseMail)
    preferredSendTime = fields.DateTimeField(null=True)
    userId = fields.CharField(max_length=64,null=True)
    unsubscribeUrl = fields.CharField(max_length=256,null=True)

    mailTo = fields.CharField(
        null=False,
        blank=False,
        verbose_name={"nl": "Email afzender"},
        js_validate_regex=JS_EMAIL_VALIDATION_REGEX)


class MailBatch(Document):
    mailBatchItems = related.ListOf(MailBatchItem)


# class Mail(BaseMail):
#     """
#     This mail contains a templatetags in the mailtext
#     """
#
#     def render_txt_template(self, ctx):
#         return render_frto_string(self.mailText, ctx)

class SharedMailTemplate(Document):

    class Meta:
        abstract = True

    def render_subject(self, ctx):
        pass

    def render_txt(self, ctx):
        pass

    def render_html(self, ctx):
        pass


class TemplateMail(BaseMail):
    
    mailData = related.OneOf(Document)
    attachments = related.ListOf(FileReference, blank=True, null=True, verbose_name={"nl": "Bijlages"})
    emailSender = fields.CharField(
        null=False,
        blank=False,
        verbose_name={"nl": "Email afzender"},
        js_validate_regex=JS_EMAIL_VALIDATION_REGEX)

    def set_shared_template(self, shared_template):
        self.shared_template = shared_template

    def get_subject(self):
        return self.shared_template.render_subject(self.mailData)

    def get_text(self):
        return self.shared_template.render_txt(self.mailData)


    def get_html(self):
        return self.shared_template.render_html(self.mailData)

    def get_from_email(self):
        return self.emailSender

    def get_reply_to_email(self):
        return self.emailSender

    def get_attachments(self):
        result = []
        if self.attachments:
            for attachment in self.attachments:
                result.append(attachment.file_path)
        return result


