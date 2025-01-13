# accounts/serializers.py
from rest_framework import serializers
from .models import User, Sponsorship


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone_number', 'sponsor_code',
                  'wallet_balance', 'is_paid', 'telegram_group_joined')
        read_only_fields = ('wallet_balance', 'sponsor_code', 'is_paid',
                            'telegram_group_joined')


class UserRegistrationSerializer(serializers.ModelSerializer):
    sponsor_code_input = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'password',
                  'sponsor_code_input')

    def validate_sponsor_code_input(self, value):
        if not User.objects.filter(sponsor_code=value).exists():
            raise serializers.ValidationError("Code de parrainage invalide")
        return value

    def create(self, validated_data):
        sponsor_code = validated_data.pop('sponsor_code_input')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Créer la relation de parrainage
        sponsor = User.objects.get(sponsor_code=sponsor_code)
        Sponsorship.objects.create(sponsor=sponsor, sponsored_user=user)

        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})