# Generated by Django 4.2 on 2023-05-07 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_alter_productrequest_id_alter_profile_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='productrequest',
            name='accepted_by',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
