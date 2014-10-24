# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vote',
            old_name='ip',
            new_name='ip_address',
        ),
    ]
