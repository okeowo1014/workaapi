# Generated by Django 4.0.2 on 2022-04-21 12:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0048_rename_transanction_planupgraderecord_transaction_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobspost',
            name='refusal_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
