# Generated by Django 4.0.6 on 2022-07-25 06:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0021_remove_gallery_content_type_remove_gallery_object_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotebookGallery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='', verbose_name='Изображение')),
            ],
        ),
        migrations.RemoveField(
            model_name='desktop',
            name='images',
        ),
        migrations.RemoveField(
            model_name='headphones',
            name='images',
        ),
        migrations.RemoveField(
            model_name='notebook',
            name='images',
        ),
        migrations.RemoveField(
            model_name='smartphone',
            name='images',
        ),
        migrations.DeleteModel(
            name='Gallery',
        ),
        migrations.AddField(
            model_name='notebookgallery',
            name='notebook',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='mainapp.notebook'),
        ),
    ]
