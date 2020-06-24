# Generated by Django 3.0.7 on 2020-06-24 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("okr", "0003_auto_20200624_1122"),
    ]

    operations = [
        migrations.RenameField(
            model_name="instastory", old_name="message", new_name="caption",
        ),
        migrations.RemoveField(model_name="instastory", name="comments",),
        migrations.RemoveField(model_name="instastory", name="likes",),
        migrations.AddField(
            model_name="instastory",
            name="exits",
            field=models.IntegerField(default=0, verbose_name="Exits"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="instastory",
            name="replies",
            field=models.IntegerField(default=0, verbose_name="Antworten"),
            preserve_default=False,
        ),
    ]