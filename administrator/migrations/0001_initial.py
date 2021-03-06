# Generated by Django 4.0.2 on 2022-05-07 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Employment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=255)),
                ('company_email', models.EmailField(default='', max_length=254)),
                ('employer_email', models.EmailField(max_length=254)),
                ('employer_uid', models.CharField(max_length=255)),
                ('salary', models.CharField(max_length=255)),
                ('resumption', models.DateField()),
                ('employees_email', models.TextField()),
                ('job_key', models.CharField(max_length=200)),
                ('job_title', models.CharField(max_length=200)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
