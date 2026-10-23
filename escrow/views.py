import base64
from datetime import datetime
import os
import requests
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenViewBase

from .models import EscrowTransaction, ItemListing
from .serializers import EscrowTransactionSerializer, ItemListingSerializer


class SecureLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        response = Response(
            {
                "message": "Login successful",
                "access_token": str(access),
                "refresh_token": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                },
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key="access_token",
            value=str(access),
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/",
            max_age=3600,
        )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/",
            max_age=3 * 24 * 60 * 60,
        )
        return response


class SecureLogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get(
            "refresh_token"
        ) or request.data.get("refresh_token")
        response = Response({"message": "Logged out successfully"})

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass

        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")
        return response


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email", "")

        if not username or not password:
            return Response(
                {"error": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            username=username, password=password, email=email
        )

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        response = Response(
            {
                "message": "User registered and logged in successfully",
                "access_token": str(access),
                "refresh_token": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                },
            },
            status=status.HTTP_201_CREATED,
        )

        response.set_cookie(
            key="access_token",
            value=str(access),
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/",
            max_age=3600,
        )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/",
            max_age=3 * 24 * 60 * 60,
        )
        return response


class CookieTokenRefreshView(TokenViewBase):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token and "refresh" not in request.data:
            request.data["refresh"] = refresh_token

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response(
                {
                    "error": "Invalid or expired refresh token",
                    "detail": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_access_token = serializer.validated_data.get("access")

        response = Response(
            {"access": new_access_token, "access_token": new_access_token},
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key="access_token",
            value=str(new_access_token),
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/",
            max_age=3600,
        )
        return response


LoginView = SecureLoginView
LogoutView = SecureLogoutView


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = "http://localhost:3000/auth/google/callback"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200 and self.user:
            refresh = RefreshToken.for_user(self.user)
            access = refresh.access_token

            response.data["access_token"] = str(access)
            response.data["refresh_token"] = str(refresh)
            response.data["user"] = {
                "id": self.user.id,
                "username": self.user.username,
                "email": self.user.email,
            }

            response.set_cookie(
                key="access_token",
                value=str(access),
                httponly=True,
                secure=False,
                samesite="Lax",
                path="/",
                max_age=3600,
            )
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=False,
                samesite="Lax",
                path="/",
                max_age=3 * 24 * 60 * 60,
            )
        return response


class ItemListView(generics.ListAPIView):
    queryset = ItemListing.objects.filter(is_sold=False).order_by("-created_at")
    serializer_class = ItemListingSerializer
    permission_classes = [permissions.AllowAny]


class ItemCreateView(generics.CreateAPIView):
    queryset = ItemListing.objects.all()
    serializer_class = ItemListingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class EscrowTransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = EscrowTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return EscrowTransaction.objects.filter(
            Q(buyer=user) | Q(seller=user)
        ).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class EscrowTransactionDetailView(generics.RetrieveUpdateAPIView):
    queryset = EscrowTransaction.objects.all()
    serializer_class = EscrowTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "deal_token"


class DarajaService:

    def __init__(self):
        self.consumer_key = str(os.getenv("DARAJA_CONSUMER_KEY", "")).strip()
        self.consumer_secret = str(os.getenv("DARAJA_CONSUMER_SECRET", "")).strip()
        self.business_short_code = str(os.getenv("DARAJA_SHORTCODE", "174379")).strip()
        self.passkey = str(
            os.getenv(
                "DARAJA_PASSKEY",
                "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919",
            )
        ).strip()
        self.base_url = str(
            os.getenv("DARAJA_BASE_URL", "https://sandbox.safaricom.co.ke")
        ).strip()

    def get_access_token(self):
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"

        print("--- DARAJA AUTH DIAGNOSTICS ---")
        print("URL:", url)
        print("KEY LENGTH:", len(self.consumer_key))
        print("SECRET LENGTH:", len(self.consumer_secret))
        print("KEY REPR:", repr(self.consumer_key))
        print("SECRET REPR:", repr(self.consumer_secret))

        response = requests.get(url, auth=(self.consumer_key, self.consumer_secret))

        print("DARAJA AUTH STATUS:", response.status_code)
        print("DARAJA AUTH RESPONSE:", response.text)

        if response.status_code == 200:
            return response.json().get("access_token")
        raise Exception(
            f"Daraja Authentication Failed ({response.status_code}): {response.text}"
        )

    def generate_password(self, timestamp):
        data_to_encode = f"{self.business_short_code}{self.passkey}{timestamp}"
        return base64.b64encode(data_to_encode.encode()).decode()

    def initiate_stk_push(self, phone_number, amount, deal_token):
        token = self.get_access_token()
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = self.generate_password(timestamp)

        formatted_phone = str(phone_number).strip()
        if formatted_phone.startswith("0"):
            formatted_phone = "254" + formatted_phone[1:]
        elif formatted_phone.startswith("+"):
            formatted_phone = formatted_phone[1:]

        payload = {
            "BusinessShortCode": self.business_short_code,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(float(amount)),
            "PartyA": formatted_phone,
            "PartyB": self.business_short_code,
            "PhoneNumber": formatted_phone,
            "CallBackURL": f"{os.getenv('BACKEND_URL', 'http://localhost:8000').strip()}/api/escrow/daraja-callback/",
            "AccountReference": f"Deal-{str(deal_token)[:8]}",
            "TransactionDesc": "KashaSalama Escrow Deposit",
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        res = requests.post(url, json=payload, headers=headers)
        print("DARAJA STK STATUS:", res.status_code)
        print("DARAJA STK RESPONSE:", res.text)
        return res


class InitiateEscrowPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, deal_token):
        try:
            deal = EscrowTransaction.objects.get(deal_token=deal_token)

            if deal.buyer and deal.buyer != request.user:
                return Response(
                    {"error": "Only the designated buyer can initiate payment."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            phone_number = request.data.get("phone_number") or getattr(
                request.user.profile, "phone_number", None
            )
            if not phone_number:
                return Response(
                    {"error": "Buyer phone number is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            daraja_service = DarajaService()
            response = daraja_service.initiate_stk_push(
                phone_number=phone_number,
                amount=deal.amount,
                deal_token=deal.deal_token,
            )

            res_data = response.json()
            if response.status_code == 200 and res_data.get("ResponseCode") == "0":
                deal.checkout_request_id = res_data.get("CheckoutRequestID")
                deal.buyer_phone = phone_number
                deal.buyer = request.user
                deal.save()
                return Response(
                    {
                        "message": "STK Push triggered successfully. Check your phone.",
                        "checkout_request_id": deal.checkout_request_id,
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"error": res_data.get("errorMessage", response.text)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except EscrowTransaction.DoesNotExist:
            return Response(
                {"error": "Escrow transaction not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DarajaCallbackView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        try:
            stk_callback = data.get("Body", {}).get("stkCallback", {})
            checkout_request_id = stk_callback.get("CheckoutRequestID")
            result_code = stk_callback.get("ResultCode")

            transaction = EscrowTransaction.objects.get(
                checkout_request_id=checkout_request_id
            )

            if result_code == 0:
                callback_metadata = (
                    stk_callback.get("CallbackMetadata", {}).get("Item", [])
                )
                receipt_number = next(
                    (
                        item["Value"]
                        for item in callback_metadata
                        if item["Name"] == "MpesaReceiptNumber"
                    ),
                    None,
                )

                transaction.status = "LOCKED"
                transaction.mpesa_receipt_number = receipt_number
                transaction.save()
            else:
                transaction.status = "PENDING"
                transaction.save()

        except EscrowTransaction.DoesNotExist:
            pass
        except Exception as e:
            print(f"Daraja callback processing error: {str(e)}")

        return Response({"ResultCode": 0, "ResultDesc": "Accepted"})