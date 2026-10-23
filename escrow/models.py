import uuid
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True)
    neighborhood = models.CharField(max_length=100, default='Juja Gate A')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.neighborhood}"

class ItemListing(models.Model):
    seller = models.ForeignKey(User, on_development=models.CASCADE, related_name='listings') if hasattr(models, 'on_development') else models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)
    neighborhood = models.CharField(max_length=100)
    
    # Flexible Image support: supports direct file uploads or external image URLs / camera snaps
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)
    whatsapp_number = models.CharField(max_length=15, blank=False, null=False)
    description = models.CharField(max_length=250, blank=False, null=False, help_text="Brief 1-sentence description.")
    
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - KES {self.price}"

class EscrowTransaction(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('LOCKED', 'Funds Locked in Vault'),
        ('COMPLETED', 'Completed & Released'),
        ('DISPUTED', 'Disputed'),
    ]

    # Unique identifier used for the public share link
    deal_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Parties involved
    seller = models.ForeignKey(User, related_name='sales', on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, related_name='purchases', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Deal details
    item_title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    seller_phone = models.CharField(max_length=15)
    buyer_phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Daraja Tracking Metadata
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Status tracker
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Timestamps for audit logs
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Deal {self.deal_token} - {self.item_title} ({self.status})"