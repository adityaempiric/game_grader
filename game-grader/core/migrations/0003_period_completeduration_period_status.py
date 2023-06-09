# Generated by Django 4.1.5 on 2023-02-23 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_user_username_alter_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='period',
            name='completeduration',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='period',
            name='status',
            field=models.CharField(choices=[('Completed', 'Completed'), ('InProgress', 'InProgress'), ('Pending', 'Pending'), ('inComplete', 'inComplete')], default='inComplete', max_length=20),
        ),
    ]
