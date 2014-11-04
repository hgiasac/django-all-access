# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import allaccess.fields
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountAccess',
            fields=[
                ('id', allaccess.fields.BigUUIDField(serialize=False, primary_key=True)),
                ('identifier', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('access_token', allaccess.fields.EncryptedField(null=True, blank=True, default=None)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('request_token_url', models.CharField(blank=True, max_length=255)),
                ('authorization_url', models.CharField(max_length=255)),
                ('access_token_url', models.CharField(max_length=255)),
                ('profile_url', models.CharField(max_length=255)),
                ('consumer_key', allaccess.fields.EncryptedField(null=True, blank=True, default=None)),
                ('consumer_secret', allaccess.fields.EncryptedField(null=True, blank=True, default=None)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='accountaccess',
            name='provider',
            field=models.ForeignKey(to='allaccess.Provider'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='accountaccess',
            name='user',
            field=allaccess.fields.BigForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='accountaccess',
            unique_together=set([('identifier', 'provider')]),
        ),
    ]
