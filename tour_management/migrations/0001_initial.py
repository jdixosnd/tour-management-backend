# Generated by Django 3.0.7 on 2024-10-16 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cardealer',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('contact_info', models.CharField(blank=True, max_length=255, null=True)),
                ('car_types', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'CarDealer',
                
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=45, null=True)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('email', models.CharField(blank=True, max_length=45, null=True)),
            ],
            options={
                'db_table': 'Customer',
                
            },
        ),
        migrations.CreateModel(
            name='Destination',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('location_id', models.BigIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Destination',
                
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('contact_info', models.CharField(blank=True, max_length=255, null=True)),
                ('charges', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Event',
                
            },
        ),
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('ratings', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('website', models.CharField(blank=True, max_length=45, null=True)),
            ],
            options={
                'db_table': 'Hotel',
                
            },
        ),
        migrations.CreateModel(
            name='Itineraryitem',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('item_type', models.CharField(blank=True, max_length=50, null=True)),
                ('item_id', models.BigIntegerField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'ItineraryItem',
                
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('city', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=255)),
                ('country', models.CharField(max_length=255)),
                ('country_code', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('lng', models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True)),
                ('lat', models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Location',
                
            },
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('pax_size', models.IntegerField(blank=True, null=True)),
                ('contains_travel_fare', models.IntegerField(blank=True, null=True)),
                ('transport_type', models.CharField(blank=True, max_length=45, null=True)),
                ('package_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
            ],
            options={
                'db_table': 'Package',
                
            },
        ),
        migrations.CreateModel(
            name='Packageitineraryitem',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('active', models.IntegerField(blank=True, null=True)),
                ('is_default', models.IntegerField(blank=True, null=True)),
                ('day', models.IntegerField(blank=True, null=True)),
                ('sequence', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'packageItineraryItem',
                
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('rating', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('price_per_night', models.CharField(blank=True, max_length=45, null=True)),
            ],
            options={
                'db_table': 'Room',
                
            },
        ),
        migrations.CreateModel(
            name='Touroperator',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255, unique=True)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('max_users', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('account_life_months', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'TourOperator',
                
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('package_name', models.CharField(blank=True, max_length=250, null=True)),
                ('package_description', models.TextField(blank=True, null=True)),
                ('pax_size', models.IntegerField(blank=True, null=True)),
                ('package_amount', models.IntegerField(blank=True, null=True)),
                ('contains_travel_fare', models.IntegerField(blank=True, null=True)),
                ('transport_type', models.CharField(blank=True, max_length=100, null=True)),
                ('documentid', models.CharField(blank=True, db_column='documentID', max_length=45, null=True)),
            ],
            options={
                'db_table': 'Transaction',
                
            },
        ),
        migrations.CreateModel(
            name='TransactionItinerary',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=250, null=True)),
                ('type', models.CharField(blank=True, max_length=250, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('hotel_price_per_night', models.IntegerField(blank=True, null=True)),
                ('hotel_description', models.TextField(blank=True, null=True)),
                ('no_of_days', models.IntegerField(blank=True, null=True)),
                ('event_contact_info', models.CharField(blank=True, max_length=15, null=True)),
                ('event_charges', models.IntegerField(blank=True, null=True)),
                ('car_dealer_contact_info', models.CharField(blank=True, max_length=15, null=True)),
                ('car_type', models.CharField(blank=True, max_length=50, null=True)),
                ('default_amount', models.IntegerField(blank=True, null=True)),
                ('offered_amount', models.IntegerField(blank=True, null=True)),
                ('sequence', models.IntegerField(blank=True, null=True)),
                ('day', models.CharField(blank=True, max_length=45, null=True)),
            ],
            options={
                'db_table': 'Transaction_itinerary',
                
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255, unique=True)),
                ('password_hash', models.CharField(max_length=255)),
                ('role', models.CharField(blank=True, max_length=50, null=True)),
                ('is_active', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('mobileno', models.CharField(blank=True, max_length=12, null=True)),
                ('username', models.CharField(blank=True, max_length=45, null=True)),
            ],
            options={
                'db_table': 'User',
                
            },
        ),
    ]