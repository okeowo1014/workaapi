# Generated by Django 4.0.2 on 2022-05-09 11:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0053_staff_roles'),
        ('administrator', '0006_employment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='employment',
            name='currency',
            field=models.CharField(default='NGN', max_length=4),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='employment',
            name='salary',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='employment',
            name='status',
            field=models.CharField(choices=[['active', 'active'], ['cancelled', 'cancelled'], ['suspended', 'suspended']], default='active', max_length=255),
        ),
        migrations.CreateModel(
            name='Payroll',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(max_length=4)),
                ('salary', models.PositiveIntegerField()),
                ('resumption', models.DateField()),
                ('resignation', models.DateField(null=True)),
                ('payment', models.PositiveIntegerField()),
                ('balance', models.PositiveIntegerField()),
                ('job_status', models.CharField(max_length=200)),
                ('payment_status', models.CharField(max_length=200)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.employee')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.jobspost')),
            ],
        ),
    ]
