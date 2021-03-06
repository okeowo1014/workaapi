# Generated by Django 4.0.2 on 2022-03-17 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0033_alter_education_course'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeletedUsers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('firstname', models.CharField(max_length=255)),
                ('lastname', models.CharField(max_length=255)),
                ('account_type', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=255)),
                ('location', models.CharField(max_length=255)),
                ('about', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Support',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('fullname', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=255)),
                ('title', models.TextField()),
                ('message', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='jobspost',
            name='currency',
            field=models.CharField(default='NGN', max_length=10),
        ),
        migrations.AlterField(
            model_name='employee',
            name='display_picture',
            field=models.URLField(default='https://api.workanetworks.com/media/display-picture/7/download.png'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='location',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='employer',
            name='company_email',
            field=models.EmailField(default='', max_length=254),
        ),
        migrations.AlterField(
            model_name='employer',
            name='company_logo',
            field=models.URLField(default='https://api.workanetworks.com/media/company-logo/b32g3zvg2y/1024.png'),
        ),
        migrations.AlterField(
            model_name='employer',
            name='company_website',
            field=models.CharField(default='', max_length=255),
        ),
    ]
