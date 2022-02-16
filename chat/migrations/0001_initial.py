# Generated by Django 3.2.8 on 2021-12-23 18:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatChannels',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_dp', models.URLField()),
                ('chat_type', models.CharField(choices=[['normal', 'normal'], ['no_reply', 'no_reply'], ['auto', 'auto']], max_length=8)),
                ('chat_uid', models.CharField(max_length=16, unique=True)),
                ('name', models.CharField(max_length=225)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('group', models.ManyToManyField(related_name='chat_group', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_sender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('message_type', models.CharField(choices=[['text', 'text'], ['interview', 'interview'], ['auto', 'auto']], max_length=10)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_channel', to='chat.chatchannels')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_sender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
