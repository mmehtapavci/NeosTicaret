# Generated by Django 4.2.1 on 2023-07-24 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urunler', '0008_alter_odeme_urunler'),
    ]

    operations = [
        migrations.AddField(
            model_name='odeme',
            name='dendiMi',
            field=models.BooleanField(default=False),
        ),
    ]