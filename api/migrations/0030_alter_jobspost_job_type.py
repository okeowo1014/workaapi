# Generated by Django 3.2.8 on 2022-02-11 19:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0029_likedjobs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobspost',
            name='job_type',
            field=models.CharField(
                choices=[['full time', 'full time'], ['part time', 'part time'], ['contract', 'contract'],
                         ['internship', 'internship'], ['voluntary', 'voluntary']], max_length=255),
        ),
    ]
