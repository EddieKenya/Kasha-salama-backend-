from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed

class JWTCookieAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # PRINT ALL INCOMING COOKIES AND HEADERS TO THE TERMINAL
        print("--- DEBUG AUTH ---")
        print("COOKIES RECEIVED:", request.COOKIES)
        print("AUTHORIZATION HEADER:", request.headers.get('Authorization'))
        
        raw_token = request.COOKIES.get('access_token')

        if raw_token is None:
            header = self.get_header(request)
            if header is not None:
                raw_token = self.get_raw_token(header)

        if raw_token is None:
            print("AUTH RESULT: No token found in cookies or headers!")
            return None

        if isinstance(raw_token, str):
            raw_token = raw_token.strip('"\'')

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            print(f"AUTH SUCCESS: Authenticated as user -> {user}")
            return user, validated_token
        except (InvalidToken, AuthenticationFailed) as e:
            print(f"AUTH FAILED: Token invalid or expired -> {e}")
            return None