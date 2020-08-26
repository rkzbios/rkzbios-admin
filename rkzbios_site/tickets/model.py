from persistent.models import Model
from persistent import fields, related


class TicketRequest(Model):
    movieDateId = fields.IntegerField()
    terms = fields.BooleanField(default=False)
    email = fields.CharField()
    emailVerification = fields.CharField()
    paymentTypes = related.ListOf(str)
    nrOfSeats = fields.IntegerField()


class TicketStatus(Model):
    ticketRequest = related.OneOf(TicketRequest)
    status = fields.CharField()
    ticketSendStatus = fields.CharField()
    movieTitle = fields.CharField()
    movieDate = fields.DateTimeField()


class TicketResponse(Model):
    ticketId = fields.CharField(null=True, blank=True)
    available = fields.BooleanField()
    redirectUrl = fields.CharField(max_length=1024, null=True, blank=True)
    verificationBy = fields.CharField(max_length=1024, null=True, blank=True) # payment, email


class PriceAvailability(Model):
    available = fields.BooleanField()
    price = fields.DecimalField(decimal_places=2)
    noPayment = fields.BooleanField()


class MailConfirmation(Model):
    confirmationId = fields.CharField()
    movieTitle = fields.CharField()
    movieDate = fields.DateTimeField()
    confirmationStatus = fields.CharField()   # open, time_out, confirmed


class TicketAvailability(Model):
    movieDateId = fields.IntegerField()
    movieTitle = fields.CharField()
    movieDate = fields.DateTimeField()
    isPassed = fields.BooleanField()
    nrOfSingleSeatsTicketsAvailable = fields.IntegerField()
    nrOfDoubleSeatsTicketsAvailable = fields.IntegerField()


class TicketPrintData(Model):
    ticketNumber = fields.IntegerField()
    ticketRequest = related.OneOf(TicketRequest)
    movieDate = fields.DateTimeField()
    movieTitle = fields.CharField()
    code = fields.CharField()
    qrCode = fields.CharField()
