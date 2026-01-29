from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# -----------------------------
# USER PROFILE EXTENSION
# -----------------------------
class Profile(models.Model):
    AVATAR_CHOICES = [
        ('iconA', 'Icon A'),
        ('iconB', 'Icon B'),
        ('iconC', 'Icon C'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.CharField(max_length=10, choices=AVATAR_CHOICES, default='iconA')

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


# -----------------------------
# DELETED USER LOG MODEL
# -----------------------------
class DeletedUser(models.Model):
    username = models.CharField(max_length=150)
    deleted_by = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} (deleted by {self.deleted_by})"
