# Generated by Django 5.0.6 on 2024-07-26 23:58

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clubs', '0002_alter_clubmember_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_title', models.CharField(default='unknown_event', max_length=100, verbose_name='이벤트 제목')),
                ('location', models.CharField(default='unknown_location', max_length=255, verbose_name='장소')),
                ('start_date_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='시작 시간')),
                ('end_date_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='종료 시간')),
                ('repeat_type', models.CharField(choices=[('NONE', '반복 안함'), ('DAY', '매일'), ('WEEK', '매주'), ('MONTH', '매월'), ('YEAR', '매년')], default='NONE', max_length=5, verbose_name='반복 타입')),
                ('game_mode', models.CharField(choices=[('MP', 'Match Play'), ('SP', 'Stroke Play')], default='SP', max_length=3, verbose_name='게임 모드')),
                ('alert_date_time', models.DateTimeField(blank=True, null=True, verbose_name='알람 일자')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.club')),
                ('club_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.clubmember')),
            ],
        ),
    ]
