from django.contrib import admin
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html

from home.models import Moviedate


class MoviedateAdmin(admin.ModelAdmin):
    list_display = ('page', 'date','export_ticket_codes_link')
    ordering = ["-date"]

    def export_ticket_codes_link(self, obj):
        url = (
                reverse("export-movie-date-ticket-codes", args=(obj.id,))

        )
        return format_html('<a href="{}"> TicketCodes</a>', url)


#
# class MailQueueAdmin(admin.ModelAdmin):
#     search_fields = ['status',]
#     list_display = ('sentAt', 'status')
#
#
# class BouncedEmailAddressAdmin(admin.ModelAdmin):
#     ordering = ['email',]
#     search_fields = ['email',]
#     list_display = ('email', 'isProcessed')
#     list_filter = ('isProcessed',)

admin.site.register(Moviedate, MoviedateAdmin)
