from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.urls import path
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

# Custom UserAdmin
class CustomUserAdmin(DefaultUserAdmin):

    # Add a custom button column
    list_display = DefaultUserAdmin.list_display + ('delete_user_link',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('delete-user/<int:user_id>/', self.admin_site.admin_view(self.delete_user), name='custom_delete_user'),
        ]
        return custom_urls + urls

    def delete_user_link(self, obj):
        return f'<a class="button" href="/admin/accounts/customuser/delete-user/{obj.id}/">Delete</a>'
    delete_user_link.allow_tags = True
    delete_user_link.short_description = 'Delete User'

    def delete_user(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" deleted successfully.')
        return redirect('/admin/auth/user/')

# Unregister default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
