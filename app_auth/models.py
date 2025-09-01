from django.db import models
from django.contrib.auth.models import User
from .storages import OverwriteStorage

USER_TYPES = [
    ('business', 'Business'),
    ('customer','Customer')
]

def profile_picture_path(instance, filename):
    # File uploaded to MEDIA_ROOT/profile_pictures/user_<id>/<filename>
    ext = filename.split('.')[-1]
    return f'profile_pictures/user_{instance.user.id}/profile.{ext}' # image name is unique (profile)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    type = models.CharField(max_length=8, choices=USER_TYPES, blank=False, null=False)
    file = models.FileField(upload_to=profile_picture_path, blank=True, null=False, storage=OverwriteStorage())
    location = models.CharField(max_length = 80, blank=True)
    tel = models.CharField(max_length = 30, blank=True)
    description = models.TextField(blank=True)
    working_hours = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username