# Generated by Django 4.2.1 on 2023-05-09 20:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0017_alter_producer_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='producer',
            old_name='_id',
            new_name='producer_id',
        ),
    ]
