# Generated by Django 3.2 on 2024-11-04 10:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tour_management', '0050_lead_leadcardealermapping_leaddestinationmapping_leadhotelmapping_leaditineraryitem_leadpackage'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='tour_management.user'),
        ),
        migrations.AddField(
            model_name='lead',
            name='tour_operator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='tour_management.touroperator'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='tour_operator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='tour_management.touroperator'),
        ),
        migrations.AlterField(
            model_name='lead',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tour_management.customer'),
        ),
        migrations.AlterField(
            model_name='lead',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='leadcardealermapping',
            name='car_dealer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tour_management.cardealer'),
        ),
        migrations.AlterField(
            model_name='leadcardealermapping',
            name='lead_package',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tour_management.leadpackage'),
        ),
        migrations.AlterField(
            model_name='leadcardealermapping',
            name='selected_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='tour_management.user'),
        ),
        migrations.AlterField(
            model_name='leaddestinationmapping',
            name='destination',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tour_management.destination'),
        ),
        migrations.AlterField(
            model_name='leaddestinationmapping',
            name='lead_package',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tour_management.leadpackage'),
        ),
        migrations.AlterField(
            model_name='leadhotelmapping',
            name='hotel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tour_management.hotel'),
        ),
        migrations.AlterField(
            model_name='leadhotelmapping',
            name='lead_package',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tour_management.leadpackage'),
        ),
        migrations.AlterField(
            model_name='leadhotelmapping',
            name='selected_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='tour_management.user'),
        ),
        migrations.AlterField(
            model_name='leaditineraryitem',
            name='itinerary_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='tour_management.itineraryitem'),
        ),
        migrations.AlterField(
            model_name='leaditineraryitem',
            name='lead_package',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tour_management.leadpackage'),
        ),
        migrations.AlterField(
            model_name='leadpackage',
            name='destination',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='tour_management.destination'),
        ),
        migrations.AlterField(
            model_name='leadpackage',
            name='lead',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tour_management.lead'),
        ),
        migrations.AlterField(
            model_name='leadpackage',
            name='tour_operator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='tour_management.touroperator'),
        ),
    ]
