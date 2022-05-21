# Generated by Django 4.0.2 on 2022-04-21 11:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0047_remove_staff_other_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='planupgraderecord',
            old_name='transanction',
            new_name='transaction',
        ),
        migrations.AddField(
            model_name='jobspost',
            name='refusal_note',
            field=models.TextField(default='Not refused'),
        ),
        migrations.AlterField(
            model_name='employer',
            name='plan',
            field=models.ForeignKey(default='20220322', on_delete=django.db.models.deletion.CASCADE, related_name='registered_plan', to='api.plans'),
        ),
        migrations.AlterField(
            model_name='plans',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name='PaymentTrackRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payer_account', models.CharField(max_length=225)),
                ('transaction', models.CharField(max_length=225)),
                ('status', models.CharField(choices=[['pending', 'pending'], ['reject', 'reject'], ['confirmed', 'confirmed']], default='pending', max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('payer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_record', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]