# Generated by Django 3.2.5 on 2021-07-16 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='next_namaz',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
