# Generated by Django 5.0.6 on 2024-08-15 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("participants", "0004_remove_holescore_event"),
    ]

    operations = [
        migrations.AddField(
            model_name="participant",
            name="handicap_score",
            field=models.IntegerField(default=0, verbose_name="핸디캡 점수"),
        ),
    ]