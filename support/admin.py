from django.contrib import admin
from .models import SupportTicket


# @admin.register(SupportTicket)
# class ModelNameAdmin(admin.ModelAdmin):
#     list_display = "__all__"

admin.site.register(SupportTicket)
