# Generated by Django 4.0.2 on 2022-02-14 13:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('chat', '0002_alter_chatchannels_group_alter_chatchannels_sender_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DMChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chatid', models.CharField(max_length=255)),
                ('sender', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('seenby', models.TextField(null=True)),
            ],
        ),
    ]
