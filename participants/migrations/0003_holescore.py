# Generated by Django 5.0.6 on 2024-08-01 02:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_remove_event_club_member'),
        ('participants', '0002_participant_created_at_participant_updated_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='HoleScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hole_number', models.IntegerField(default=1, verbose_name='홀 번호')),
                ('score', models.IntegerField(default=0, verbose_name='홀 점수')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.event')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='participants.participant')),
            ],
        ),
    ]
