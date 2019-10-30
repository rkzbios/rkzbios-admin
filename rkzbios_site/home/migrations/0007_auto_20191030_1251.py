# Generated by Django 2.2.6 on 2019-10-30 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_auto_20191029_1734'),
    ]

    operations = [
        migrations.AddField(
            model_name='filmpage',
            name='trailer',
            field=models.URLField(blank=True, null=True, verbose_name='Trailer'),
        ),
        migrations.AlterField(
            model_name='filmpage',
            name='lengthInMinutes',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='filmpage',
            name='minimumAge',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]