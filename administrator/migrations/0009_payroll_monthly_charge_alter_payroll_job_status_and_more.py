# Generated by Django 4.0.2 on 2022-05-09 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0053_staff_roles'),
        ('administrator', '0008_payroll_payment_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='payroll',
            name='monthly_charge',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='payroll',
            name='job_status',
            field=models.CharField(choices=[['active', 'active'], ['cancelled', 'cancelled'], ['suspended', 'suspended']], default='active', max_length=200),
        ),
        migrations.AlterField(
            model_name='payroll',
            name='payment_status',
            field=models.CharField(choices=[['active', 'active'], ['completed', 'completed'], ['suspended', 'suspended']], default='active', max_length=200),
        ),
        migrations.AlterUniqueTogether(
            name='payroll',
            unique_together={('job', 'employee')},
        ),
    ]
