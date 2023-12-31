# Generated by Django 4.2.1 on 2023-06-14 18:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('urunler', '0004_serino_urun_seri_no'),
    ]

    operations = [
        migrations.CreateModel(
            name='AltKategori',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isim', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='urun',
            name='Seri_no',
        ),
        migrations.AddField(
            model_name='urun',
            name='AltKategori',
            field=models.ManyToManyField(blank=True, to='urunler.altkategori'),
        ),
        migrations.AddField(
            model_name='urun',
            name='seri_no',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='urunler.serino'),
        ),
    ]
