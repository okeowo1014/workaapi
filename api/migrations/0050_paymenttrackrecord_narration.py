# Generated by Django 4.0.2 on 2022-04-21 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0049_jobspost_refusal_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymenttrackrecord',
            name='narration',
            field=models.CharField(default='Account Upgrade', max_length=255),
            preserve_default=False,
        ),
    ]
