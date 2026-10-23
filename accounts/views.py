from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Secure isolation: Only return the currently authenticated user's details
        profile_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": getattr(user, 'phone_number', 'Linked via Item Uploads'),
            "neighborhood": getattr(user, 'neighborhood', 'Juja Gate A'),
            "trust_points": getattr(user, 'trust_points', 0),
        }
        
        return Response(profile_data, status=status.HTTP_200_OK)