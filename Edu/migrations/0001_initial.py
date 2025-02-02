# Generated by Django 5.1.1 on 2025-01-12 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Formation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('thumbnail', models.ImageField(upload_to='formations/thumbnails/')),
                ('description', models.TextField(blank=True, null=True)),
                ('duration', models.CharField(blank=True, max_length=50, null=True)),
                ('presentation_video', models.FileField(blank=True, null=True, upload_to='')),
                ('presentation_video_link', models.URLField(blank=True, null=True)),
                ('drive_link', models.URLField()),
                ('points', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-points', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Inscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_status', models.CharField(choices=[('pending', 'En attente'), ('completed', 'Complété'), ('failed', 'Échoué')], default='pending', max_length=20)),
                ('is_validated', models.BooleanField(default=False)),
                ('sponsor_code_used', models.CharField(max_length=12)),
                ('date_inscription', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_type', models.CharField(choices=[('inscription', 'Inscription'), ('telegram', 'Groupe Telegram')], max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'En attente'), ('completed', 'Complété'), ('failed', 'Échoué')], default='pending', max_length=20)),
                ('transaction_id', models.CharField(max_length=100, unique=True)),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('payment_method', models.CharField(max_length=50)),
                ('payment_details', models.JSONField(blank=True, default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='TelegramSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscription_date', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
    ]
