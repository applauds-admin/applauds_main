# Generated by Django 4.1.9 on 2023-05-16 07:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0003_task_verification_url_alter_task_verification_class"),
    ]

    operations = [
        migrations.AddField(
            model_name="taskuser",
            name="request_hash",
            field=models.CharField(
                blank=True,
                max_length=64,
                null=True,
                verbose_name="Verified By Functions",
            ),
        ),
    ]
