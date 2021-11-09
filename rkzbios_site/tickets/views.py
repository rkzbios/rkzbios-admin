import csv

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from persistent.serializer import JsonSerializer, PythonDeserializer

from rest_framework.decorators import api_view
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser

from tickets.service import ticket_service

ACCESS_TOKEN_PARAM_NAME = "accessToken"


class PersistentJsonResponse(HttpResponse):
    """
    An HTTP response class that consumes data to be serialized to JSON.

    :param data: Data to be dumped into json. By default only ``dict`` objects
      are allowed to be passed due to a security flaw before EcmaScript 5. See
      the ``safe`` parameter for more information.
    :param encoder: Should be a json encoder class. Defaults to
      ``django.core.serializers.json.DjangoJSONEncoder``.
    :param safe: Controls if only ``dict`` objects may be serialized. Defaults
      to ``True``.
    :param json_dumps_params: A dictionary of kwargs passed to json.dumps().
    """

    def __init__(self, data, **kwargs):
        kwargs.setdefault('content_type', 'application/json')
        data = JsonSerializer().serialize(data)
        super().__init__(content=data, **kwargs)
        self['Cache-Control'] = 'no-cache'


def get_ticket_print_data(request, ticket_id):

    if request.method == 'GET':
        jwt_raw_access_token = request.GET.get(ACCESS_TOKEN_PARAM_NAME, None)
        ticket_print_data = ticket_service.get_ticket_print_data(ticket_id)
        response = PersistentJsonResponse(ticket_print_data)
        return response


def get_available_tickets(request, movie_date_id):
    if request.method == 'GET':
        availability_data = ticket_service.get_availability(movie_date_id)
        response = PersistentJsonResponse(availability_data)
        return response


def mollie_callback(request, ticket_id):
    if request.method == 'POST':
        ticket_service.sync_payment_status(ticket_id)
        return HttpResponse("ok")


def get_ticket_status(request, ticket_id):
    if request.method == 'GET':
        ticket_status = ticket_service.get_ticket_status(ticket_id)
        response = PersistentJsonResponse(ticket_status)
        return response

@csrf_exempt
@api_view(['POST'])
@parser_classes([JSONParser])
def get_price_availability(request):
    from tickets.model import TicketRequest
    ticket_request = PythonDeserializer().unserialize(request.data, TicketRequest)
    price_availability = ticket_service.get_price_availability(ticket_request)
    response = PersistentJsonResponse(price_availability)
    return response

@csrf_exempt
@api_view(['POST'])
@parser_classes([JSONParser])
def create_ticket_request(request):
    from tickets.model import TicketRequest
    # if request.method == 'POST':
    ticket_request = PythonDeserializer().unserialize(request.data, TicketRequest)
    ticket_response = ticket_service.request_ticket(ticket_request)
    response = PersistentJsonResponse(ticket_response)
    return response


@csrf_exempt
@api_view(['POST','GET'])
@parser_classes([JSONParser])
def ticket_mail_confirmation(request, confirmation_id):
    if request.method == "POST":
        mail_confirmation = ticket_service.mail_ticket_confirmation(confirmation_id, do_confirm=True)
    else:
        mail_confirmation = ticket_service.mail_ticket_confirmation(confirmation_id)
    response = PersistentJsonResponse(mail_confirmation)
    return response


def obfuscate_email_address(email_address):
    try:
        local_part, domain_name = email_address.split('@')
        local_parts = local_part.split('.')
        for i, part in enumerate(local_parts):
            replaced_email = "".join("*" for _char in part[1:-1])
            last_char = part[-1] if len(part) > 2 else "*"
            local_parts[i] = "".join((part[0], replaced_email, last_char))
        replace_local_parts = ".".join(local_parts)
        return replace_local_parts + "@" + domain_name
    except Exception as _e:
        return ""

@login_required
def export_movie_date_ticket_codes(request, movie_date_id):
    from tickets.models import Ticket, TICKET_STATUS_ACCEPTED

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ticket-codes.csv"'

    accepted_tickets = Ticket.objects.filter(movieDate_id=movie_date_id, status=TICKET_STATUS_ACCEPTED).order_by("code")

    writer = csv.writer(response)

    for accepted_ticket in accepted_tickets:
        ticket_request = accepted_ticket.get_ticket_request()
        writer.writerow([accepted_ticket.code,
                         accepted_ticket.get_seat_type_str(),
                         accepted_ticket.get_ticket_types_str(),
                         accepted_ticket.referenceNumber,
                         obfuscate_email_address(ticket_request.email)
                         ])
    return response
