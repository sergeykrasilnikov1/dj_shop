# Generated by Django 4.0.6 on 2022-07-24 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0020_remove_desktop_image_remove_headphones_image_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gallery',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='gallery',
            name='object_id',
        ),
        migrations.AddField(
            model_name='desktop',
            name='images',
            field=models.ManyToManyField(blank=True, to='mainapp.gallery'),
        ),
        migrations.AddField(
            model_name='headphones',
            name='images',
            field=models.ManyToManyField(blank=True, to='mainapp.gallery'),
        ),
        migrations.AddField(
            model_name='notebook',
            name='images',
            field=models.ManyToManyField(blank=True, to='mainapp.gallery'),
        ),
        migrations.AddField(
            model_name='smartphone',
            name='images',
            field=models.ManyToManyField(blank=True, to='mainapp.gallery'),
        ),
    ]