from __future__ import unicode_literals
from django.http import HttpResponse, JsonResponse
import json
from ..models import CompanyProfile, Touroperator, User, ImageMetadata
from django.core.exceptions import ValidationError
from django.db import IntegrityError


def get_profile_images(image_ids, include_binary=False):
    """
    Helper function to fetch image objects with URLs from image IDs.
    Returns list of image objects with id, description, order, and image_url.

    Handles both cases:
    - image_ids is a list of integers: [1, 2, 3]
    - image_ids is a list of dicts (corrupted data): [{'id': 1, ...}, ...]
    """
    if not image_ids:
        return []

    # Extract IDs if image_ids contains dictionaries (corrupted data)
    if isinstance(image_ids, list) and len(image_ids) > 0:
        if isinstance(image_ids[0], dict):
            # Already contains full objects, extract IDs
            image_ids = [img['id'] if isinstance(img, dict) else img for img in image_ids]

    images = ImageMetadata.objects.filter(id__in=image_ids).order_by('order')
    images_data = []

    for image in images:
        image_data = {
            "id": image.id,
            "description": image.description,
            "order": image.order,
            "image_url": image.image_path.url
        }

        # Include binary data if requested
        if include_binary:
            try:
                import base64
                with open(image.image_path.path, 'rb') as img_file:
                    image_data["image_binary"] = base64.b64encode(img_file.read()).decode('utf-8')
            except Exception as e:
                # If there's an error reading the file, continue without binary data
                image_data["image_binary_error"] = str(e)

        images_data.append(image_data)

    return images_data


def add_company_profile(request):
    """
    Create a company profile for a tour operator.
    Only one profile per tour operator is allowed.
    Required fields: tour_operator_id, company_name, created_by
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode("utf-8"))
            
            # Validate required fields
            required_fields = ["tour_operator_id", "company_name", "created_by"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({
                    "code": 400,
                    "message": f"Missing required fields: {', '.join(missing_fields)}"
                }, status=400)

            # Validate tour operator exists
            try:
                tour_operator = Touroperator.objects.get(id=data['tour_operator_id'])
            except Touroperator.DoesNotExist:
                return JsonResponse({
                    "code": 404,
                    "message": "Tour operator not found"
                }, status=404)

            # Validate user exists
            try:
                user = User.objects.get(id=data['created_by'])
            except User.DoesNotExist:
                return JsonResponse({
                    "code": 404,
                    "message": "User not found"
                }, status=404)

            # Check if profile already exists for this tour operator
            if CompanyProfile.objects.filter(tour_operator=tour_operator).exists():
                return JsonResponse({
                    "code": 409,
                    "message": "Company profile already exists for this tour operator. Use update API instead."
                }, status=409)

            # Create company profile
            profile = CompanyProfile.objects.create(
                tour_operator=tour_operator,
                company_name=data['company_name'],
                tagline=data.get('tagline'),
                description=data.get('description'),
                phone_number=data.get('phone_number'),
                alternate_phone=data.get('alternate_phone'),
                email=data.get('email'),
                website=data.get('website'),
                address_line1=data.get('address_line1'),
                address_line2=data.get('address_line2'),
                city=data.get('city'),
                state=data.get('state'),
                country=data.get('country'),
                pincode=data.get('pincode'),
                instagram_url=data.get('instagram_url'),
                facebook_url=data.get('facebook_url'),
                twitter_url=data.get('twitter_url'),
                linkedin_url=data.get('linkedin_url'),
                youtube_url=data.get('youtube_url'),
                registration_number=data.get('registration_number'),
                gst_number=data.get('gst_number'),
                established_year=data.get('established_year'),
                logo_image_ids=data.get('logo_image_ids', []),
                banner_image_ids=data.get('banner_image_ids', []),
                created_by=user
            )

            return JsonResponse({
                "code": 200,
                "message": "Company profile created successfully",
                "profile_id": profile.id
            }, status=201)

        except Exception as e:
            return JsonResponse({
                "code": 500,
                "message": f"Error creating company profile: {str(e)}"
            }, status=500)
    else:
        return JsonResponse({"code": 405, "message": "Method not allowed"}, status=405)


def get_company_profile(request):
    """
    Get company profile for a tour operator.
    Required field: tour_operator_id
    Optional field: include_binary (default: False)
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode("utf-8"))

            # Validate required field
            if 'tour_operator_id' not in data:
                return JsonResponse({
                    "code": 400,
                    "message": "Missing required field: tour_operator_id"
                }, status=400)

            # Get optional include_binary parameter
            include_binary = data.get("include_binary", False)

            # Get company profile
            try:
                profile = CompanyProfile.objects.get(tour_operator_id=data['tour_operator_id'])
            except CompanyProfile.DoesNotExist:
                return JsonResponse({
                    "code": 404,
                    "message": "Company profile not found for this tour operator"
                }, status=404)

            # Get image objects with URLs
            logo_images = get_profile_images(profile.logo_image_ids, include_binary)
            banner_images = get_profile_images(profile.banner_image_ids, include_binary)

            # Build response
            response_data = {
                "id": profile.id,
                "tour_operator_id": profile.tour_operator.id,
                "company_name": profile.company_name,
                "tagline": profile.tagline,
                "description": profile.description,
                "phone_number": profile.phone_number,
                "alternate_phone": profile.alternate_phone,
                "email": profile.email,
                "website": profile.website,
                "address": {
                    "line1": profile.address_line1,
                    "line2": profile.address_line2,
                    "city": profile.city,
                    "state": profile.state,
                    "country": profile.country,
                    "pincode": profile.pincode
                },
                "social_media": {
                    "instagram": profile.instagram_url,
                    "facebook": profile.facebook_url,
                    "twitter": profile.twitter_url,
                    "linkedin": profile.linkedin_url,
                    "youtube": profile.youtube_url
                },
                "business_info": {
                    "registration_number": profile.registration_number,
                    "gst_number": profile.gst_number,
                    "established_year": profile.established_year
                },
                "images": {
                    "logo": logo_images,
                    "banner": banner_images
                },
                "created_at": str(profile.created_at),
                "updated_at": str(profile.updated_at),
                "created_by": profile.created_by.id if profile.created_by else None,
                "updated_by": profile.updated_by.id if profile.updated_by else None
            }

            return JsonResponse({
                "code": 200,
                "data": response_data
            }, status=200)

        except Exception as e:
            return JsonResponse({
                "code": 500,
                "message": f"Error retrieving company profile: {str(e)}"
            }, status=500)
    else:
        return JsonResponse({"code": 405, "message": "Method not allowed"}, status=405)


