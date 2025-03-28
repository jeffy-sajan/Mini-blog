# Generated by Django 4.2.18 on 2025-03-22 02:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0004_alter_post_title_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, help_text='Tell us about yourself', max_length=500)),
                ('location', models.CharField(blank=True, max_length=100)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('website', models.URLField(blank=True)),
                ('interests', models.CharField(blank=True, help_text='Your interests (comma separated)', max_length=200)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
