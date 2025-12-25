# Generated manually for CompanyProfile model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tour_management', '0008_auto_20251113_1631'),
    ]

    operations = [
        # Add max_images_company_profile to TourOperatorQuota
        migrations.AddField(
            model_name='touroperatorquota',
            name='max_images_company_profile',
            field=models.PositiveIntegerField(default=5),
        ),
        
        # Create CompanyProfile model
        migrations.CreateModel(
            name='CompanyProfile',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('company_name', models.CharField(max_length=255)),
                ('tagline', models.CharField(blank=True, max_length=500, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('alternate_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=255, null=True)),
                ('website', models.URLField(blank=True, max_length=500, null=True)),
                ('address_line1', models.CharField(blank=True, max_length=255, null=True)),
                ('address_line2', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('pincode', models.CharField(blank=True, max_length=20, null=True)),
                ('instagram_url', models.URLField(blank=True, max_length=500, null=True)),
                ('facebook_url', models.URLField(blank=True, max_length=500, null=True)),
                ('twitter_url', models.URLField(blank=True, max_length=500, null=True)),
                ('linkedin_url', models.URLField(blank=True, max_length=500, null=True)),
                ('youtube_url', models.URLField(blank=True, max_length=500, null=True)),
                ('registration_number', models.CharField(blank=True, max_length=100, null=True)),
                ('gst_number', models.CharField(blank=True, max_length=50, null=True)),
                ('established_year', models.PositiveIntegerField(blank=True, null=True)),
                ('logo_image_ids', models.JSONField(blank=True, null=True)),
                ('banner_image_ids', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_profiles', to='tour_management.user')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_profiles', to='tour_management.user')),
                ('tour_operator', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='company_profile', to='tour_management.touroperator')),
            ],
            options={
                'db_table': 'CompanyProfile',
            },
        ),
    ]

