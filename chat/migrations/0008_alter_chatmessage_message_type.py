# Generated by Django 4.0.2 on 2022-02-20 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0007_alter_chatmessage_sender_alter_dmchatmessage_sender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatmessage',
            name='message_type',
            field=models.CharField(choices=[['text', 'text'], ['objective_interview', 'objective_interview'], ['theory_interview', 'theory_interview'], ['auto', 'auto']], max_length=20),
        ),
    ]