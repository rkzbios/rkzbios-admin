from django.contrib import admin

from jimbo_mail.models import MailSender, MailServerConnection, MailQueue
from jimbo_mail.models import BouncedEmailAddress



class MailQueueAdmin(admin.ModelAdmin):
    search_fields = ['status',]
    list_display = ('sentAt', 'status')


class BouncedEmailAddressAdmin(admin.ModelAdmin):
    ordering = ['email',]
    search_fields = ['email',]
    list_display = ('email', 'isProcessed')
    list_filter = ('isProcessed',)

admin.site.register(MailServerConnection)
admin.site.register(MailSender)
# admin.site.register(BouncedEmailAddress, BouncedEmailAddressAdmin)
admin.site.register(MailQueue, MailQueueAdmin)

