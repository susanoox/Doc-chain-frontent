from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0001_initial')
    ]

    operations = [
        migrations.CreateModel(
            name='PermissionHolder',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False,
                        auto_created=True, primary_key=True
                    )
                ),
                (
                    'holder_id', models.PositiveIntegerField()
                ),
                (
                    'holder_type', models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name='permission_holder',
                        to='contenttypes.ContentType'
                    )
                )
            ],
            options={
                'verbose_name': 'Permission holder',
                'verbose_name_plural': 'Permission holders'
            },
            bases=(models.Model,)
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False,
                        auto_created=True, primary_key=True
                    )
                ),
                (
                    'name', models.CharField(unique=True, max_length=64)
                ),
                (
                    'label', models.CharField(
                        unique=True, max_length=64, verbose_name='Label'
                    )
                )
            ],
            options={
                'ordering': ('label',),
                'verbose_name': 'Role',
                'verbose_name_plural': 'Roles'
            },
            bases=(models.Model,)
        ),
        migrations.CreateModel(
            name='RoleMember',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False,
                        auto_created=True, primary_key=True
                    )
                ),
                (
                    'member_id', models.PositiveIntegerField()
                ),
                (
                    'member_type', models.ForeignKey(
                        on_delete=models.CASCADE, related_name='role_member',
                        to='contenttypes.ContentType'
                    )
                ),
                (
                    'role', models.ForeignKey(
                        on_delete=models.CASCADE, to='permissions.Role',
                        verbose_name='Role'
                    )
                )
            ],
            options={
                'verbose_name': 'Role member',
                'verbose_name_plural': 'Role members'
            },
            bases=(models.Model,)
        ),
        migrations.CreateModel(
            name='StoredPermission',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False,
                        auto_created=True, primary_key=True
                    )
                ),
                (
                    'namespace', models.CharField(
                        max_length=64, verbose_name='Namespace'
                    )
                ),
                (
                    'name', models.CharField(
                        max_length=64, verbose_name='Name'
                    )
                )
            ],
            options={
                'ordering': ('namespace',),
                'verbose_name': 'Permission',
                'verbose_name_plural': 'Permissions'
            },
            bases=(models.Model,)
        ),
        migrations.AlterUniqueTogether(
            name='storedpermission', unique_together={
                ('namespace', 'name')
            }
        ),
        migrations.AddField(
            model_name='permissionholder',
            name='permission',
            field=models.ForeignKey(
                on_delete=models.CASCADE, to='permissions.StoredPermission',
                verbose_name='Permission'
            ),
            preserve_default=True
        )
    ]
