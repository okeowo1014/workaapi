# Generated by Django 3.2.8 on 2021-12-04 16:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0011_jobspost_salary_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobspost',
            name='salary_type',
            field=models.CharField(
                choices=[['hourly', 'hour'], ['monthly', 'month'], ['weekly', 'week'], ['annually', 'annual']],
                max_length=10),
        ),
    ]
