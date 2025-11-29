from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tour_management', '0018_add_room_selection_to_packages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AddField(
            model_name='package',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]

