# Generated by Django 2.2.3 on 2019-11-14 15:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('environment', models.CharField(choices=[('LAB', 'lab device'), ('PROD', 'production device')], default='PROD', max_length=4)),
                ('os_type', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='DeviceInterface',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lab.Device')),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='RouteSwitchConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('text', models.TextField()),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lab.Device')),
            ],
        ),
        migrations.CreateModel(
            name='InterfaceMapper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lab_device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lab', to='lab.DeviceInterface')),
                ('prod_device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prod', to='lab.DeviceInterface')),
            ],
        ),
        migrations.CreateModel(
            name='DevicePair',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lab_device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lab', to='lab.Device')),
                ('prod_device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prod', to='lab.Device')),
            ],
        ),
    ]
