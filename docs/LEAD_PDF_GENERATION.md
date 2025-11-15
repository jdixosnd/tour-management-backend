# Lead PDF Generation API

## Overview

The Lead PDF Generation feature allows you to generate professional PDF documents for leads that include all necessary details such as customer information, package details, itinerary, hotels, transportation options, and company branding.

The system uses **WeasyPrint** to convert HTML templates into high-quality PDF documents.

## Features

- ✅ Professional PDF layout with company branding (logo, banner)
- ✅ Complete customer information
- ✅ Detailed package overview with pricing
- ✅ Day-wise itinerary with hotels, transportation, and activities
- ✅ Package inclusions and exclusions
- ✅ Terms and conditions
- ✅ Company contact information in footer
- ✅ Automatic PDF storage in media directory
- ✅ Downloadable URL returned in API response

## Installation

### 1. Install WeasyPrint

The `weasyprint` package has been added to `requirements.txt`. Install it using:

```bash
pip install -r requirements.txt
```

**Note:** WeasyPrint requires some system dependencies. On Ubuntu/Debian:

```bash
sudo apt-get install python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

On macOS:

```bash
brew install cairo pango gdk-pixbuf libffi
```

## API Endpoint

### Generate Lead PDF

**Endpoint:** `POST /lead/generate_pdf/`

**Description:** Generates a PDF document for a specific lead and returns the download URL.

### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "lead_id": 123,
  "lead_package_id": 456  // Optional
}
```

**Parameters:**
- `lead_id` (required): The ID of the lead for which to generate the PDF
- `lead_package_id` (optional): Specific package ID. If not provided, the first package of the lead will be used

### Response

**Success Response (200 OK):**
```json
{
  "success": true,
  "pdf_url": "/media/pdfs/leads/lead_123_John_Doe.pdf",
  "filename": "lead_123_John_Doe.pdf",
  "message": "PDF generated successfully"
}
```

**Error Response (400/404/500):**
```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

## Usage Examples

### Example 1: Generate PDF for a Lead

```bash
curl -X POST http://localhost:8000/lead/generate_pdf/ \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": 123
  }'
```

### Example 2: Generate PDF with Specific Package

```bash
curl -X POST http://localhost:8000/lead/generate_pdf/ \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": 123,
    "lead_package_id": 456
  }'
