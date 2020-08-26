from django.urls import path

from tickets.views import export_movie_date_ticket_codes


urlpatterns = [
    path('export-tickets/<int:movie_date_id>/', export_movie_date_ticket_codes,name='export-movie-date-ticket-codes')
]