# Generated by Django 3.1.6 on 2021-02-05 12:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Smartphone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Найменування')),
                ('slug', models.SlugField(unique=True)),
                ('image', models.ImageField(upload_to='', verbose_name='Зображення')),
                ('description', models.TextField(null=True, verbose_name='Опис')),
                ('price', models.DecimalField(decimal_places=2, max_digits=9, verbose_name='Ціна')),
                ('diagonal', models.CharField(max_length=255, verbose_name='Діагональ')),
                ('display', models.CharField(max_length=255, verbose_name='Тип дисплея')),
                ('resolution', models.CharField(max_length=255, verbose_name='Розширення екрана')),
                ('accum_volume', models.CharField(max_length=255, verbose_name="об'єм батареї")),
                ('ram', models.CharField(max_length=255, verbose_name="Оперативна пам'ять")),
                ('sd', models.BooleanField(default=True)),
                ('sd_volume_max', models.CharField(max_length=255, verbose_name="Максимальний об'єм встроєної пам'яті")),
                ('main_cam_mp', models.CharField(max_length=255, verbose_name='Головна камера')),
                ('frontal_cam_mp', models.CharField(max_length=255, verbose_name='Фронтальна камера')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.category', verbose_name='Категорія')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Notebook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Найменування')),
                ('slug', models.SlugField(unique=True)),
                ('image', models.ImageField(upload_to='', verbose_name='Зображення')),
                ('description', models.TextField(null=True, verbose_name='Опис')),
                ('price', models.DecimalField(decimal_places=2, max_digits=9, verbose_name='Ціна')),
                ('diagonal', models.CharField(max_length=255, verbose_name='Діагональ')),
                ('display', models.CharField(max_length=255, verbose_name='Тип дисплея')),
                ('processor_freq', models.CharField(max_length=255, verbose_name='Частота процессора')),
                ('ram', models.CharField(max_length=255, verbose_name="Оперативна пам'ять")),
                ('video', models.CharField(max_length=255, verbose_name='Відеокарта')),
                ('time_without_charge', models.CharField(max_length=255, verbose_name='Час роботи батареї')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.category', verbose_name='Категорія')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]