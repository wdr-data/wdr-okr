# Generated by Django 3.0.7 on 2020-06-24 09:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("okr", "0002_auto_20200624_1114"),
    ]

    operations = [
        migrations.RenameField(
            model_name="instainsight",
            old_name="emailContactsDay",
            new_name="email_contacts_day",
        ),
        migrations.RenameField(
            model_name="instainsight",
            old_name="textMessageClicksDay",
            new_name="text_message_clicks_day",
        ),
    ]
