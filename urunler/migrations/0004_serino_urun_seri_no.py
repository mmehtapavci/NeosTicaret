# Generated by Django 4.2.1 on 2023-06-14 09:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('urunler', '0003_kategori_urun_kategori'),
    ]

    operations = [
        migrations.CreateModel(
            name='SeriNo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='urun',
            name='Seri_no',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='urunler.serino'),
        ),
    ]