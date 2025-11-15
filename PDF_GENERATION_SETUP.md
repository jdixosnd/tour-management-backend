# Lead PDF Generation - Setup Guide

## Overview

This guide will help you set up and test the Lead PDF Generation feature that was just implemented.

## What Was Implemented

✅ **WeasyPrint Integration** - Professional PDF generation from HTML templates  
✅ **PDF Generation API** - REST endpoint to generate PDFs for leads  
✅ **Professional Template** - Beautiful HTML template with company branding  
✅ **Automatic Storage** - PDFs saved to media directory with downloadable URLs  
✅ **Complete Documentation** - Full API docs and UI integration guides  

## Files Added/Modified

### New Files Created
```
tour_management/utils/__init__.py
tour_management/utils/pdf_generator.py
tour_management/templates/lead_pdf_template.html
tour_management/controllers/lead_pdf.py
docs/LEAD_PDF_GENERATION.md
docs/UI_TEAM_PDF_GENERATION_GUIDE.md
test_pdf_generation.sh
```

### Modified Files
```
requirements.txt                          # Added weasyprint
tour_management/urls.py                   # Added PDF generation route
tour_management_project/settings.py       # Updated TEMPLATES configuration
```

## Installation Steps

### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info
```

**macOS:**
```bash
brew install cairo pango gdk-pixbuf libffi
```

**Windows:**
- Download GTK+ runtime from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
- Install the runtime
- Add GTK bin directory to PATH

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install WeasyPrint and all its dependencies.

### 3. Verify Installation

```bash
python -c "import weasyprint; print('WeasyPrint version:', weasyprint.__version__)"
```

Expected output:
```
WeasyPrint version: 60.2 (or similar)
```

### 4. Create Media Directories

```bash
mkdir -p media/pdfs/leads
```

### 5. Run Migrations (if needed)

```bash
python manage.py migrate
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

## Testing the Implementation

### Option 1: Using the Test Script

```bash
./test_pdf_generation.sh
```

This will run automated tests against the API endpoint.

### Option 2: Manual Testing with cURL

```bash
# Generate PDF for lead ID 1
curl -X POST http://localhost:8000/lead/generate_pdf/ \
  -H "Content-Type: application/json" \
  -d '{"lead_id": 1}'
```

Expected response:
```json
{
  "success": true,
  "pdf_url": "/media/pdfs/leads/lead_1_Customer_Name.pdf",
  "filename": "lead_1_Customer_Name.pdf",
  "message": "PDF generated successfully"
}
```

### Option 3: Using Postman

1. Create a new POST request
2. URL: `http://localhost:8000/lead/generate_pdf/`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
   ```json
   {
     "lead_id": 1
   }
   ```
5. Send the request
6. Copy the `pdf_url` from response and open in browser

## Viewing Generated PDFs

Generated PDFs are stored in:
```
./media/pdfs/leads/
```

To view a PDF:
1. Get the `pdf_url` from the API response
2. Open in browser: `http://localhost:8000<pdf_url>`
3. Or navigate to the file directly in the media folder

## API Endpoint Details

**Endpoint:** `POST /lead/generate_pdf/`

**Request Body:**
```json
{
  "lead_id": 123,              // Required
  "lead_package_id": 456       // Optional
}
```

**Success Response:**
```json
{
  "success": true,
  "pdf_url": "/media/pdfs/leads/lead_123_John_Doe.pdf",
  "filename": "lead_123_John_Doe.pdf",
  "message": "PDF generated successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message"
}
```

## Customizing the PDF Template

The PDF template is located at:
```
tour_management/templates/lead_pdf_template.html
```

You can customize:
- **Styling:** Modify the CSS in the `<style>` section
- **Layout:** Change the HTML structure
- **Content:** Add or remove sections
- **Branding:** Update colors, fonts, logos

After making changes, restart the server and regenerate PDFs to see updates.

## Troubleshooting

### Issue: "WeasyPrint not found"
**Solution:** Install system dependencies first, then run `pip install weasyprint`

### Issue: "Template not found"
**Solution:** Verify `TEMPLATES` setting in `settings.py` includes:
```python
'DIRS': [os.path.join(BASE_DIR, 'tour_management', 'templates')]
```

### Issue: "Permission denied" when creating PDFs
**Solution:** Ensure media directory is writable:
```bash
chmod -R 755 media/
```

### Issue: Images not showing in PDF
**Solution:** 
- Ensure images have absolute URLs
- Check that MEDIA_URL is properly configured
- Verify image files exist and are accessible

### Issue: PDF generation is slow
**Solution:**
- Optimize image sizes
- Simplify CSS
- Consider implementing async generation for production

## Next Steps

1. **Test with Real Data:** Create a lead with complete information and generate PDF
2. **Customize Template:** Modify the template to match your branding
3. **Integrate with Frontend:** Use the UI team guide to add PDF generation buttons
4. **Set Up Company Profile:** Add company logo and branding for better PDFs
5. **Production Setup:** Consider async generation and cleanup jobs

## Documentation

- **Full API Documentation:** `docs/LEAD_PDF_GENERATION.md`
- **UI Integration Guide:** `docs/UI_TEAM_PDF_GENERATION_GUIDE.md`
- **Company Profile Setup:** `docs/company_profile_api.md`

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the full documentation in `docs/`
3. Check Django logs for detailed error messages
4. Verify WeasyPrint installation: `python -c "import weasyprint"`

## Production Considerations

Before deploying to production:

- [ ] Install WeasyPrint system dependencies on production server
- [ ] Configure proper media file storage (S3, CDN, etc.)
- [ ] Set up PDF cleanup job to remove old files
- [ ] Consider implementing async PDF generation (Celery)
- [ ] Add rate limiting to prevent abuse
- [ ] Set up monitoring for PDF generation failures
- [ ] Configure proper permissions for media directory
- [ ] Test PDF generation under load

## Summary

The Lead PDF Generation feature is now ready to use! You can:

1. Generate professional PDF proposals for leads
2. Include company branding and contact information
3. Provide downloadable PDFs to customers
4. Customize the template to match your needs

Start by testing with the provided test script, then integrate into your frontend application using the UI team guide.
