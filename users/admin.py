from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'is_subscribed', 'subscription_expires', 'is_staff']
    list_filter = ['is_subscribed', 'is_staff', 'is_superuser', 'is_active']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Subscription', {
            'fields': ('is_subscribed', 'subscription_expires', 'stripe_customer_id'),
        }),
        ('Progress', {
            'fields': ('last_node', 'last_video_position', 'completed_skills'),
        }),
    )
