# Generated by Django 4.2.1 on 2023-07-25 12:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('urunler', '0009_odeme_dendimi'),
    ]

    operations = [
        migrations.RenameField(
            model_name='odeme',
            old_name='dendiMi',
            new_name='odendiMi',
        ),
    ]
