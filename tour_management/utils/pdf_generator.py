"""
PDF Generation Utility for Tour Management
Uses WeasyPrint to generate PDFs from HTML templates
"""
import os
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
try:
    from weasyprint import HTML
except OSError:
    HTML = None

import uuid


def generate_pdf_from_html(html_content, filename=None):
    """
    Generate a PDF file from HTML content and save it to media directory.
    
    Args:
        html_content (str): HTML content to convert to PDF
        filename (str, optional): Custom filename for the PDF. If not provided, generates a unique name.
    
    Returns:
        dict: Dictionary containing 'success', 'pdf_path', 'pdf_url', and optional 'error' keys
    """
    try:
        # Create PDFs directory if it doesn't exist
        pdf_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs', 'leads')
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            filename = f'lead_{timestamp}_{unique_id}.pdf'
        
        # Ensure filename ends with .pdf
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        # Full path to save the PDF
        pdf_path = os.path.join(pdf_dir, filename)
        
        # Generate PDF from HTML
        # Use BASE_DIR as base_url so WeasyPrint can resolve file:// URLs for local media files
        HTML(string=html_content, base_url=settings.BASE_DIR).write_pdf(pdf_path)
        
        # Generate URL for the PDF
        pdf_url = os.path.join(settings.MEDIA_URL, 'pdfs', 'leads', filename)
        
        return {
            'success': True,
            'pdf_path': pdf_path,
            'pdf_url': pdf_url,
            'filename': filename
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def render_lead_pdf_template(context_data):
    """
    Render the lead PDF template with provided context data.
    
    Args:
        context_data (dict): Context data for the template including:
            - lead: Lead object data
            - customer: Customer information
            - package: Package details
            - itinerary: Day-wise itinerary details
            - company_profile: Company branding information
    
    Returns:
        str: Rendered HTML content
    """
    try:
        html_content = render_to_string('lead_pdf_template.html', context_data)
        return html_content
    except Exception as e:
        raise Exception(f"Error rendering template: {str(e)}")


def convert_image_urls_to_absolute(data, media_root):
    """
    Recursively convert relative image URLs to absolute file paths for WeasyPrint.

    Args:
        data: Dictionary or list containing image URLs
        media_root: Base path for media files

    Returns:
        Modified data with absolute file paths
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'image_url' and isinstance(value, str) and value.startswith('/media/'):
                # Convert /media/path/to/image.jpg to file:///absolute/path/media/path/to/image.jpg
                relative_path = value.replace('/media/', '')
                absolute_path = os.path.join(media_root, relative_path)
                data[key] = f'file://{absolute_path}'
            elif isinstance(value, (dict, list)):
                convert_image_urls_to_absolute(value, media_root)
    elif isinstance(data, list):
        for item in data:
            convert_image_urls_to_absolute(item, media_root)
    return data


def generate_lead_pdf(lead_data, company_profile_data=None, created_by_data=None):
    """
    Generate a PDF for a lead with ALL available details.

    Args:
        lead_data (dict): Complete lead data including customer, package, itinerary with:
            - lead_id, status, created_at
            - customer: id, name, email, mobileno, company, address
            - package: id, name, description, type, pax_size, no_of_days, package_amount,
                      contains_travel_fare, transport_type, terms_and_conditions, notes
            - package.images: array of image objects
            - package.inclusions: array of inclusion objects
            - package.exclusions: array of exclusion objects
            - package.amenities: array of amenity objects
            - package.policies: array of policy objects
            - package.itinerary_details: array of day objects with:
                - day, city, state, title, description, note
                - hotel_details: array of hotel objects with rooms, images, location
                - car_dealers: array of car dealer objects
                - activities: array of activity objects with images
        company_profile_data (dict, optional): Company profile data for branding with:
            - company_name, phone_number, alternate_phone, email, website
            - address: line1, line2, city, state, country, pincode
            - images.logo: array of logo images
            - images.banner: array of banner images
        created_by_data (dict, optional): User information who created the lead with:
            - id, name, first_name, last_name, username, email, mobileno

    Returns:
        dict: Result dictionary with success status, PDF URL, or error message
    """
    try:
        # Convert all image URLs to absolute file paths for WeasyPrint
        lead_data = convert_image_urls_to_absolute(lead_data, settings.MEDIA_ROOT)
        if company_profile_data:
            company_profile_data = convert_image_urls_to_absolute(company_profile_data, settings.MEDIA_ROOT)

        # Extract package data with all fields
        package_data = lead_data.get('package', {})

        # Prepare comprehensive context for template with ALL available data
        context = {
            # Lead basic info
            'lead': {
                'lead_id': lead_data.get('lead_id'),
                'status': lead_data.get('status'),
                'created_at': lead_data.get('created_at'),
            },

            # Customer complete info
            'customer': lead_data.get('customer', {}),

            # Package complete info with ALL fields
            'package': {
                # Basic package info
                'id': package_data.get('id'),
                'name': package_data.get('name'),
                'description': package_data.get('description'),
                'type': package_data.get('type'),
                'pax_size': package_data.get('pax_size'),
                'no_of_days': package_data.get('no_of_days'),
                'package_amount': package_data.get('package_amount'),
                'contains_travel_fare': package_data.get('contains_travel_fare'),
                'transport_type': package_data.get('transport_type'),
                'destination_id': package_data.get('destination_id'),
                'notes': package_data.get('notes'),

                # Terms and conditions - CRITICAL for PDF
                'terms_and_conditions': package_data.get('terms_and_conditions'),

                # Package images - ALL images
                'images': package_data.get('images', []),

                # Inclusions - ALL inclusions with details
                'inclusions': package_data.get('inclusions', []),

                # Exclusions - ALL exclusions with details
                'exclusions': package_data.get('exclusions', []),

                # Amenities - ALL amenities with details
                'amenities': package_data.get('amenities', []),

                # Policies - ALL policies with details
                'policies': package_data.get('policies', []),

                # Itinerary - COMPLETE day-wise details with hotels, rooms, activities, transportation
                'itinerary_details': package_data.get('itinerary_details', []),
            },

            # Company profile complete info
            'company_profile': company_profile_data or {},

            # Created by user info
            'created_by': created_by_data,

            # Metadata
            'generated_date': datetime.now().strftime('%B %d, %Y'),
            'generated_time': datetime.now().strftime('%I:%M %p'),
            'base_dir': settings.BASE_DIR
        }

        # Render HTML template
        html_content = render_lead_pdf_template(context)

        # Generate PDF filename
        lead_id = lead_data.get('lead_id', 'unknown')
        customer_name = lead_data.get('customer', {}).get('name', 'customer')
        # Sanitize customer name for filename
        safe_customer_name = "".join(c for c in customer_name if c.isalnum() or c in (' ', '_')).rstrip()
        safe_customer_name = safe_customer_name.replace(' ', '_')

        filename = f'lead_{lead_id}_{safe_customer_name}.pdf'

        # Generate PDF
        result = generate_pdf_from_html(html_content, filename)

        return result

    except Exception as e:
        return {
            'success': False,
            'error': f"Error generating lead PDF: {str(e)}"
        }

