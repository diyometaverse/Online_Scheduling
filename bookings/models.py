from django.db import models
from django.contrib.auth.models import User

class Booking(models.Model):
    SERVICE_CHOICES = [
        ('portrait', 'Portrait Session'),
        ('wedding', 'Wedding Photoshoot'),
        ('product', 'Product Photography'),
        ('event', 'Event Coverage'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('disapproved', 'Disapproved'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    session_datetime = models.DateTimeField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_service_type_display()} on {self.session_datetime.strftime('%Y-%m-%d %H:%M')} ({self.get_status_display()})"
