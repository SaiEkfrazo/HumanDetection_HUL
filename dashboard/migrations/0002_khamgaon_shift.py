# Generated by Django 5.1.1 on 2024-09-09 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='khamgaon',
            name='shift',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
