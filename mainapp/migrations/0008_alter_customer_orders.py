# Generated by Django 4.0.6 on 2022-07-17 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0007_customer_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='orders',
            field=models.ManyToManyField(blank=True, related_name='related_order', to='mainapp.order', verbose_name='Заказы покупателя'),
        ),
    ]
