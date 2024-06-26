from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('document_states', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflowstate',
            name='completion',
            field=models.IntegerField(
                default=0, help_text='Enter the percent of completion that '
                'this state represents in relation to the workflow. Use '
                'numbers without the percent sign.', verbose_name='Completion',
                blank=True
            ),
            preserve_default=True,
        ),
    ]
