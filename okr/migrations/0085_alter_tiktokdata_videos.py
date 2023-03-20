# Generated by Django 4.1.3 on 2022-12-20 19:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("okr", "0084_auto_20220905_1415"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tiktokdata",
            name="videos",
            field=models.IntegerField(
                help_text="Anzahl der Videos des Accounts. Wird automatisch berechnet und kann daher von der tatsächlichen Anzahl der Videos im Account abweichen.",
                null=True,
                verbose_name="Videos",
            ),
        ),
    ]
