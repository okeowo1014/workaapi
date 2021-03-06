# Generated by Django 4.0.2 on 2022-04-15 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0042_jobspost_shortlist_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='applyjob',
            name='is_new',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='education',
            name='certificate',
            field=models.CharField(choices=[('leaving school', 'leaving school'), ('o level', 'o level'), ('nce', 'NCE'), ('diploma', 'Diploma'), ('ond', 'National Diploma'), ('technician', 'Technician'), ('hnd', 'Higher National Diploma'), ('bsc', 'Bachelor of Science'), ('bseng', 'Bachelor of Engineering'), ('btech', 'Bachelor of Technology'), ('bedu', 'Bachelor of Education')], max_length=255),
        ),
    ]