def update_company_profile(request):
    """
    Update company profile for a tour operator.
    Only managers can update the profile.
    Required fields: tour_operator_id, updated_by
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode("utf-8"))

            # Validate required fields
            required_fields = ["tour_operator_id", "updated_by"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return JsonResponse({
                    "code": 400,
                    "message": f"Missing required fields: {', '.join(missing_fields)}"
                }, status=400)

            # Validate user exists and is a manager
            try:
                user = User.objects.get(id=data['updated_by'])
                if user.role != 'manager':
                    return JsonResponse({
                        "code": 403,
                        "message": "Only managers can update company profile"
                    }, status=403)
            except User.DoesNotExist:
                return JsonResponse({
                    "code": 404,
                    "message": "User not found"
                }, status=404)

            # Get company profile
            try:
                profile = CompanyProfile.objects.get(tour_operator_id=data['tour_operator_id'])
            except CompanyProfile.DoesNotExist:
                return JsonResponse({
                    "code": 404,
                    "message": "Company profile not found. Please create one first."
                }, status=404)

            # Update fields if provided
            if 'company_name' in data:
                profile.company_name = data['company_name']
            if 'tagline' in data:
                profile.tagline = data['tagline']
            if 'description' in data:
                profile.description = data['description']
            if 'phone_number' in data:
                profile.phone_number = data['phone_number']
            if 'alternate_phone' in data:
                profile.alternate_phone = data['alternate_phone']
            if 'email' in data:
                profile.email = data['email']
            if 'website' in data:
                profile.website = data['website']
            if 'address_line1' in data:
                profile.address_line1 = data['address_line1']
            if 'address_line2' in data:
                profile.address_line2 = data['address_line2']
            if 'city' in data:
                profile.city = data['city']
            if 'state' in data:
                profile.state = data['state']
            if 'country' in data:
                profile.country = data['country']
            if 'pincode' in data:
                profile.pincode = data['pincode']
            if 'instagram_url' in data:
                profile.instagram_url = data['instagram_url']
            if 'facebook_url' in data:
                profile.facebook_url = data['facebook_url']
            if 'twitter_url' in data:
                profile.twitter_url = data['twitter_url']
            if 'linkedin_url' in data:
                profile.linkedin_url = data['linkedin_url']
            if 'youtube_url' in data:
                profile.youtube_url = data['youtube_url']
            if 'registration_number' in data:
                profile.registration_number = data['registration_number']
            if 'gst_number' in data:
                profile.gst_number = data['gst_number']
            if 'established_year' in data:
                profile.established_year = data['established_year']
            if 'logo_image_ids' in data:
                profile.logo_image_ids = data['logo_image_ids']
            if 'banner_image_ids' in data:
                profile.banner_image_ids = data['banner_image_ids']

            profile.updated_by = user
            profile.save()

            return JsonResponse({
                "code": 200,
                "message": "Company profile updated successfully",
                "profile_id": profile.id
            }, status=200)

        except Exception as e:
            return JsonResponse({
                "code": 500,
                "message": f"Error updating company profile: {str(e)}"
            }, status=500)
    else:
        return JsonResponse({"code": 405, "message": "Method not allowed"}, status=405)

