# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('funds', models.DecimalField(max_digits=7, decimal_places=2, default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataSet',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('description', models.CharField(default='Add a description here. ', max_length=255)),
                ('is_training', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('datum_count', models.IntegerField(default=0)),
                ('reveal_interval', models.IntegerField(verbose_name='Interval between challenges', default=7)),
                ('active_datum_id', models.IntegerField(default=0)),
                ('active_datum_start', models.DateTimeField(verbose_name='Date last challenge was started', default=datetime.datetime(2014, 1, 1, 0, 0))),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Datum',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('x', models.CharField(max_length=1024)),
                ('set_id', models.IntegerField()),
                ('data_set', models.ForeignKey(to='markets.DataSet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('description', models.CharField(default='Add a description here. ', max_length=255)),
                ('pub_date', models.DateTimeField(verbose_name='Date Started')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MarketState',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('market', models.ForeignKey(to='markets.Market')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('timestamp', models.DateTimeField(verbose_name='Time created')),
                ('is_processed', models.BooleanField(default=False)),
                ('account', models.ForeignKey(to='markets.Account')),
                ('datum', models.ForeignKey(to='markets.Datum')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Outcome',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('current_price', models.DecimalField(max_digits=7, decimal_places=2, default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Outcomes',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('description', models.CharField(default='Some outcome set', max_length=255)),
                ('market', models.ForeignKey(to='markets.Market')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('amount', models.DecimalField(max_digits=7, decimal_places=2, default=0)),
                ('contract_price', models.DecimalField(max_digits=7, decimal_places=2, default=0)),
                ('order', models.ForeignKey(to='markets.Order')),
                ('outcome', models.ForeignKey(to='markets.Outcome')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('datum', models.ForeignKey(to='markets.Datum')),
                ('outcome', models.ForeignKey(to='markets.Outcome')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='outcome',
            name='set',
            field=models.ForeignKey(to='markets.Outcomes', default=1),
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