```

### Example 3: Using JavaScript/Fetch

```javascript
fetch('http://localhost:8000/lead/generate_pdf/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    lead_id: 123
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('PDF URL:', data.pdf_url);
    // You can now provide a download link to the user
    window.open(data.pdf_url, '_blank');
  } else {
    console.error('Error:', data.error);
  }
});
```

## PDF Content Structure

The generated PDF includes the following sections:

1. **Header**
   - Company logo (if available)
   - Company name and tagline
   
2. **Proposal Information**
   - Proposal ID (Lead ID)
   - Date and time of generation
   - Lead status

3. **Customer Information**
   - Name, phone, email, address

4. **Package Overview**
   - Package name and description
   - Package type, duration, group size
   - Transport type
   - Total package price

5. **Detailed Itinerary**
   - Day-wise breakdown
   - Day title and description
   - Accommodation options (hotels)
   - Transportation options
   - Activities and sightseeing

6. **Inclusions & Exclusions**
   - What's included in the package
   - What's excluded from the package

7. **Terms & Conditions**
   - Package terms and conditions

8. **Footer**
   - Company contact information
   - Address, phone, email, website

## File Storage

Generated PDFs are stored in the following location:

```
<MEDIA_ROOT>/pdfs/leads/
```

**Filename Format:**
```
lead_<lead_id>_<customer_name>.pdf
```

Example: `lead_123_John_Doe.pdf`

The PDF files are accessible via the media URL:
```
<MEDIA_URL>/pdfs/leads/<filename>
```

## Integration with Company Profile

The PDF generation automatically fetches the company profile for the tour operator to include:

- Company logo
- Company name and tagline
- Contact information (phone, email, website)
- Address details

If no company profile exists, the PDF will still be generated without the branding elements.

## Customization

### Modifying the PDF Template

The PDF template is located at:
```
tour_management/templates/lead_pdf_template.html
```

You can customize:
- Layout and styling (CSS in the `<style>` section)
- Content structure
- Colors, fonts, and spacing
- Additional sections or information

### Styling Guidelines

The template uses inline CSS and supports most CSS properties that are compatible with WeasyPrint. Some limitations:

- No JavaScript
- Limited CSS3 support
- Use absolute units (pt, cm, mm) for print-specific styling
- Use `@page` rules for page-specific settings

## Error Handling

The API handles various error scenarios:

| Error | Status Code | Description |
|-------|-------------|-------------|
| Missing lead_id | 400 | Required field not provided |
| Lead not found | 404 | Lead with specified ID doesn't exist |
| PDF generation failed | 500 | Error during PDF creation |
| Template rendering error | 500 | Error in HTML template |

## Performance Considerations

- PDF generation is synchronous and may take 2-5 seconds depending on content size
- For large itineraries (10+ days), consider implementing async generation
- Generated PDFs are cached on disk and can be reused
- Consider implementing a cleanup job to remove old PDFs

## Workflow Integration

### Typical User Flow

1. User creates a lead with package details
2. User reviews the lead information
3. User clicks "Generate PDF" button
4. Frontend calls the PDF generation API
5. API returns PDF URL
6. User can download or share the PDF with customer

### Example Frontend Implementation

```javascript
// Button click handler
async function generateLeadPDF(leadId) {
  try {
    // Show loading indicator
    showLoading();

    const response = await fetch('/lead/generate_pdf/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ lead_id: leadId })
    });

    const data = await response.json();

    if (data.success) {
      // Open PDF in new tab or trigger download
      window.open(data.pdf_url, '_blank');

      // Or trigger download
      const link = document.createElement('a');
      link.href = data.pdf_url;
      link.download = data.filename;
      link.click();
    } else {
      alert('Error generating PDF: ' + data.error);
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Failed to generate PDF');
  } finally {
    hideLoading();
  }
}
```

## Testing

### Manual Testing

1. Create a lead with complete information
2. Call the PDF generation API
3. Verify the PDF is generated and accessible
4. Check PDF content for accuracy
5. Test with and without company profile

### Sample Test Request

```bash
# Test with a valid lead
curl -X POST http://localhost:8000/lead/generate_pdf/ \
  -H "Content-Type: application/json" \
  -d '{"lead_id": 1}'

# Expected response
{
  "success": true,
  "pdf_url": "/media/pdfs/leads/lead_1_Customer_Name.pdf",
  "filename": "lead_1_Customer_Name.pdf",
  "message": "PDF generated successfully"
}
```

## Troubleshooting

### Common Issues

**1. WeasyPrint installation fails**
- Ensure system dependencies are installed (cairo, pango, etc.)
- Check Python version compatibility (Python 3.6+)

**2. Template not found error**
- Verify `TEMPLATES` setting in `settings.py` includes the templates directory
- Check file path: `tour_management/templates/lead_pdf_template.html`

**3. Images not showing in PDF**
- Ensure image URLs are absolute, not relative
- Check that `MEDIA_URL` is properly configured
- Verify image files exist and are accessible

**4. PDF generation is slow**
- Large images can slow down generation - optimize image sizes
- Complex CSS can impact performance - simplify where possible

**5. Fonts not rendering correctly**
- WeasyPrint uses system fonts
- Ensure required fonts are installed on the server
- Use web-safe fonts for better compatibility

## Future Enhancements

Potential improvements for the PDF generation feature:

- [ ] Async PDF generation with task queue (Celery)
- [ ] Email PDF directly to customer
- [ ] Multiple template options (modern, classic, minimal)
- [ ] Watermark support for draft proposals
- [ ] Digital signature integration
- [ ] Multi-language support
- [ ] PDF compression for smaller file sizes
- [ ] Batch PDF generation for multiple leads

## Support

For issues or questions regarding PDF generation:

1. Check this documentation
2. Review the error message in the API response
3. Check Django logs for detailed error information
4. Verify WeasyPrint installation and dependencies

## Related Documentation

- [Lead API Documentation](./booking_api_reference.md)
- [Company Profile API](./company_profile_api.md)
- [Image Handling Guide](./UI_TEAM_IMAGE_HANDLING_GUIDE.md)

