# Generated by Django 3.1.4 on 2020-12-10 14:34

from django.db import migrations, models


def set_node(apps, schema_editor):
    Page = apps.get_model("okr", "Page")

    if Page.objects.count() == 0:
        return

    from ..scrapers.pages import _parse_sophora_url

    for page in Page.objects.all():
        _, node, _ = _parse_sophora_url(page.url)
        page.node = node
        page.save()


class Migration(migrations.Migration):
    dependencies = [
        ("okr", "0038_auto_20201210_1505"),
    ]

    operations = [
        migrations.AddField(
            model_name="page",
            name="node",
            field=models.CharField(
                help_text="Der Sophora-Strukturknoten, unter dem der Nachrichtenartikel gefunden wurde",
                max_length=128,
                null=True,
                verbose_name="Strukturknoten",
            ),
        ),
        migrations.RunPython(set_node),
    ]
