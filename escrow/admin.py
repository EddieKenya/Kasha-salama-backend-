
from django.contrib import admin
from .models import UserProfile, ItemListing, EscrowTransaction

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'neighborhood', 'is_verified', 'created_at')
    search_fields = ('user__username', 'phone_number', 'neighborhood')

@admin.register(ItemListing)
class ItemListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'price', 'category', 'neighborhood', 'is_sold', 'created_at')
    list_filter = ('category', 'neighborhood', 'is_sold')
    search_fields = ('title', 'description', 'seller__username')

@admin.register(EscrowTransaction)
class EscrowTransactionAdmin(admin.ModelAdmin):
    list_display = ('deal_token', 'item_title', 'seller', 'buyer', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('item_title', 'deal_token', 'seller__username', 'buyer__username', 'mpesa_receipt_number')