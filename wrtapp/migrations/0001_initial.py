# Generated by Django 3.2.9 on 2021-11-13 15:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mac', models.CharField(max_length=32)),
                ('model', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=64)),
                ('description', models.CharField(max_length=128)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('device', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='wrtapp.device')),
                ('hostname', models.CharField(max_length=64)),
                ('ip', models.GenericIPAddressField(protocol='IPv4')),
                ('netmask', models.GenericIPAddressField(protocol='IPv4')),
                ('gateway', models.GenericIPAddressField(protocol='IPv4')),
                ('dns1', models.GenericIPAddressField(protocol='IPv4')),
                ('dns2', models.GenericIPAddressField(protocol='IPv4')),
            ],
        ),
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('device', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='wrtapp.device')),
                ('status', models.CharField(max_length=32)),
                ('cpu_load', models.FloatField()),
                ('memory_usage', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('severity', models.CharField(max_length=32)),
                ('message', models.CharField(max_length=128)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wrtapp.device')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
