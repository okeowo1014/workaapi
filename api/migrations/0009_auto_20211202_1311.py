# Generated by Django 3.2.8 on 2021-12-02 13:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20211124_1241'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='uid',
            field=models.CharField(max_length=12, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='employer',
            name='uid',
            field=models.CharField(max_length=10, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='jobspost',
            name='job_key',
            field=models.CharField(max_length=16, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='applyjob',
            name='applicant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_applicant', to='api.employee'),
        ),
        migrations.AlterField(
            model_name='applyjob',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job', to='api.jobspost'),
        ),
        migrations.AlterField(
            model_name='jobspost',
            name='benefit',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='jobspost',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='jobspost',
            name='employer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_employer', to='api.employer'),
        ),
        migrations.AlterField(
            model_name='jobspost',
            name='qualification',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='jobspost',
            name='requirement',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='jobspost',
            name='tags',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='workexperience',
            name='end_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='workexperience',
            name='start_date',
            field=models.DateField(null=True),
        ),
    ]
