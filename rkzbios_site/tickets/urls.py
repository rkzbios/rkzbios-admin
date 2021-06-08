from django.urls import path

from tickets.views import get_ticket_print_data, get_available_tickets, mollie_callback, get_ticket_status, \
    get_price_availability, create_ticket_request, ticket_mail_confirmation, export_movie_date_ticket_codes


urlpatterns = [
    path('ticket-confirmation/<str:confirmation_id>/', ticket_mail_confirmation),
    path('status/<str:ticket_id>/', get_ticket_status),
    path('price-availability/', get_price_availability),
    path('ticket-request/', create_ticket_request),
    path('availability/<int:movie_date_id>/', get_available_tickets),
    path('mollie-callback/<str:ticket_id>/', mollie_callback),
    path('ticket-print-data/<str:ticket_id>/', get_ticket_print_data),
    path('export-tickets/<int:movie_date_id>/', export_movie_date_ticket_codes, name='export-movie-date-ticket-codes')

]