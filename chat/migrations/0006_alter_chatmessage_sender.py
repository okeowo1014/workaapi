# Generated by Django 4.0.2 on 2022-02-17 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_alter_dmchatmessage_sender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatmessage',
            name='sender',
            field=models.CharField(default='', max_length=255),
        ),
    ]