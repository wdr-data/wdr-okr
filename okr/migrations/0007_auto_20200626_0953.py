# Generated by Django 3.0.7 on 2020-06-26 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("okr", "0006_auto_20200626_0930"),
    ]

    operations = [
        migrations.AddField(
            model_name="instacollaboration",
            name="topic",
            field=models.TextField(
                default="", help_text="Thema der Kollaboration", verbose_name="Thema"
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="instacollaboration",
            name="description",
            field=models.TextField(verbose_name="Notiz", blank=True),
        ),
        migrations.AlterField(
            model_name="instacollaboration",
            name="followers",
            field=models.IntegerField(
                help_text="Anzahl Follower der Influencer*in", verbose_name="Follower"
            ),
        ),
    ]
