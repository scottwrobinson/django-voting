# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('direction', models.IntegerField(choices=[(b'up', 1), (b'down', -1)])),
                ('ip', models.GenericIPAddressField(editable=False)),
                ('date_created', models.DateTimeField(editable=False)),
                ('user', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-date_created',),
                'get_latest_by': 'date_created',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VoteCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('upvotes', models.PositiveIntegerField(default=0)),
                ('downvotes', models.PositiveIntegerField(default=0)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('object_pk', models.TextField(verbose_name=b'object ID')),
                ('content_type', models.ForeignKey(related_name='content_type_set_for_votecount', verbose_name=b'content type', to='contenttypes.ContentType')),
            ],
            options={
                'get_latest_by': 'modified',
                'verbose_name': 'Vote Count',
                'verbose_name_plural': 'Vote Counts',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='vote',
            name='votecount',
            field=models.ForeignKey(editable=False, to='voting.VoteCount'),
            preserve_default=True,
        ),
    ]
