from django.test import TestCase

from jimbo_mail.mail_connections import MailGunConnectionSettings
from jimbo_mail.documents import Mail, MailBatch, MailBatchItem
from jimbo_mail.models import MailSender, MailServerConnection
from jimbo_mail.services import mail_service


class TestMailGun(TestCase):

    def setUp(self):
        from persistent.serializer import JsonSerializer
        mg = MailGunConnectionSettings(
            domain='sandboxdcf43d206af14bfea97d9935782f6cc4.mailgun.org',
            privateKey='key-7ecc7c60f368bdef2f5f84fba4145423',
            publicKey='pubkey-cc185b9df1e0a47d3b50be5d24c242f1'
        )

        mail_server_connection = MailServerConnection(
            name="sandbox.mailgun.org"
        )
        mail_server_connection.set_object(mg)
        mail_server_connection.save()

        mail_sender = MailSender(
            name="testmailsender",
            mailServerConnection=mail_server_connection
        )
        mail_sender.save()

    def testSendMailImmediately(self):

        mail_from = "Tickets Betavak<info@andboxdcf43d206af14bfea97d9935782f6cc4.mailgun.org>"
        mail = Mail(
            subject="Testmail",
            mailText="Dit is een testmail"
        )

        mail_service.send_mail(
            "testmailsender",
            mail_from=mail_from,
            mail_to="robert.hofstra@gmail.com",
            mail=mail,
            send_immediate=True
        )

    def testSendBatch(self):
        mail_from = "Tickets Betavak<info@andboxdcf43d206af14bfea97d9935782f6cc4.mailgun.org>"

        mail_batch = MailBatch(mailBatchItems=[])
        mail_batch.mailBatchItems.append(
            MailBatchItem(
                mail=Mail(
                    subject="Testmail 1",
                    mailText="Dit is een testmail 1"
                ),
                mailTo="robert.hofstra@gmail.com"
            )
        )

        mail_batch.mailBatchItems.append(
            MailBatchItem(
                mail=Mail(
                    subject="Testmail 2",
                    mailText="Dit is een testmail 2"
                ),
                mailTo="robert.hofstra@gmail.com"
            )
        )

        mail_service.add_batch(
            "testmailsender",
            mail_from=mail_from,
            mail_batch=mail_batch,
        )

        mail_service.run()