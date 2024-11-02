# Generated by Django 3.0.7 on 2024-10-18 17:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tour_management', '0011_auto_20241018_1723'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarType',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=255)),
                ('capacity', models.IntegerField()),
                ('tour_operator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tour_management.Touroperator')),
            ],
        ),
    ]