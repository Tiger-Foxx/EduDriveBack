# Edu/models.py
import random
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

import os
import random
import subprocess
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.conf import settings
from django.db import models
from django.core.files.base import ContentFile
import tempfile

class Formation(models.Model):
    title = models.CharField(max_length=200)
    thumbnail = models.ImageField(upload_to='formations/thumbnails/')
    description = models.TextField(blank=True, null=True)
    duration = models.IntegerField(null=True, blank=True, default=6)
    presentation_video = models.FileField(
        upload_to='formations/videos/',
        blank=True,
        null=True
    )
    CATEGORY_CHOICES = [
        ('marketing', 'Marketing'),
        ('development', 'Développement Personnel'),
        ('business', 'Business'),
        ('sales', 'Ventes'),
        ('tech', 'Technologie'),
        ('other', 'Autres'),
    ]
    category = models.CharField(
        max_length=60,
        choices=CATEGORY_CHOICES,
        default='other'
    )
    presentation_video_link = models.URLField(blank=True, null=True)
    drive_link = models.URLField()
    points = models.IntegerField(default=40)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notions = models.TextField(blank=True, null=True)
    participants_number = models.IntegerField(null=True, blank=True, default=2153)
    notation = models.FloatField(null=True, blank=True, default=4.5)

    def compress_image(self, image_field):
        """Compresse une image tout en préservant son nom de fichier original"""
        try:
            # Ouvre l'image
            img = Image.open(image_field)
            
            # Convertit en RGB si nécessaire
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Redimensionne si nécessaire
            if img.height > 500 or img.width > 800:
                output_size = (800, 500)
                img.thumbnail(output_size, Image.LANCZOS)
            
            # Prépare un buffer pour l'image compressée
            output_io = BytesIO()
            
            # Sauvegarde avec compression
            img.save(output_io, format='JPEG', quality=85, optimize=True)
            
            # Prépare le nom du fichier
            original_name = os.path.splitext(image_field.name)[0]
            new_name = f"{original_name}_compressed.jpg"
            
            # Crée un nouveau fichier Django
            compressed_image = ContentFile(output_io.getvalue())
            return compressed_image, new_name
            
        except Exception as e:
            print(f"Erreur lors de la compression de l'image: {str(e)}")
            return None, None

    def compress_video(self, video_field):
        """Compresse une vidéo en utilisant ffmpeg"""
        try:
            # Crée un dossier temporaire
            with tempfile.TemporaryDirectory() as temp_dir:
                # Prépare les chemins
                input_path = os.path.join(temp_dir, 'input' + os.path.splitext(video_field.name)[1])
                output_path = os.path.join(temp_dir, 'output.mp4')
                
                # Sauvegarde le fichier d'entrée
                with open(input_path, 'wb') as f:
                    for chunk in video_field.chunks():
                        f.write(chunk)
                
                # Commande ffmpeg
                command = [
                    'ffmpeg', '-i', input_path,
                    '-vcodec', 'libx264',
                    '-crf', '28',
                    '-preset', 'medium',
                    '-acodec', 'aac',
                    '-strict', 'experimental',
                    output_path
                ]
                
                # Exécute la compression
                subprocess.run(command, check=True, capture_output=True)
                
                # Prépare le nom du fichier
                original_name = os.path.splitext(video_field.name)[0]
                new_name = f"{original_name}_compressed.mp4"
                
                # Crée un nouveau fichier Django
                with open(output_path, 'rb') as f:
                    compressed_video = ContentFile(f.read())
                    return compressed_video, new_name
                    
        except Exception as e:
            print(f"Erreur lors de la compression de la vidéo: {str(e)}")
            return None, None

    def save(self, *args, **kwargs):
        # Génère des statistiques aléatoires si c'est une nouvelle formation
        if not self.pk:  # Si c'est une nouvelle formation
            self.notation = round(random.uniform(4.0, 5.0), 1)
            self.participants_number = random.randint(2150, 3250)

        # Compression de l'image
        if self.thumbnail and hasattr(self.thumbnail, 'file'):
            compressed_image, new_name = self.compress_image(self.thumbnail)
            if compressed_image:
                self.thumbnail.save(new_name, compressed_image, save=False)

        # Compression de la vidéo
        if self.presentation_video and hasattr(self.presentation_video, 'file'):
            compressed_video, new_name = self.compress_video(self.presentation_video)
            if compressed_video:
                self.presentation_video.save(new_name, compressed_video, save=False)

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
