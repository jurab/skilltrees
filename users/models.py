from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with subscription and progress tracking."""

    # Subscription
    is_subscribed = models.BooleanField(default=False)
    subscription_expires = models.DateTimeField(null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True)

    # Progress tracking - last position for "continue" feature
    last_node = models.ForeignKey(
        'skills.Node',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='last_viewers',
    )
    last_video_position = models.PositiveIntegerField(default=0, help_text='Position in seconds')

    # Completed skills (global, applies across all trees)
    completed_skills = models.ManyToManyField(
        'skills.Skill',
        blank=True,
        related_name='completed_by',
    )

    # Ignored skills (user never wants to see these)
    ignored_skills = models.ManyToManyField(
        'skills.Skill',
        blank=True,
        related_name='ignored_by',
    )
