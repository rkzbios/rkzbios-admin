# Generated by Django 2.2.6 on 2019-10-31 11:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0041_group_collection_permissions_verbose_name_plural'),
        ('home', '0007_auto_20191030_1251'),
    ]

    operations = [
        migrations.AddField(
            model_name='filmpage',
            name='doubleBillFilm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.Page'),
        ),
    ]