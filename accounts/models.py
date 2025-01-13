# accounts/models.py
import string
import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    sponsor_code = models.CharField(max_length=12, unique=True, blank=True)
    wallet_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    is_paid = models.BooleanField(default=False)
    telegram_group_joined = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.sponsor_code:
            # Générer un code de parrainage aléatoire
            chars = string.ascii_uppercase + string.digits
            while True:
                code = ''.join(random.choices(chars, k=12))
                if not User.objects.filter(sponsor_code=code).exists():
                    self.sponsor_code = code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} - {self.sponsor_code}"

class Sponsorship(models.Model):
    sponsor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sponsorships_given'
    )
    sponsored_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sponsored_by'
    )
    date_sponsored = models.DateTimeField(auto_now_add=True)
    commission_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=40.00
    )
    indirect_commission_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00
    )

    class Meta:
        unique_together = ['sponsor', 'sponsored_user']

    def __str__(self):
        return f"{self.sponsor.username} parraine {self.sponsored_user.username}"
