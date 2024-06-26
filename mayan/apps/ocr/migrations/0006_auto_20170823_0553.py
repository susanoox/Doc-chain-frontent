from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0040_auto_20170725_1111'),
        ('ocr', '0005_auto_20170630_1846')
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentPageOCRContent',
            fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'content', models.TextField(
                        blank=True, verbose_name='Content'
                    )
                ),
                (
                    'document_page', models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='ocr', to='documents.DocumentPage',
                        verbose_name='Document page'
                    )
                )
            ],
            options={
                'verbose_name': 'Document page OCR content',
                'verbose_name_plural': 'Document pages OCR contents'
            }
        ),
        migrations.RemoveField(
            model_name='documentpagecontent',
            name='document_page',
        ),
        migrations.AlterModelOptions(
            name='documentversionocrerror',
            options={
                'ordering': ('datetime_submitted',),
                'verbose_name': 'Document version OCR error',
                'verbose_name_plural': 'Document version OCR errors'
            }
        ),
        migrations.AlterField(
            model_name='documentversionocrerror',
            name='datetime_submitted',
            field=models.DateTimeField(
                auto_now_add=True, db_index=True,
                verbose_name='Date time submitted'
            )
        ),
        migrations.DeleteModel(
            name='DocumentPageContent'
        )
    ]
