# Generated by Django 2.2.6 on 2019-12-02 20:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_auto_20191127_1608'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moviepage',
            name='doubleBillMovie',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='home.MoviePage'),
        ),
    ]
