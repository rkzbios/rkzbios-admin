
import logging

from django.conf import settings
from django.utils import timezone
from django.db.models import Q

from persistent.serializer import JsonSerializer

from jimbo_mail.models import MailSender, MailQueue, READY_TO_SEND, SEND_FAILED_RETRY, SEND_FAILED_NO_RETRY, SENDING, SENT

mail_logger = logging.getLogger('mail.service')

MAX_NR_SEND_ATTEMPTS = 3


class MailService(object):

    def _get_connection(self, sender_name):
        mail_sender = MailSender.objects.filter(name=sender_name).first()
        if mail_sender and mail_sender.mailServerConnection:
            connection_settings = mail_sender.mailServerConnection.get_object()
            return connection_settings.create_connection()
        return None

    def add_batch(self, sender_name,
                  mail_from=None,
                  mail_batch=None,
                  delete_after_send=False,
                  organisation_id=None,
                  shared_mail_template_id=None):

        for mail_batch_item in mail_batch.mailBatchItems:
            mail = mail_batch_item.mail
            mail_to = mail_batch_item.mailTo
            user_id = mail_batch_item.userId
            unsubscribe_url = mail_batch_item.unsubscribeUrl
            preferred_send_time = mail_batch_item.preferredSendTime if mail_batch_item.preferredSendTime else timezone.now()
            mail_queue = MailQueue(
                sharedMailTemplate_id=shared_mail_template_id,
                mailTo=mail_to,
                mailFrom=mail_from,
                userId=user_id,
                organisationId=organisation_id,
                unsubscribeUrl=unsubscribe_url,
                preferredSendTime=preferred_send_time,
                deleteAfterSend=delete_after_send,
                senderName=sender_name,
                data=JsonSerializer().serialize(mail)
            )
            mail_queue.save()


    def send_mail(self, sender_name,
                  mail_from=None,
                  mail_to=None,
                  mail=None,
                  send_immediate=False,
                  delete_after_send=False,
                  organisation_id=None,
                  user_id=None,
                  preferred_send_time=None,
                  unsubscribe_url=None,
                  shared_mail_template_id=None):

        preferred_send_time = preferred_send_time if preferred_send_time else timezone.now()
        mail_queue = MailQueue(
            sharedMailTemplate_id=shared_mail_template_id,
            mailTo=mail_to,
            mailFrom=mail_from,
            userId=user_id,
            organisationId=organisation_id,
            unsubscribeUrl=unsubscribe_url,
            preferredSendTime=preferred_send_time,
            deleteAfterSend=delete_after_send,
            senderName=sender_name,
            data=JsonSerializer().serialize(mail)
        )
        mail_queue.save()

        if send_immediate:
            _connection = self._get_connection(sender_name)
            if _connection:
                _connection.open()
                try:
                    self._send_from_queue(_connection, mail_queue.id)
                finally:
                    _connection.close()

    def run(self):
        open_connections = {}

        def _get_and_cache_connection(sender_name):
            if sender_name in open_connections:
                _connection = open_connections[sender_name]
            else:
                _connection = self._get_connection(sender_name)
                open_connections[sender_name] = _connection
            if _connection:
                _connection.open()
            return _connection

        def _close_connections():
            for _connection in open_connections.values():
                if _connection:
                    _connection.close()

        can_send_status = Q(status=SEND_FAILED_RETRY) | Q(status=READY_TO_SEND)
        not_before_preferred_send_time = Q(preferredSendTime__lte=timezone.now())
        mail_to_send_filter = can_send_status & not_before_preferred_send_time
        mail_queue_items_to_send = MailQueue.objects.filter(mail_to_send_filter).only('id','senderName')
        try:
            for mail_queue_item_to_send in mail_queue_items_to_send:
                connection = _get_and_cache_connection(mail_queue_item_to_send.senderName)
                if connection:
                    self._send_from_queue(connection, mail_queue_item_to_send.id)
        finally:
            _close_connections()

    def _send_from_queue(self, connection, mail_queue_item_id):

        can_send_status = Q(status=SEND_FAILED_RETRY) | Q(status=READY_TO_SEND)
        can_send_this_mail = Q(id=mail_queue_item_id) & can_send_status

        nr_of_rows_updated = MailQueue.objects.filter(
            can_send_this_mail
        ).update(
            status=SENDING,
            sentAt=timezone.now()
        )
        if nr_of_rows_updated == 1:

            mail_queue_item = MailQueue.objects.get(id=mail_queue_item_id)
            mail_object = mail_queue_item.get_object()
            if mail_queue_item.sharedMailTemplate:
                shared_template = mail_queue_item.sharedMailTemplate.get_object()
                mail_object.set_shared_template(shared_template)

            subject = mail_object.get_subject()
            email_text = mail_object.get_text()
            html_text = mail_object.get_html()
            attachments = mail_object.get_attachments()
            mail_from = mail_queue_item.mailFrom
            reply_to_email = mail_queue_item.mailFrom

            mail_to = mail_queue_item.mailTo.strip()

            if settings.DEVELOPMENT:
                mail_to = settings.TEST_MAIL_ADDRESS

            response = connection.send_message(
                mail_from,
                mail_to,
                subject=subject,
                text=email_text,
                html=html_text,
                reply_to=reply_to_email,
                attachments=attachments
            )
            if not response.ok:
                # self.handle_and_store_exception(response, mail_queue_item)
                mail_logger.info("Error sending mail to: [%s]" % mail_to)

                if mail_queue_item.nrOfSendAttempts > MAX_NR_SEND_ATTEMPTS:
                    mail_queue_item.status = SEND_FAILED_NO_RETRY
                else:
                    mail_queue_item.status = SEND_FAILED_RETRY if response.error.shouldRetry else SEND_FAILED_NO_RETRY
                mail_queue_item.nrOfSendAttempts = mail_queue_item.nrOfSendAttempts + 1
                mail_queue_item.sendResponse = JsonSerializer().serialize(response)
                mail_queue_item.save()
            else:
                mail_logger.info("Sended mail to: [%s]" % mail_to)
                if not mail_queue_item.deleteAfterSend:
                    mail_queue_item.status = SENT
                    mail_queue_item.sendResponse = JsonSerializer().serialize(response)
                    mail_queue_item.save()
                else:
                    mail_queue_item.delete()  # may set other status, so we can see if there is any error


mail_service = MailService()