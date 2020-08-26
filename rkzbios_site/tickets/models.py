import os
from datetime import date

from django.db import models

from persistent.serializer import JsonUnSerializer

from home.models import Moviedate

TICKETS_DIR = 'tickets/'


SEAT_CHOICE_SINGLE = 1
SEAT_CHOICE_DOUBLE = 2

SEAT_CHOICES = [
    (SEAT_CHOICE_SINGLE, 'OneSeat'),
    (SEAT_CHOICE_DOUBLE, 'DuoSeat'),
]

TICKET_STATUS_CREATED = 'created'
TICKET_STATUS_OPEN = 'open'
TICKET_STATUS_ACCEPTED = 'accepted'
TICKET_STATUS_REJECTED = 'rejected'

TICKET_STATUS_CHOICES = [
    (TICKET_STATUS_OPEN, 'open'),
    (TICKET_STATUS_ACCEPTED, 'accepted'),
    (TICKET_STATUS_REJECTED, 'rejected'),
]


TICKET_SEND_STATUS_NO_TICKET = 'no-ticket'
TICKET_SEND_STATUS_REQUEST_TICKET_CREATE = 'request-ticket-create'
TICKET_SEND_STATUS_TICKET_START_CREATED = 'ticket-create-start'
TICKET_SEND_STATUS_TICKET_CREATED = 'ticket-created'
TICKET_SEND_STATUS_REQUEST_TICKET_SEND = 'request-ticket-send'
TICKET_SEND_STATUS_TICKET_SENT = 'ticket-sent'

TICKET_SEND_STATUS_CHOICES = [
    (TICKET_SEND_STATUS_NO_TICKET, 'no-ticket'),
    (TICKET_SEND_STATUS_REQUEST_TICKET_CREATE, 'request-ticket-create'),
    (TICKET_SEND_STATUS_TICKET_START_CREATED,'ticket-create-start'),
    (TICKET_SEND_STATUS_TICKET_CREATED, 'ticket-created'),
    (TICKET_SEND_STATUS_REQUEST_TICKET_SEND, 'request-ticket-send'),
    (TICKET_SEND_STATUS_TICKET_SENT, 'ticket-sent'),

]

PAYMENT_STATUS_OPEN = 'open'  # The payment has been created, but nothing else has happened yet.
PAYMENT_STATUS_CANCELED = 'canceled' # Your customer has canceled the payment. This is a definitive status.
PAYMENT_STATUS_PENDING = 'pending' # This is a temporary status that can occur when the actual payment process has been started, but it’s not complete yet.

PAYMENT_STATUS_AUTHORIZED = 'authorized' #
PAYMENT_STATUS_EXPIRED = 'expired' #
PAYMENT_STATUS_FAILED = 'failed' #
PAYMENT_STATUS_PAYED = 'payed' #
PAYMENT_STATUS_REFUNDED = 'refunded'

EMAIL_STATUS_VERIFICATION_MAIL = 'sended-vmail'
EMAIL_STATUS_EMAIL_VERIFIED = 'email-verified'

STATUS_CHOICES = [
    (PAYMENT_STATUS_OPEN, 'open'),
    (PAYMENT_STATUS_CANCELED, 'canceled'),
    (PAYMENT_STATUS_PENDING, 'pending'),
    (PAYMENT_STATUS_AUTHORIZED, 'authorized'),
    (PAYMENT_STATUS_EXPIRED, 'expired'),
    (PAYMENT_STATUS_FAILED, 'failed'),
    (PAYMENT_STATUS_PAYED, 'payed'),
    (PAYMENT_STATUS_REFUNDED, 'refunded'),
    (EMAIL_STATUS_VERIFICATION_MAIL,'sended-vmail'),
    (EMAIL_STATUS_EMAIL_VERIFIED,'email-verified'),
]


TICKET_TYPE_NORMAL = 'normal'
TICKET_TYPE_STRIPPENKAART = 'strippenkaart'
TICKET_TYPE_BIOSCOOPPAS =  'bioscooppas'
TICKET_TYPE_STADJESPAS = 'stadjespas'
TICKET_TYPE_STUDENENTPAS ='studentenpas'
TICKET_TYPE_RKZMEMBER = 'rkzmember'

TICKET_TYPES = [
    (TICKET_TYPE_NORMAL, 'normal'),
    (TICKET_TYPE_STRIPPENKAART, 'strippenkaart'),
    (TICKET_TYPE_BIOSCOOPPAS,  'bioscooppas'),
    (TICKET_TYPE_STADJESPAS, 'stadjespas'),
    (TICKET_TYPE_STUDENENTPAS, 'studentenpas'),
    (TICKET_TYPE_RKZMEMBER, 'rkzmember'),
]

def generate_ticket_filename(instance, filename):
    """Get upload_to path specific to this upload."""
    year = date.today().year
    month = date.today().month
    path = os.path.join("tickets", "%s" % year, "%s" % month)
    return os.path.join(TICKETS_DIR, path, filename)


# class TicketMovieDateStatus(models.Model):
#     movieDate = models.ForeignKey(Moviedate, on_delete=models.SET_NULL, null=True)
#     nrAvailable = models.IntegerField()

class Ticket(models.Model):
    class Meta:
        permissions = [('list_ticket_codes', 'Can list ticket codes')]

    id = models.CharField(max_length=36, primary_key=True, editable=False)
    movieDate = models.ForeignKey(Moviedate, on_delete=models.SET_NULL, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    nrOfSeats = models.IntegerField(choices=SEAT_CHOICES)
    email = models.EmailField()
    status = models.CharField(choices=TICKET_STATUS_CHOICES, max_length=24)
    ticketSendStatus = models.CharField(
        choices=TICKET_SEND_STATUS_CHOICES,
        max_length=24,
        default=TICKET_SEND_STATUS_NO_TICKET)
    lastStatusUpdate = models.DateTimeField(auto_now=True)
    paymentUrl = models.CharField(max_length=256, null=True, blank=True)
    paymentId = models.CharField(max_length=256, null=True, blank=True)
    ticketPdf = models.FileField(upload_to=generate_ticket_filename, max_length=200, null=True, blank=True)
    ticketRequestData = models.TextField() # Stored as json list
    price = models.DecimalField(max_digits=8, decimal_places=2)
    referenceNumber = models.IntegerField(null=True, blank=True)  # Simple number on accepted ticket
    code = models.CharField(max_length=6, null=True, blank=True)
    mailConfirmationId = models.CharField(max_length=36, null=True,blank=True, unique=True)

    def get_ticket_request(self):
        from tickets.model import TicketRequest
        ticket_request = JsonUnSerializer().unserialize(self.ticketRequestData, clazz=TicketRequest)
        return ticket_request

    def get_tickets_types(self):
        return self.get_ticket_request().paymentTypes

    def get_ticket_types_str(self):
        ticket_types = self.get_tickets_types()
        return "|".join(ticket_types)

    def get_seat_type_str(self):
        if self.nrOfSeats == 1:
            return "OneSeat"
        if self.nrOfSeats == 2:
            return "DuoTeat"
        return "%s Seats" % self.nrOfSeats


class TicketStatus(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, max_length=24)
