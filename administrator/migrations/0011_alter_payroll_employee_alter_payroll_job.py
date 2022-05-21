# Generated by Django 4.0.2 on 2022-05-09 19:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0053_staff_roles'),
        ('administrator', '0010_alter_payroll_balance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payroll',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employed', to='api.employee'),
        ),
        migrations.AlterField(
            model_name='payroll',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payroll_job', to='api.jobspost'),
        ),
    ]