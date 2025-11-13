# Generated manually on 2025-11-13
# Simplifies Transaction model to reference Lead instead of storing snapshot data

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tour_management', '0006_add_lead_package_snapshot_fields'),
    ]

    operations = [
        # Drop old transaction-related tables
        migrations.DeleteModel(
            name='TransactionItineraryDetails',
        ),
        migrations.DeleteModel(
            name='TransactionDayDetails',
        ),

        # Remove fields we don't need anymore
        migrations.RemoveField(
            model_name='transaction',
            name='contains_travel_fare',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='transport_type',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='package_amount',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='proposed_package_amount',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='original_package_amount',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='margin_of_profit',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='package',
        ),

        # Add new fields to Transaction
        migrations.AddField(
            model_name='transaction',
            name='lead',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tour_management.lead', null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='booking_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled'), ('completed', 'Completed')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='transaction',
            name='payment_status',
            field=models.CharField(choices=[('unpaid', 'Unpaid'), ('partial', 'Partial'), ('paid', 'Paid'), ('refunded', 'Refunded')], default='unpaid', max_length=20),
        ),
        migrations.AddField(
            model_name='transaction',
            name='travel_start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='travel_end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='base_amount',
            field=models.DecimalField(decimal_places=2, max_digits=15, default=0.0),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='discount_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='taxes',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=15),
        ),
        migrations.AddField(
            model_name='transaction',
            name='final_amount',
            field=models.DecimalField(decimal_places=2, max_digits=15, default=0.0),
        ),
        migrations.AddField(
            model_name='transaction',
            name='amount_paid',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=15),
        ),
        migrations.AddField(
            model_name='transaction',
            name='amount_due',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=15),
        ),
        migrations.AddField(
            model_name='transaction',
            name='booking_notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='cancellation_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='confirmed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='cancelled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),

        # Create TransactionItineraryItem model
        migrations.CreateModel(
            name='TransactionItineraryItem',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('day', models.IntegerField()),
                ('title', models.CharField(blank=True, max_length=512, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('hotel_name', models.CharField(blank=True, max_length=255, null=True)),
                ('hotel_description', models.TextField(blank=True, null=True)),
                ('hotel_images', models.JSONField(blank=True, null=True)),
                ('car_dealer_name', models.CharField(blank=True, max_length=255, null=True)),
                ('car_type', models.CharField(blank=True, max_length=255, null=True)),
                ('activities', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='itinerary_items', to='tour_management.transaction')),
                ('selected_hotel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='tour_management.hotel')),
                ('selected_car_dealer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='tour_management.cardealer')),
            ],
            options={
                'db_table': 'TransactionItineraryItem',
                'unique_together': {('transaction', 'day')},
            },
        ),
    ]

