# Generated by Django 4.0.6 on 2022-07-25 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0023_smartphonegallery_headphonesgallery_desktopgallery'),
    ]

    operations = [
        migrations.AddField(
            model_name='desktop',
            name='image',
            field=models.ImageField(null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='headphones',
            name='image',
            field=models.ImageField(null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='notebook',
            name='image',
            field=models.ImageField(null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='smartphone',
            name='image',
            field=models.ImageField(null=True, upload_to=''),
        ),
    ]