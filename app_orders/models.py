from django.db import models
from django.contrib.auth.models import User

from app_offers.models import OfferDetail

class Order(models.Model):
    customer_user = models.ForeignKey(User, on_delete=models.CASCADE)
    offer_detail = models.ForeignKey(OfferDetail, on_delete=models.CASCADE)
    status = models.CharField(max_length=12, default='in_progress', choices=[
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)