from rest_framework import serializers
from django.contrib.auth import get_user_model
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from dj_rest_auth.serializers import LoginSerializer

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture']

class CustomRegisterSerializer(RegisterSerializer):
    username = serializers.CharField(required=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'username',
            'profile_picture',
            'password1',
            'password2',
        )

    def validate(self, data):
        return data

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data.update({
            'username': self.validated_data.get('username', ''),
            'profile_picture': self.validated_data.get('profile_picture', None),
        })
        return data


class CustomLoginSerializer(LoginSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'password')
