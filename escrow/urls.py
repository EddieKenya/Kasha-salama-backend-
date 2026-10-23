from django.urls import path
from .views import (
    RegisterView,
    LoginView,                 # Custom login view that sets the HttpOnly cookie
    LogoutView,
    CookieTokenRefreshView,    # Custom refresh view that reads the HttpOnly cookie
    GoogleLogin,
    ItemListView,
    ItemCreateView,
    EscrowTransactionListCreateView,
    EscrowTransactionDetailView,
    InitiateEscrowPaymentView,
    DarajaCallbackView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='api_register'),
    path('login/', LoginView.as_view(), name='api_login'),
    path('google/', GoogleLogin.as_view(), name='google_rest_login'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='api_logout'),
    
    # Marketplace Item Listings
    path('items/', ItemListView.as_view(), name='item_list'),
    path('items/create/', ItemCreateView.as_view(), name='item_create'),
    
    # Escrow Deals Tracker & Daraja Payment Workflows
    path('escrow/', EscrowTransactionListCreateView.as_view(), name='escrow_list_create'),
    path('escrow/<uuid:deal_token>/', EscrowTransactionDetailView.as_view(), name='escrow_detail'),
    path('escrow/<uuid:deal_token>/pay/', InitiateEscrowPaymentView.as_view(), name='initiate_escrow_payment'),
    path('escrow/daraja-callback/', DarajaCallbackView.as_view(), name='daraja_callback'),
]  