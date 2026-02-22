from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tracking", "0002_expense"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="max_writer_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="project",
            name="max_photographer_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="project",
            name="max_videographer_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="project",
            name="max_editor_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="project",
            name="pay_writer",
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name="project",
            name="pay_photographer",
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name="project",
            name="pay_videographer",
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name="project",
            name="pay_editor",
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12),
        ),
    ]
