from rest_framework import serializers
from .models import ItemListing, EscrowTransaction, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'phone_number', 'neighborhood', 'is_verified', 'created_at']
        read_only_fields = ['id', 'is_verified', 'created_at']

class ItemListingSerializer(serializers.ModelSerializer):
    seller_username = serializers.ReadOnlyField(source='seller.username')

    class Meta:
        model = ItemListing
        fields = [
            'id', 'seller', 'seller_username', 'title', 'description', 
            'price', 'category', 'neighborhood', 'whatsapp_number',
            'image', 'is_sold', 'created_at'
        ]
        read_only_fields = ['id', 'seller', 'seller_username', 'created_at', 'is_sold']

class EscrowTransactionSerializer(serializers.ModelSerializer):
    seller_username = serializers.ReadOnlyField(source='seller.username')
    buyer_username = serializers.ReadOnlyField(source='buyer.username')

    class Meta:
        model = EscrowTransaction
        fields = ['id', 'deal_token', 'seller', 'seller_username', 'buyer', 'buyer_username', 'item_title', 'amount', 'seller_phone', 'buyer_phone', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'deal_token', 'seller', 'seller_username', 'buyer', 'buyer_username', 'status', 'created_at', 'updated_at']