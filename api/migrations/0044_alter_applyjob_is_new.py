# Generated by Django 4.0.2 on 2022-04-16 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0043_applyjob_is_new_alter_education_certificate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applyjob',
            name='is_new',
            field=models.BooleanField(default=True),
        ),
    ]