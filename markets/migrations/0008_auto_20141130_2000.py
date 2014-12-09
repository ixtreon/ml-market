# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('markets', '0007_auto_20141123_2236'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dataset',
            old_name='active_datum_start',
            new_name='challenge_start',
        ),
    ]
