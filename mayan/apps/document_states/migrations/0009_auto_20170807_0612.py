from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('document_states', '0008_auto_20170803_0752')
    ]

    operations = [
        migrations.CreateModel(
            name='WorkflowStateAction',
            fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'label', models.CharField(
                        max_length=255, verbose_name='Label'
                    )
                ),
                (
                    'enabled', models.BooleanField(
                        default=True, verbose_name='Enabled'
                    )
                ),
                (
                    'when', models.PositiveIntegerField(
                        choices=[(1, 'On entry'), (2, 'On exit')], default=1,
                        help_text='At which moment of the state this action '
                        'will execute', verbose_name='When'
                    )
                ),
                (
                    'action_path', models.CharField(
                        help_text='The dotted Python path to the workflow '
                        'action class to execute.', max_length=128,
                        verbose_name='Entry action path'
                    )
                ),
                (
                    'action_data', models.TextField(
                        blank=True, verbose_name='Entry action data'
                    )
                ),
                (
                    'state', models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='actions',
                        to='document_states.WorkflowState',
                        verbose_name='Workflow state'
                    )
                )
            ],
            options={
                'ordering': ('label',),
                'verbose_name': 'Workflow state action',
                'verbose_name_plural': 'Workflow state actions'
            }
        ),
        migrations.AlterUniqueTogether(
            name='workflowstateaction',
            unique_together={
                ('state', 'label')
            }
        )
    ]
