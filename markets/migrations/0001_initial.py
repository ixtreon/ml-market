# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import markets.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('funds', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataSet',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('is_training', models.BooleanField(default=False)),
                ('datum_count', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Datum',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('x', models.CharField(max_length=1024)),
                ('setId', models.IntegerField()),
                ('data_set', models.ForeignKey(to='markets.DataSet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('file', models.FileField(upload_to='uploads')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Market',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('description', models.CharField(max_length=255, default='Add a description here. ')),
                ('pub_date', models.DateTimeField(verbose_name='Date Started')),
                ('exp_date', models.DateTimeField(default=markets.models.t, verbose_name='Expiration Date')),
                ('reveal_interval', models.IntegerField(default=1, verbose_name='Interval between challenges')),
                ('last_revealed_id', models.IntegerField(default=-1, verbose_name='Current challenge id')),
                ('last_reveal_date', models.DateTimeField(default=markets.models.t, verbose_name='Date Last Challenge started')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MarketState',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('market', models.ForeignKey(to='markets.Market')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('timestamp', models.DateTimeField(verbose_name='Time created')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Outcome',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('current_price', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('market', models.ForeignKey(to='markets.Market')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='order',
            name='claim',
            field=models.ForeignKey(to='markets.Outcome'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='datum',
            field=models.ForeignKey(to='markets.Datum'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='datum',
            name='y',
            field=models.ForeignKey(to='markets.Outcome'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dataset',
            name='market',
            field=models.ForeignKey(to='markets.Market'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='market',
            field=models.ForeignKey(to='markets.Market'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
