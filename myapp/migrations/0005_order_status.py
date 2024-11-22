# Generated by Django 5.1.2 on 2024-10-27 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_order_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('placed', 'Placed'), ('canceled', 'Canceled')], default='placed', max_length=20),
        ),
    ]
