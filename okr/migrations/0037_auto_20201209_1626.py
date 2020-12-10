# Generated by Django 3.1.4 on 2020-12-09 15:26

from django.db import migrations, models
import django.db.models.deletion


def add_sophora_id_to_page(apps, schema_editor):
    Page = apps.get_model("okr", "Page")
    SophoraID = apps.get_model("okr", "SophoraID")

    if Page.objects.count() == 0:
        return

    from ..scrapers.pages import _parse_sophora_url

    for page in Page.objects.all():
        sophora_id_str, *_ = _parse_sophora_url(page.url)
        sophora_id, created = SophoraID.objects.get_or_create(
            sophora_id=sophora_id_str,
            defaults=dict(
                sophora_document=None,
            ),
        )
        page.sophora_id = sophora_id
        page.save()


def convert_sophora_id_to_foreignkey(apps, schema_editor):
    SophoraDocumentMeta = apps.get_model("okr", "SophoraDocumentMeta")
    SophoraID = apps.get_model("okr", "SophoraID")

    if SophoraDocumentMeta.objects.count() == 0:
        return

    for meta in SophoraDocumentMeta.objects.all():
        sophora_id, created = SophoraID.objects.get_or_create(
            sophora_id=meta.sophora_id,
            defaults=dict(
                sophora_document=meta.sophora_document,
            ),
        )
        meta.sophora_id_new = sophora_id
        meta.save()


class Migration(migrations.Migration):

    dependencies = [
        ("okr", "0036_podcastepisode_available"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="sophoraid",
            options={
                "ordering": ["-created"],
                "verbose_name": "Sophora-ID",
                "verbose_name_plural": "Sophora-IDs",
            },
        ),
        migrations.AlterField(
            model_name="sophoraid",
            name="sophora_document",
            field=models.ForeignKey(
                help_text="Das Sophora-Dokument, zu dem diese ID gehört (hat)",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sophora_ids",
                related_query_name="sophora_id",
                to="okr.sophoradocument",
                verbose_name="Sophora-Dokument",
            ),
        ),
        migrations.AlterModelTable(
            name="sophoraid",
            table="sophora_id",
        ),
        # Add relation to SophoraID on Page
        migrations.AddField(
            model_name="page",
            name="sophora_id",
            field=models.ForeignKey(
                help_text="Sophora ID der Seite",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="pages",
                related_query_name="page",
                to="okr.sophoraid",
                verbose_name="Sophora ID",
            ),
        ),
        migrations.RunPython(add_sophora_id_to_page),
        # Refactor sophora_id on document meta to foreign key
        migrations.AddField(
            model_name="sophoradocumentmeta",
            name="sophora_id_new",
            field=models.ForeignKey(
                null=True,
                help_text="Momentane Sophora ID des Dokuments",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="metas",
                related_query_name="meta",
                to="okr.sophoraid",
                verbose_name="Sophora ID",
            ),
        ),
        migrations.RunPython(convert_sophora_id_to_foreignkey),
        migrations.AlterUniqueTogether(
            name="sophoradocumentmeta",
            unique_together={
                ("sophora_document", "headline", "teaser", "document_type", "node")
            },
        ),
        migrations.RemoveField(
            model_name="sophoradocumentmeta",
            name="sophora_id",
        ),
        migrations.RenameField(
            model_name="sophoradocumentmeta",
            old_name="sophora_id_new",
            new_name="sophora_id",
        ),
        migrations.AlterField(
            model_name="sophoradocumentmeta",
            name="sophora_id",
            field=models.ForeignKey(
                help_text="Momentane Sophora ID des Dokuments",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="metas",
                related_query_name="meta",
                to="okr.sophoraid",
                verbose_name="Sophora ID",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="sophoradocumentmeta",
            unique_together={
                (
                    "sophora_document",
                    "headline",
                    "teaser",
                    "document_type",
                    "sophora_id",
                    "node",
                )
            },
        ),
    ]
