from django.contrib import admin

from tickets.models import Ticket


class TicketAdmin(admin.ModelAdmin):
    search_fields = ['email', 'code', ]
    list_display = ('createdAt', 'email', 'status', 'referenceNumber', 'code', 'nrOfSeats',)


admin.site.register(Ticket, TicketAdmin)

