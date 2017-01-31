# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-01-30 21:05
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('community', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sponser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('braintree_id', models.CharField(blank=True, max_length=100, null=True)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Support',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sponser', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='support.Sponser')),
                ('studentneed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='community.StudentNeed')),
            ],
        ),
        migrations.CreateModel(
            name='SupportDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('on process', 'On Process'), ('completed', 'Completed')], default='on process', max_length=120)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=50)),
                ('support', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='support.Support')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='support.Sponser')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
    ]
