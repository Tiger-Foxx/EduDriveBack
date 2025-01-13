# Edu/models.py
from django.db import models
from accounts.models import User

# Edu/models.py
import os
from PIL import Image
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import subprocess
from django.conf import settings
from django.db import models


class Formation(models.Model):
    title = models.CharField(max_length=200)
    thumbnail = models.ImageField(upload_to='formations/thumbnails/')
    description = models.TextField(blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True, null=True)
    presentation_video = models.FileField(
        upload_to='formations/videos/',
        blank=True,
        null=True
    )
    presentation_video_link = models.URLField(blank=True, null=True)
    drive_link = models.URLField()
    points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def compress_image(self, image):
        img = Image.open(image)

        # Redimensionner si l'image est plus grande que 800x500
        if img.height > 500 or img.width > 800:
            output_size = (800, 500)
            img.thumbnail(output_size, Image.LANCZOS)

        # Créer un fichier temporaire
        temp_thumb = NamedTemporaryFile(delete=True)

        # Sauvegarder avec compression
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        img.save(temp_thumb, format='JPEG', quality=85, optimize=True)

        temp_thumb.flush()
        return File(temp_thumb)

    def compress_video(self, video):
        # Créer les chemins pour le fichier compressé
        filename = os.path.splitext(os.path.basename(video.name))[0]
        output_path = os.path.join(settings.MEDIA_ROOT, 'formations/videos',
                                   f'{filename}_compressed.mp4')

        # Commande ffmpeg pour compression vidéo
        command = [
            'ffmpeg', '-i', video.temporary_file_path(),
            '-vcodec', 'libx264',
            '-crf', '28',  # Facteur de compression (18-28 est bon)
            '-preset', 'medium',  # Balance entre vitesse et compression
            '-acodec', 'aac',
            '-strict', 'experimental',
            output_path
        ]

        try:
            subprocess.run(command, check=True)
            return File(open(output_path, 'rb'))
        except subprocess.CalledProcessError:
            return video

    def save(self, *args, **kwargs):
        # Compression de l'image
        if self.thumbnail:
            compressed_image = self.compress_image(self.thumbnail)
            self.thumbnail = compressed_image

        # Compression de la vidéo
        if self.presentation_video and hasattr(self.presentation_video, 'temporary_file_path'):
            compressed_video = self.compress_video(self.presentation_video)
            self.presentation_video = compressed_video

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-points', '-created_at']



class Inscription(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
    ]

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='inscription'
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    is_validated = models.BooleanField(default=False)
    sponsor_code_used = models.CharField(max_length=12)
    date_inscription = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inscription de {self.user.username}"

class Payment(models.Model):
    PAYMENT_TYPES = [
        ('inscription', 'Inscription'),
        ('telegram', 'Groupe Telegram'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='payments'
    )
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)
    payment_details = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Paiement de {self.user.username} - {self.payment_type}"

class TelegramSubscription(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='telegram_subscription'
    )
    subscription_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    payment = models.OneToOneField(
        Payment, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='telegram_subscription'
    )

    def __str__(self):
        return f"Abonnement Telegram de {self.user.username}"





## ANCIEN MODEL DE FORMATIONS A CONCERVER AU CAS OU


# class Formation(models.Model):
#     title = models.CharField(max_length=200)
#     thumbnail = models.ImageField(upload_to='formations/thumbnails/')
#     description = models.TextField(blank=True, null=True)
#     duration = models.CharField(max_length=50, blank=True, null=True)
#     presentation_video = models.FileField(blank=True, null=True,upload_to='formations/videos/')
#     presentation_video_link = models.URLField(blank=True, null=True)
#     drive_link = models.URLField()
#     points = models.IntegerField(default=0)  # Pour le classement des formations populaires
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return self.title
#
#     class Meta:
#         ordering = ['-points', '-created_at']
