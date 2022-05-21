# Generated by Django 4.0.2 on 2022-04-21 12:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0006_remove_employmentrequest_interview_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='interviews',
            name='refusal_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='interviews',
            name='refusal_note',
            field=models.TextField(default='Not refused'),
        ),
    ]