from django.db import models

from app_auth.models import UserProfile
from django.contrib.auth.models import User

class Review(models.Model):
    business_user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="reviews",
        limit_choices_to = {'type' : 'business'}
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="written_reviews",
        limit_choices_to={'type':'customer'}
    )
    rating = models.PositiveSmallIntegerField(
        choices= [
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5)]
        )
    description = models.TextField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
