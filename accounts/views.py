from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

User = get_user_model()

class CheckUserExistsView(APIView):
    def get(self, request):
        username = request.query_params.get('username')
        email = request.query_params.get('email')

        if username:
            user_exists = User.objects.filter(username=username).exists()
            return Response({'exists': user_exists}, status=status.HTTP_200_OK)

        if email:
            user_exists = User.objects.filter(email=email).exists()
            return Response({'exists': user_exists}, status=status.HTTP_200_OK)

        return Response({'error': 'Username or email must be provided'}, status=status.HTTP_400_BAD_REQUEST)

