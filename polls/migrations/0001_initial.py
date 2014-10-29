# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import polls.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('funds', models.DecimalField(default=0, decimal_places=2, max_digits=7)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('is_training', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Datum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('x', models.CharField(max_length=1024)),
                ('setId', models.IntegerField()),
                ('data_set', models.ForeignKey(to='polls.DataSet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Market',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('description', models.CharField(default='Add a description here. ', max_length=255)),
                ('pub_date', models.DateTimeField(verbose_name='Date Started')),
                ('exp_date', models.DateTimeField(default=polls.models.t, verbose_name='Expiration Date')),
                ('reveal_interval', models.IntegerField(default=1, verbose_name='Interval between challenges')),
                ('last_revealed_id', models.IntegerField(default=-1)),
                ('last_reveal_date', models.DateTimeField(default=polls.models.t, verbose_name='Date Last Challenge started')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MarketState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('market', models.ForeignKey(to='polls.Market')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('price', models.DecimalField(default=0, decimal_places=2, max_digits=7)),
                ('amount', models.DecimalField(default=0, decimal_places=2, max_digits=7)),
                ('timestamp', models.DateTimeField(verbose_name='Time created')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Outcome',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('current_price', models.IntegerField(default=0)),
                ('market', models.ForeignKey(to='polls.Market')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='order',
            name='claim',
            field=models.ForeignKey(to='polls.Outcome'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='datum',
            field=models.ForeignKey(to='polls.Datum'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='datum',
            name='y',
            field=models.ForeignKey(to='polls.Outcome'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dataset',
            name='market',
            field=models.ForeignKey(to='polls.Market'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='market',
            field=models.ForeignKey(to='polls.Market'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
