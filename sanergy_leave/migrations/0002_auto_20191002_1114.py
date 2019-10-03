# Generated by Django 2.2.5 on 2019-10-02 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sanergy_leave', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leavetype',
            name='Leave_Types',
            field=models.CharField(choices=[('MATERNITY_LEAVE', 'MATERNITY_LEAVE'), ('PATERNITY_LEAVE', 'PATERNITY_LEAVE'), ('ANNUAL_LEAVE', 'ANNUAL_LEAVE'), ('COMPASSIONATE_LEAVE', 'COMPASSIONATE_LEAVE'), ('SICK_LEAVE', 'SICK_LEAVE'), ('STUDY_LEAVE', 'STUDY_LEAVE')], default='annual', max_length=20),
        ),
    ]