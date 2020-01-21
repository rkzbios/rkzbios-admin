# Generated by Django 2.2.6 on 2019-11-27 16:08

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0041_group_collection_permissions_verbose_name_plural'),
        ('home', '0002_auto_20191127_1240'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.core.fields.StreamField([('heading', wagtail.core.blocks.CharBlock(classname='full title')), ('paragraph', wagtail.core.blocks.TextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('quotation', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.TextBlock()), ('author', wagtail.core.blocks.CharBlock())]))], blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.AlterField(
            model_name='moviepage',
            name='showEndDate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='moviepage',
            name='showStartDate',
            field=models.DateField(blank=True, null=True),
        ),
    ]