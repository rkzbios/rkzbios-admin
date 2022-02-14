import os
import logging
import uuid
from decimal import Decimal

from datetime import timedelta


from pytz import timezone as pytz_timezone
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.conf import settings

from persistent.serializer import JsonSerializer
from jimbo_mail.documents import Mail, LocalFileReference

from home.models import Moviedate

from tickets.models import Ticket,  SEAT_CHOICE_SINGLE, SEAT_CHOICE_DOUBLE, \
    TICKET_TYPE_STRIPPENKAART, TICKET_TYPE_BIOSCOOPPAS,TICKET_TYPE_STADJESPAS, TICKET_TYPE_STUDENENTPAS, \
    TICKET_TYPE_RKZMEMBER, TicketStatus, EMAIL_STATUS_VERIFICATION_MAIL, TICKET_STATUS_ACCEPTED, \
    TICKET_STATUS_REJECTED, TICKET_STATUS_CREATED, TICKET_STATUS_OPEN, \
    TICKET_SEND_STATUS_NO_TICKET, TICKET_SEND_STATUS_REQUEST_TICKET_CREATE, TICKET_SEND_STATUS_TICKET_START_CREATED, \
    TICKET_SEND_STATUS_TICKET_CREATED, TICKET_SEND_STATUS_REQUEST_TICKET_SEND, TICKET_SEND_STATUS_TICKET_SENT,\
    EMAIL_STATUS_EMAIL_VERIFIED

from tickets.utils import create_pdf, create_acccess_token, get_short_code

PAYMENT_TYPES_WITH_DISCOUNT = [TICKET_TYPE_STADJESPAS, TICKET_TYPE_STUDENENTPAS, TICKET_TYPE_RKZMEMBER]

SEATS_AVAILABILITY = {
    SEAT_CHOICE_SINGLE: 68,
    SEAT_CHOICE_DOUBLE: 0
}

tickets_logger = logging.getLogger(__name__)


TICKET_PRICE = Decimal(7.00)
DISCOUNT = Decimal(2.00)


TICKET_FULL_FILL_TIME_FRAME_MINUTES = 15

def get_tz_aware_date(date):
    amsterdam_tz = pytz_timezone('Europe/Amsterdam')
    timezone_aware_date = date.astimezone(amsterdam_tz)
    return timezone_aware_date


def get_time_frame_max():
    open_within_time = timezone.now() - timedelta(minutes=TICKET_FULL_FILL_TIME_FRAME_MINUTES)
    return open_within_time


def get_ticket_description(movie_date):
    title = movie_date.page.title
    movie_date_str = movie_date.date.strftime("%d-%m %H:%M")
    movie_description = "%s - %s" % (title, movie_date_str)
    return "RKZBios ticket voor %s" % movie_description


def is_free_payment_type(payment_type):
    return payment_type == TICKET_TYPE_STRIPPENKAART or payment_type == TICKET_TYPE_BIOSCOOPPAS


def create_ticket_paths_and_name(the_date):
    relative_dir = os.path.join("tickets","%s-%s-%s" % (the_date.day, the_date.month, the_date.year))
    full_path_tickets_dir = os.path.join(settings.MEDIA_ROOT, relative_dir)
    aid = str(uuid.uuid4())
    pdf_name = "%s.%s" % (aid, "pdf")

    full_path_ticket = os.path.join(full_path_tickets_dir, pdf_name)
    relative_path_ticket = os.path.join(relative_dir, pdf_name)
    return full_path_tickets_dir, full_path_ticket, relative_path_ticket


