from django.db import models
from django.contrib.auth.models import User
from .storages import OverwriteStorage
from django.db.models import Min

def offer_picture_path(instance, filename):
    # File uploaded to MEDIA_ROOT/profile_pictures/user_<id>/<filename>
    ext = filename.split('.')[-1].lower()
    if filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')):
        return f'offers/offer_{instance.user.id}/logo.{ext}' # image name is unique / always the same (logo)


class Offer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    description = models.TextField()
    image = models.ImageField(upload_to=offer_picture_path, blank=True, null=True, storage=OverwriteStorage())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OfferDetail(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='details')
    title = models.CharField(max_length= 150)
    revisions = models.PositiveIntegerField(default=0)
    delivery_time_in_days = models.PositiveIntegerField(default=0)
    offer_type = models.CharField(max_length=10, choices=[
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list, blank=True)


    class Meta:
        #no duplicates for offer_type
        constraints = [
            models.UniqueConstraint(
                fields=['offer', 'offer_type'],
                name='unique_offer_type_per_offer'
            )
        ]

