import uuid
import os
from django.test import TestCase
from django.conf import settings

from tickets.utils import create_pdf


from decimal import Decimal
from home.models import HomePage, MoviePage, Moviedate
from tickets.model import TicketRequest
import datetime
from tickets.service import ticket_service, TICKET_PRICE, DISCOUNT

from jimbo_mail.mail_connections import MailGunConnectionSettings
from jimbo_mail.models import MailSender, MailServerConnection

FREE = Decimal(0.00)


class TestPrinting(TestCase):


    # def testCreatePrint(self):
    #     aid = str(uuid.uuid4())
    #     pdf_name = "%s.%s" % (aid, "pdf")
    #
    #
    #     tickets_dir = "tickets"
    #     full_tickets_dir = os.path.join(settings.MEDIA_ROOT, tickets_dir)
    #     os.makedirs(full_tickets_dir, exist_ok=True)
    #
    #     ticket_path = os.path.join(tickets_dir,pdf_name)
    #     ticket_pdf_storage_path = os.path.join(settings.MEDIA_ROOT, ticket_path)
    #
    #     create_pdf(aid,"342424.342.3424234234.3242342341",ticket_pdf_storage_path)

    def setUp(self):

        home_page = HomePage(
            title="test",
            depth=2,
            path="00010002")
        home_page.save()

        movie_page = MoviePage(
            title="Jojo Rabbit",
            depth=3,
            path="000100020001",
        )
        movie_page.save()

        from django.utils import timezone

        movie_date_1 = Moviedate(
            page=movie_page,
            date=timezone.datetime(year=2020, month=11, day=29, hour=20, minute=30)
        )
        movie_date_1.save()
        self.movie_movie_date_id = movie_date_1.id

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
            name="rkzbios",
            mailServerConnection=mail_server_connection
        )
        mail_sender.save()

    def test_availability(self):

        availability = ticket_service.get_availability(self.movie_movie_date_id)

        self.assertEqual(availability.nrOfSingleSeatsTicketsAvailable, 6)
        self.assertEqual(availability.nrOfDoubleSeatsTicketsAvailable, 7)
        self.assertEqual(availability.movieDateId, self.movie_movie_date_id)

    def _create_ticket_request(self, payment_types, nr_of_seats):
        return TicketRequest(
            movieDateId=self.movie_movie_date_id,
            terms=True,
            email="robert.hofstra@gmail.com",
            emailVerification="robert.hofstra@gmail.com",
            paymentTypes=payment_types,
            nrOfSeats=nr_of_seats
        )

    def test_price_one_normal_ticket(self):

        one_normal_ticket_request = self._create_ticket_request(["normal"], 1)
        price_availability = ticket_service.get_price_availability(one_normal_ticket_request)
        self.assertEqual(price_availability.available, True)
        self.assertEqual(price_availability.price, TICKET_PRICE)
        self.assertEqual(price_availability.noPayment, False)

    def test_price_one_strippenkaart_ticket(self):

        one_normal_ticket_request = self._create_ticket_request(["strippenkaart"], 1)
        price_availability = ticket_service.get_price_availability(one_normal_ticket_request)
        self.assertEqual(price_availability.available, True)
        self.assertEqual(price_availability.price, FREE)
        self.assertEqual(price_availability.noPayment, True)

    def test_price_one_bioscooppas_ticket(self):

        one_normal_ticket_request = self._create_ticket_request(["bioscooppas"], 1)
        price_availability = ticket_service.get_price_availability(one_normal_ticket_request)
        self.assertEqual(price_availability.available, True)
        self.assertEqual(price_availability.price, FREE)
        self.assertEqual(price_availability.noPayment, True)

    def test_price_one_stadjespas_ticket(self):

        one_normal_ticket_request = self._create_ticket_request(["stadjespas"], 1)
        price_availability = ticket_service.get_price_availability(one_normal_ticket_request)
        self.assertEqual(price_availability.available, True)
        self.assertEqual(price_availability.price, TICKET_PRICE - DISCOUNT)
        self.assertEqual(price_availability.noPayment, False)

    def test_price_one_studentenpas_ticket(self):
        one_normal_ticket_request = self._create_ticket_request(["studentenpas"], 1)
        price_availability = ticket_service.get_price_availability(one_normal_ticket_request)
        self.assertEqual(price_availability.available, True)
        self.assertEqual(price_availability.price, TICKET_PRICE - DISCOUNT)
        self.assertEqual(price_availability.noPayment, False)

    def test_price_one_rkzmember_ticket(self):
        one_normal_ticket_request = self._create_ticket_request(["rkzmember"], 1)
        price_availability = ticket_service.get_price_availability(one_normal_ticket_request)
        self.assertEqual(price_availability.available, True)
        self.assertEqual(price_availability.price, TICKET_PRICE - DISCOUNT)
        self.assertEqual(price_availability.noPayment, False)


    def test_price_duo_normal_ticket(self):

        duo_normal_ticket_request = self._create_ticket_request(["normal","normal"], 2)
        price_availability = ticket_service.get_price_availability(duo_normal_ticket_request)
        self.assertEqual(price_availability.available, True)
        self.assertEqual(price_availability.price, 2 * TICKET_PRICE)
        self.assertEqual(price_availability.noPayment, False)

    def test_price_duo_normal_ticket(self):

        duo_normal_ticket_request = self._create_ticket_request(["normal","normal"], 2)
        price_availability = ticket_service.get_price_availability(duo_normal_ticket_request)
        self.assertEqual(price_availability.available, True)
        self.assertEqual(price_availability.price, 2 * TICKET_PRICE)
        self.assertEqual(price_availability.noPayment, False)

    def test_price_duo_normal_strippenkaart_ticket(self):

        duo_normal_ticket_request = self._create_ticket_request(["normal","strippenkaart"], 2)
        price_availability = ticket_service.get_price_availability(duo_normal_ticket_request)
        self.assertEqual(price_availability.available, True)
        self.assertEqual(price_availability.price, TICKET_PRICE)
        self.assertEqual(price_availability.noPayment, False)

    def test_price_duo_normal_rkzmember_ticket(self):

        duo_normal_ticket_request = self._create_ticket_request(["normal","rkzmember"], 2)
        price_availability = ticket_service.get_price_availability(duo_normal_ticket_request)
        self.assertEqual(price_availability.available, True)
        self.assertEqual(price_availability.price, TICKET_PRICE + TICKET_PRICE - DISCOUNT)
        self.assertEqual(price_availability.noPayment, False)

    def test_payment_ticket(self):
        from tickets.models import TICKET_STATUS_OPEN

        duo_normal_ticket_request = self._create_ticket_request(["normal","rkzmember"], 2)
        price_availability = ticket_service.get_price_availability(duo_normal_ticket_request)
        self.assertEqual(price_availability.available, True)
        self.assertEqual(price_availability.price, TICKET_PRICE + TICKET_PRICE - DISCOUNT)
        self.assertEqual(price_availability.noPayment, False)

        ticket_response = ticket_service.request_ticket(duo_normal_ticket_request)
        print(ticket_response.redirectUrl)
        ticket_service.sync_payment_status(ticket_response.ticketId)
        ticket_status = ticket_service.get_ticket_status(ticket_response.ticketId)

        self.assertEqual(ticket_status.status, TICKET_STATUS_OPEN)


    def test_request_strippenkaart_ticket(self):
        from tickets.models import TICKET_STATUS_OPEN, Ticket

        one_strippenkaart_ticket_request = self._create_ticket_request(["strippenkaart"], 1)
        price_availability = ticket_service.get_price_availability(one_strippenkaart_ticket_request)
        self.assertEqual(price_availability.available, True)
        self.assertEqual(price_availability.price, FREE)
        self.assertEqual(price_availability.noPayment, True)

        ticket_response = ticket_service.request_ticket(one_strippenkaart_ticket_request)

        self.assertEqual(ticket_response.redirectUrl, None)

        ticket = Ticket.objects.get(id=ticket_response.ticketId)
        mail_confirmation_id = ticket.mailConfirmationId
        self.assertNotEqual(mail_confirmation_id, None)

        mail_confirmation = ticket_service.mail_ticket_confirmation(mail_confirmation_id)

        self.assertEqual(mail_confirmation.confirmed, False)
        self.assertEqual(mail_confirmation.found, True)
        self.assertEqual(mail_confirmation.available, True)

        mail_confirmation = ticket_service.mail_ticket_confirmation(mail_confirmation_id, do_confirm=True)
        self.assertEqual(mail_confirmation.confirmed, True)
        self.assertEqual(mail_confirmation.found, True)
        self.assertEqual(mail_confirmation.available, True)


