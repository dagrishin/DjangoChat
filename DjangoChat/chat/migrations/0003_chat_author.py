# Generated by Django 3.0.6 on 2020-06-01 10:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_auto_20200601_1345'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='chat.Contact'),
            preserve_default=False,
        ),
    ]
