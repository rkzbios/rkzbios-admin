from django.contrib import admin

from tickets.models import Ticket, TicketStatus


class TicketStatusInline(admin.TabularInline):
    model = TicketStatus


class TicketAdmin(admin.ModelAdmin):
    search_fields = ['email', 'code', ]
    list_display = ('createdAt', 'email', 'status', 'referenceNumber', 'code', 'nrOfSeats',)
    inlines = [
        TicketStatusInline,
    ]


admin.site.register(Ticket, TicketAdmin)

