from django.contrib import admin

from django.conf import settings

from users.models import User


class UserAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
