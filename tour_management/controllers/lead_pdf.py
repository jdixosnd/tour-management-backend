"""
Lead PDF Generation Controller
Handles API endpoints for generating PDF documents from lead data
"""
from __future__ import unicode_literals
import json
from django.http import JsonResponse
from ..models import Lead, LeadPackage, CompanyProfile
from ..utils.pdf_generator import generate_lead_pdf
from .lead import get_lead
from .company_profile import get_company_profile


def generate_lead_pdf_api(request):
    """
    Generate a PDF for a lead and return the download URL.
    
    Request body (POST):
    {
        "lead_id": 123,
        "lead_package_id": 456  // Optional, if not provided will use first package of lead
    }
    
    Response:
    {
        "success": true,
        "pdf_url": "/media/pdfs/leads/lead_123_customer_name.pdf",
        "filename": "lead_123_customer_name.pdf",
        "message": "PDF generated successfully"
    }
    
    Or on error:
    {
        "success": false,
        "error": "Error message"
    }
    """
    if request.method != 'POST':
        return JsonResponse({
            "success": False,
            "error": "Method not allowed. Use POST."
        }, status=405)
    
    try:
        # Parse request data
        data = json.loads(request.body.decode("utf-8"))
        
        # Validate required fields
        if 'lead_id' not in data:
            return JsonResponse({
                "success": False,
                "error": "Missing required field: lead_id"
            }, status=400)
        
        lead_id = data.get('lead_id')
        lead_package_id = data.get('lead_package_id')
        
        # Fetch lead data using existing get_lead function
        # Create a mock request object to pass to get_lead
        from django.http import HttpRequest
        mock_request = HttpRequest()
        mock_request.method = 'POST'
        mock_request._body = json.dumps({
            'lead_id': lead_id,
            'lead_package_id': lead_package_id
        }).encode('utf-8')
        
        # Get lead data
        lead_response = get_lead(mock_request)
        
        if lead_response.status_code != 200:
            return JsonResponse({
                "success": False,
                "error": "Failed to fetch lead data"
            }, status=lead_response.status_code)
        
        lead_data = json.loads(lead_response.content.decode('utf-8'))

        # Split customer name into first and last name
        if 'customer' in lead_data and lead_data['customer'] and 'name' in lead_data['customer']:
            customer_name = lead_data['customer']['name']
            name_parts = customer_name.split(' ', 1) if customer_name else ['', '']
            lead_data['customer']['first_name'] = name_parts[0] if len(name_parts) > 0 else ''
            lead_data['customer']['last_name'] = name_parts[1] if len(name_parts) > 1 else ''

        # Get lead object for additional details
        lead_obj = Lead.objects.select_related('created_by', 'tour_operator').get(uuid=lead_id)

        # Add created_by user information to lead_data
        created_by_data = None
        if lead_obj.created_by:
            # Split name into first and last name
            name_parts = lead_obj.created_by.name.split(' ', 1) if lead_obj.created_by.name else ['', '']
            first_name = name_parts[0] if len(name_parts) > 0 else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            created_by_data = {
                'id': lead_obj.created_by.id,
                'name': lead_obj.created_by.name,
                'first_name': first_name,
                'last_name': last_name,
                'username': lead_obj.created_by.username,
                'email': lead_obj.created_by.email,
                'mobileno': lead_obj.created_by.mobileno
            }

        # Get company profile data for branding
        company_profile_data = None
        try:
            tour_operator_id = str(lead_obj.tour_operator.uuid)

            # Fetch company profile
            mock_profile_request = HttpRequest()
            mock_profile_request.method = 'POST'
            mock_profile_request._body = json.dumps({
                'tour_operator_id': tour_operator_id
            }).encode('utf-8')

            profile_response = get_company_profile(mock_profile_request)

            if profile_response.status_code == 200:
                profile_json = json.loads(profile_response.content.decode('utf-8'))
                company_profile_data = profile_json.get('data', {})
        except Exception as e:
            # If company profile fetch fails, continue without it
            print(f"Warning: Could not fetch company profile: {str(e)}")
            company_profile_data = None

        # Generate PDF with created_by information
        pdf_result = generate_lead_pdf(lead_data, company_profile_data, created_by_data)
        
        if pdf_result.get('success'):
            return JsonResponse({
                "success": True,
                "pdf_url": pdf_result.get('pdf_url'),
                "filename": pdf_result.get('filename'),
                "message": "PDF generated successfully"
            }, status=200)
        else:
            return JsonResponse({
                "success": False,
                "error": pdf_result.get('error', 'Unknown error occurred')
            }, status=500)
    
    except Lead.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": f"Lead with ID {lead_id} not found"
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": f"Error generating PDF: {str(e)}"
        }, status=500)

