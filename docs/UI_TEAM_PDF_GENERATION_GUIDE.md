# UI Team Guide: Lead PDF Generation

## Quick Start

This guide explains how to integrate the Lead PDF generation feature into your frontend application.

## API Endpoint

**URL:** `POST /lead/generate_pdf/`

**Purpose:** Generate a downloadable PDF proposal for a lead

## Request Format

```javascript
{
  "lead_id": 123,              // Required: The lead ID
  "lead_package_id": 456       // Optional: Specific package ID
}
```

## Response Format

### Success Response
```javascript
{
  "success": true,
  "pdf_url": "/media/pdfs/leads/lead_123_John_Doe.pdf",
  "filename": "lead_123_John_Doe.pdf",
  "message": "PDF generated successfully"
}
```

### Error Response
```javascript
{
  "success": false,
  "error": "Error message"
}
```

## Implementation Examples

### React Example

```jsx
import React, { useState } from 'react';

function GeneratePDFButton({ leadId }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGeneratePDF = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/lead/generate_pdf/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ lead_id: leadId })
      });

      const data = await response.json();

      if (data.success) {
        // Option 1: Open in new tab
        window.open(data.pdf_url, '_blank');

        // Option 2: Trigger download
        const link = document.createElement('a');
        link.href = data.pdf_url;
        link.download = data.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Failed to generate PDF');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button 
        onClick={handleGeneratePDF} 
        disabled={loading}
        className="btn btn-primary"
      >
        {loading ? 'Generating PDF...' : 'Download PDF Proposal'}
      </button>
      {error && <div className="error">{error}</div>}
    </div>
  );
}

export default GeneratePDFButton;
```

### Vue.js Example

```vue
<template>
  <div>
    <button 
      @click="generatePDF" 
      :disabled="loading"
      class="btn btn-primary"
    >
      {{ loading ? 'Generating PDF...' : 'Download PDF Proposal' }}
    </button>
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script>
export default {
  props: {
    leadId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      loading: false,
      error: null
    };
  },
  methods: {
    async generatePDF() {
      this.loading = true;
      this.error = null;

      try {
        const response = await fetch('/lead/generate_pdf/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ lead_id: this.leadId })
        });

        const data = await response.json();

        if (data.success) {
          // Open PDF in new tab
          window.open(data.pdf_url, '_blank');
        } else {
          this.error = data.error;
        }
      } catch (err) {
        this.error = 'Failed to generate PDF';
        console.error(err);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

### Vanilla JavaScript Example

```javascript
function generateLeadPDF(leadId) {
  const button = document.getElementById('generate-pdf-btn');
  const errorDiv = document.getElementById('pdf-error');
  
  // Show loading state
  button.disabled = true;
  button.textContent = 'Generating PDF...';
  errorDiv.textContent = '';

  fetch('/lead/generate_pdf/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ lead_id: leadId })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Open PDF in new window
      window.open(data.pdf_url, '_blank');
    } else {
      errorDiv.textContent = 'Error: ' + data.error;
    }
  })
  .catch(error => {
    errorDiv.textContent = 'Failed to generate PDF';
    console.error('Error:', error);
  })
  .finally(() => {
    button.disabled = false;
    button.textContent = 'Download PDF Proposal';
  });
}
```

## UI/UX Recommendations

### Button Placement

Add the "Generate PDF" button in the following locations:

1. **Lead Detail Page** - Primary action button
2. **Lead List Page** - Action menu for each lead
3. **Lead Edit Page** - After saving changes

### Button States

```css
/* Normal state */
.pdf-button {
  background-color: #3498db;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* Loading state */
.pdf-button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

/* Hover state */
.pdf-button:hover:not(:disabled) {
  background-color: #2980b9;
}
```

### Loading Indicator

Show a loading spinner or progress indicator while PDF is being generated:

```jsx
{loading && (
  <div className="loading-spinner">
    <i className="fas fa-spinner fa-spin"></i>
    Generating PDF...
  </div>
)}
```

### Success Feedback

After successful PDF generation:

```javascript
// Show success message
showNotification('PDF generated successfully!', 'success');

// Or use a toast notification
toast.success('PDF is ready for download');
```

### Error Handling

Display user-friendly error messages:

```javascript
const errorMessages = {
  'Lead with ID': 'Lead not found. Please refresh and try again.',
  'Failed to fetch': 'Unable to generate PDF. Please check your connection.',
  'default': 'An error occurred. Please try again later.'
};

function getErrorMessage(error) {
  for (let key in errorMessages) {
    if (error.includes(key)) {
      return errorMessages[key];
    }
  }
  return errorMessages.default;
}
```

## Best Practices

### 1. User Feedback
- Always show loading state during PDF generation
- Display clear success/error messages
- Provide option to retry on failure

### 2. Performance
- PDF generation takes 2-5 seconds
- Don't allow multiple simultaneous requests
- Consider caching PDF URLs if regenerating same lead

### 3. Accessibility
- Use semantic HTML for buttons
- Provide keyboard navigation
- Include ARIA labels for screen readers

```html
<button 
  aria-label="Generate PDF proposal for this lead"
  onClick={handleGeneratePDF}
>
  Download PDF
</button>
```

### 4. Mobile Considerations
- On mobile, PDFs may download instead of opening in new tab
- Provide clear indication that download has started
- Consider using native share API on mobile devices

```javascript
if (navigator.share && /mobile/i.test(navigator.userAgent)) {
  navigator.share({
    title: 'Tour Package Proposal',
    url: data.pdf_url
  });
} else {
  window.open(data.pdf_url, '_blank');
}
```

## Testing Checklist

- [ ] Button appears in correct locations
- [ ] Loading state displays correctly
- [ ] PDF opens in new tab/downloads
- [ ] Error messages display properly
- [ ] Works on desktop browsers (Chrome, Firefox, Safari, Edge)
- [ ] Works on mobile browsers (iOS Safari, Chrome Mobile)
- [ ] Keyboard navigation works
- [ ] Screen reader announces button purpose

## Common Issues

**Issue:** PDF doesn't open in new tab
- **Solution:** Check browser popup blocker settings

**Issue:** Download starts instead of preview
- **Solution:** This is browser-dependent behavior, both are acceptable

**Issue:** Button stays disabled after error
- **Solution:** Ensure loading state is reset in finally block

## Support

For technical issues or questions:
- Check the [full PDF generation documentation](./LEAD_PDF_GENERATION.md)
- Review API response for specific error messages
- Contact backend team for server-side issues