class TicketService(object):

    @staticmethod
    def _get_nr_accepted_tickets(movie_date_id):

        return Ticket.objects.filter(
            movieDate_id=movie_date_id,
            status=TICKET_STATUS_ACCEPTED
        ).count()

    @staticmethod
    def _get_nr_available_seats(movie_date_id, nr_of_seats):

        open_within_time = get_time_frame_max()
        is_before_end_time_frame = Q(status=TICKET_STATUS_OPEN) & Q(createdAt__gte=open_within_time)
        open_or_accepted = is_before_end_time_frame | Q(status=TICKET_STATUS_ACCEPTED)
        nr_of_seats_used = Ticket.objects.filter(
            movieDate_id=movie_date_id,
            nrOfSeats=nr_of_seats
        ).filter(open_or_accepted).count()

        nr_of_seats_available = 0
        if nr_of_seats in SEATS_AVAILABILITY:
            nr_of_seats_available = SEATS_AVAILABILITY[nr_of_seats] - nr_of_seats_used

        return nr_of_seats_available

    @staticmethod
    def get_ticket_print_data(ticket_id):
        from tickets.model import TicketPrintData

        ticket = Ticket.objects.get(id=ticket_id)
        if ticket.status == TICKET_STATUS_ACCEPTED:
            movie_date = ticket.movieDate.date
            movie_title = ticket.movieDate.page.title
            ticket_request = ticket.get_ticket_request()
            code = ticket.code
            qr_code = ticket.code
            ticket_number = ticket.referenceNumber


            ticket_print_data = TicketPrintData(
                code=code,
                ticketNumber=ticket_number,
                ticketRequest=ticket_request,
                movieDate=get_tz_aware_date(movie_date),
                movieTitle=movie_title,
                qrCode=qr_code
            )
            return ticket_print_data
        else:
            return None

    def get_availability(self, movie_date_id):
        from tickets.model import TicketAvailability

        movie_date = Moviedate.objects.get(pk=movie_date_id)

        nr_of_single_seats_available = self._get_nr_available_seats(movie_date_id, SEAT_CHOICE_SINGLE)
        nr_of_double_seats_available = self._get_nr_available_seats(movie_date_id, SEAT_CHOICE_DOUBLE)

        availability_data = TicketAvailability(
            movieTitle=movie_date.page.title,
            movieDateId=movie_date_id,
            movieDate=get_tz_aware_date(movie_date.date),
            isPassed=movie_date.is_passed,
            latestSellTime=movie_date.latest_sell_time,
            nrOfSingleSeatsTicketsAvailable=nr_of_single_seats_available,
            nrOfDoubleSeatsTicketsAvailable=nr_of_double_seats_available
        )
        return availability_data

    def get_ticket_status(self, ticket_id):
        from tickets.model import TicketStatus

        ticket = Ticket.objects.get(id=ticket_id)
        movie_date = ticket.movieDate.date
        movie_title = ticket.movieDate.page.title

        if ticket.status == TICKET_STATUS_OPEN and ticket.paymentId is not None:
            self.sync_payment_status(ticket.id)
            ticket = Ticket.objects.get(id=ticket_id)

        ticket_status = TicketStatus(
            status=ticket.status,
            ticketRequest=ticket.get_ticket_request(),
            movieDate=get_tz_aware_date(movie_date),
            movieTitle=movie_title
        )
        return ticket_status

    @staticmethod
    def _no_payment(payment_types):
        no_payment = True
        for payment_type in payment_types:
            no_payment = no_payment and is_free_payment_type(payment_type)
        return no_payment

    @staticmethod
    def _get_price(payment_types):
        total_price = Decimal(0.00)
        for payment_type in payment_types:
            if not is_free_payment_type(payment_type):
                price = TICKET_PRICE
                if payment_type in PAYMENT_TYPES_WITH_DISCOUNT:
                    price = price - DISCOUNT
                total_price = total_price + price
        return total_price

    def get_price_availability(self, ticket_request):
        from tickets.model import PriceAvailability
        nr_of_tickets_available = self._get_nr_available_seats(ticket_request.movieDateId, ticket_request.nrOfSeats)
        no_payment = self._no_payment(ticket_request.paymentTypes)
        if no_payment:
            price = Decimal(0.00)
        else:
            price = self._get_price(ticket_request.paymentTypes)

        price_availability = PriceAvailability(
            available=nr_of_tickets_available > 0,
            price=price,
            noPayment=no_payment
        )
        price_availability.full_clean()
        return price_availability

    def _create_and_send_confirmation_mail(self, mail_to):
        mail_confirmation_id = uuid.uuid4()
        ticket_confirmation_url = "%s/ticketEmailConfirmation?confirmationId=%s" % \
                                  (settings.RKZBIOS_WEBSITE, mail_confirmation_id)

        mail = Mail(
            subject="Bevestig uw ticket aanvraag van de RKZBios",
            mailText="Wilt U uw ticket aanvraag bevestigen door op de bevestig knop te klikken op deze pagina: %s" % ticket_confirmation_url
        )
        self._send_mail(mail, mail_to)
        return mail_confirmation_id

    def mail_ticket_confirmation(self, mail_confirmation_id, do_confirm=False):
        from tickets.model import MailConfirmation
        from tickets.models import TICKET_STATUS_ACCEPTED, TICKET_STATUS_OPEN

        # open_within_time = get_time_frame_max()
        # is_before_end_time_frame = Q(status=TICKET_STATUS_OPEN) & Q(createdAt__gte=open_within_time)
        # open_or_accepted = is_before_end_time_frame | Q(status=TICKET_STATUS_ACCEPTED)

        ticket = Ticket.objects.filter(mailConfirmationId=mail_confirmation_id).first()

        if ticket:
            movie_date = ticket.movieDate.date
            movie_title = ticket.movieDate.page.title

            time_frame_end_time = get_time_frame_max()

            if ticket.status == TICKET_STATUS_ACCEPTED:
                confirmation_status = TICKET_STATUS_ACCEPTED
            elif ticket.status == TICKET_STATUS_OPEN and ticket.createdAt >= time_frame_end_time:
                confirmation_status = TICKET_STATUS_OPEN
            else:
                confirmation_status = TICKET_STATUS_REJECTED
                ticket.status = confirmation_status
                ticket.save()

            #
            # if not is_available:
            #     price_availability = self.get_price_availability(ticket.get_ticket_request())
            #     if price_availability.available:
            #         is_available = True

            if do_confirm and confirmation_status == TICKET_STATUS_OPEN:
                confirmation_status = TICKET_STATUS_ACCEPTED
                self._save_ticket_status(ticket.id, confirmation_status, EMAIL_STATUS_EMAIL_VERIFIED)
                self.create_and_send_ticket(ticket.id)

            return MailConfirmation(
                    confirmationId=mail_confirmation_id,
                    movieTitle=movie_title,
                    movieDate=get_tz_aware_date(movie_date),
                    confirmationStatus=confirmation_status
            )
        else:
            return None

    def _get_mollie_client(self):
        from mollie.api.client import Client
        mollie_client = Client()
        mollie_client.set_api_key(settings.MOLIE_API_KEY)
        return mollie_client

    def _create_payment(self, ticket_id, price, description):

        mollie_client = self._get_mollie_client()
        mollie_web_hook_url = '%s/api/tickets/mollie-callback/%s/' % (settings.MOLLIE_CALLBACK_HOST, ticket_id)
        redirect_url = '%s/ticketStatus?ticketId=%s' %  (settings.RKZBIOS_WEBSITE, ticket_id)

        # tickets_logger.info("mollie url %s " % mollie_web_hook_url)

        payment_data = {
            'amount': {
                'currency': 'EUR',
                'value': str(price)
            },
            'description': description,
            'webhookUrl': mollie_web_hook_url,
            'redirectUrl': redirect_url,
            'metadata': {
                'ticketId': ticket_id
            }
        }

        tickets_logger.debug("Start creating payment with data %s " % payment_data)

        payment = mollie_client.payments.create(payment_data)

        tickets_logger.debug("Payment created returned %s " % payment)

        return payment.id, payment.checkout_url, payment.status

    @transaction.atomic()
    def _save_ticket_status(self, ticket_id, status, ticket_status):
        ticket = Ticket.objects.get(id=ticket_id)
        current_status = ticket.status
        if current_status != TICKET_STATUS_ACCEPTED:
            ticket.status = status
            if status == TICKET_STATUS_ACCEPTED:
                ticket.code = get_short_code()
                ticket.referenceNumber = self._get_nr_accepted_tickets(ticket.movieDate_id) + 1
            ticket.save()
            TicketStatus(ticket=ticket, status=ticket_status).save()

    def _sync_payment_status(self, ticket_id):
        tickets_logger.debug("Start sync payment for ticket_id %s " % ticket_id)

        ticket = Ticket.objects.get(id=ticket_id)
        status_before = ticket.status

        mollie_client = self._get_mollie_client()

        payment = mollie_client.payments.get(ticket.paymentId)

        tickets_logger.debug("Payment status returned %s " % payment)

        status = TICKET_STATUS_REJECTED
        payment_status = payment['status']
        if payment.is_paid():
            # At this point you'd probably want to start the process of delivering the product to the customer.
            status = TICKET_STATUS_ACCEPTED
        elif payment.is_pending():
            # The payment has started but is not complete yet.
            status = TICKET_STATUS_OPEN
        elif payment.is_open():
            # The payment has not started yet. Wait for it.
            status = TICKET_STATUS_OPEN

        self._save_ticket_status(ticket_id, status, payment_status)

        return status_before, status

    def _request_create_pdf(self, ticket_id):
        if self._get_toggle_send_status(
                ticket_id,
                TICKET_SEND_STATUS_NO_TICKET,
                TICKET_SEND_STATUS_REQUEST_TICKET_CREATE):
            return True
        else:
            return False

    def _create_ticket_pdf(self, ticket_id):
        if self._get_toggle_send_status(
                ticket_id,
                TICKET_SEND_STATUS_REQUEST_TICKET_CREATE,
                TICKET_SEND_STATUS_TICKET_START_CREATED
        ):
            # yes we have locked
            try:
                ticket = Ticket.objects.get(id= ticket_id)
                the_date = ticket.movieDate.date
                full_path_tickets_dir, full_path_ticket, relative_path_ticket = create_ticket_paths_and_name(the_date)
                os.makedirs(full_path_tickets_dir, exist_ok=True)
                access_token = create_acccess_token()
                create_pdf(ticket_id, access_token, full_path_ticket)

                with transaction.atomic():
                    ticket = Ticket.objects.get(id=ticket_id)
                    ticket.ticketSendStatus = TICKET_SEND_STATUS_TICKET_CREATED
                    ticket.ticketPdf.name = relative_path_ticket
                    ticket.save()
                return True
            except:
                self._get_toggle_send_status(
                    ticket_id,
                    TICKET_SEND_STATUS_TICKET_START_CREATED,
                    TICKET_SEND_STATUS_REQUEST_TICKET_CREATE,
                )
                return False

    @transaction.atomic()
    def _get_toggle_send_status(self, ticket_id, current_status, new_status):
        nr_of_rows_updated = Ticket.objects.filter(
            id=ticket_id,
            ticketSendStatus=current_status
        ).update(ticketSendStatus=new_status)
        return nr_of_rows_updated == 1

    @transaction.atomic()
    def _set_send_status(self, ticket_id, new_status):
        nr_of_rows_updated = Ticket.objects.filter(
            id=ticket_id,
        ).update(ticketSendStatus=new_status)
        TicketStatus(ticket_id=ticket_id, status=new_status).save()
        return nr_of_rows_updated == 1

    def _send_mail(self, mail, mail_to):
        from jimbo_mail.services import mail_service
        mail_from = settings.MAIL_FROM

        mail_service.send_mail(
            settings.MAIL_SENDER_NAME,
            mail_from=mail_from,
            mail_to=mail_to,
            mail=mail,
            send_immediate=True
        )

    def _send_ticket(self, ticket_id):

        if self._get_toggle_send_status(
                ticket_id,
                TICKET_SEND_STATUS_TICKET_CREATED,
                TICKET_SEND_STATUS_REQUEST_TICKET_SEND):

            try:
                ticket = Ticket.objects.get(id=ticket_id)
                mail = Mail(
                    subject="Tickets RKZBios",
                    mailText="Bijgevoegd zijn de tickets van de RKZBios",
                    attachments=[LocalFileReference(fileName=os.path.join(settings.MEDIA_ROOT, ticket.ticketPdf.name))]
                )
                self._send_mail(mail,ticket.email)
                self._set_send_status(ticket_id, TICKET_SEND_STATUS_TICKET_SENT)
            except Exception as e:
                self._get_toggle_send_status(
                    ticket_id,
                    TICKET_SEND_STATUS_REQUEST_TICKET_SEND,
                    TICKET_SEND_STATUS_TICKET_CREATED)
                raise e

    def sync_payment_status(self, ticket_id):
        status_before, status_after = self._sync_payment_status(ticket_id)
        if status_after == TICKET_STATUS_ACCEPTED and status_before == TICKET_STATUS_OPEN:
            self.create_and_send_ticket(ticket_id)

    def create_and_send_ticket(self, ticket_id):
        if self._request_create_pdf(ticket_id):
            ticket_created = self._create_ticket_pdf(ticket_id)
            if ticket_created:
                self._send_ticket(ticket_id)

    @transaction.atomic()
    def _create_ticket_item(self, ticket_id, ticket_request, price):
        ticket = Ticket(
            id=ticket_id,
            email=ticket_request.email,
            movieDate_id=ticket_request.movieDateId,
            nrOfSeats=ticket_request.nrOfSeats,
            status=TICKET_STATUS_CREATED,
            ticketRequestData=JsonSerializer().serialize(ticket_request),
            price=price)
        ticket.save()

    @transaction.atomic()
    def _open_ticket_for_payment(self, ticket_id, payment_id, payment_url, payment_status):
        Ticket.objects.filter(id=ticket_id).update(
            paymentId=payment_id,
            paymentUrl=payment_url,
            status=TICKET_STATUS_OPEN
        )
        TicketStatus.objects.create(ticket_id=ticket_id, status=payment_status)

    @transaction.atomic()
    def _open_ticket_for_mail_confirmation(self, ticket_id,mail_confirmation_id ):
        Ticket.objects.filter(id=ticket_id).update(
            mailConfirmationId=mail_confirmation_id,
            status=TICKET_STATUS_OPEN
        )
        TicketStatus.objects.create(ticket_id=ticket_id, status=EMAIL_STATUS_VERIFICATION_MAIL)

    def request_ticket(self, ticket_request):
        from tickets.model import TicketResponse
        price_availability = self.get_price_availability(ticket_request)

        movie_date = Moviedate.objects.get(id=ticket_request.movieDateId)
        description = get_ticket_description(movie_date)

        ticket_id = None
        redirect_url = None
        verification_by = None
        if price_availability.available:

            price = price_availability.price
            no_payment = price_availability.noPayment
            ticket_id = str(uuid.uuid4())
            if no_payment:
                self._create_ticket_item(ticket_id, ticket_request, price)
                mail_confirmation_id = self._create_and_send_confirmation_mail(ticket_request.email)
                self._open_ticket_for_mail_confirmation(ticket_id, mail_confirmation_id)
                verification_by = "email"
            else:
                self._create_ticket_item(ticket_id, ticket_request, price)
                payment_id, payment_url, payment_status = self._create_payment(ticket_id, price, description)
                self._open_ticket_for_payment(ticket_id, payment_id, payment_url, payment_status)
                redirect_url = payment_url
                verification_by = "payment"

        return TicketResponse(
            ticketId=ticket_id,
            available=price_availability.available,
            redirectUrl=redirect_url,
            verificationBy=verification_by
        )

    def get_ticket_data(self, ticket_id):
        from tickets.model import TicketPrintData
        ticket = Ticket.objects.get(id=ticket_id)
        if ticket.status == TICKET_STATUS_ACCEPTED:
            return TicketPrintData(
                code=ticket.code,
                ticketNumber=ticket.referenceNumber,
                seatType= ticket.get_seat_type_str(),
                paymentType=ticket.get_ticket_types_str(),
                movieDateId=ticket.movieDate.id,
                moviedate=get_tz_aware_date(ticket.movieDate.date),
                movieTitle=ticket.movieDate.page.title,
                qrCode=ticket.code
            )
        else:
            raise Exception("Ticket has no accepted status")


ticket_service = TicketService()