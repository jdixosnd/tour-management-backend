#!/bin/bash

# Test script for Lead PDF Generation API
# This script tests the PDF generation endpoint with sample data

echo "=========================================="
echo "Lead PDF Generation API Test"
echo "=========================================="
echo ""

# Configuration
BASE_URL="http://localhost:8000"
ENDPOINT="/lead/generate_pdf/"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Generate PDF for a valid lead
echo -e "${YELLOW}Test 1: Generate PDF for Lead ID 1${NC}"
echo "Request:"
echo '{"lead_id": 1}'
echo ""

RESPONSE=$(curl -s -X POST "${BASE_URL}${ENDPOINT}" \
  -H "Content-Type: application/json" \
  -d '{"lead_id": 1}')

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Check if successful
if echo "$RESPONSE" | grep -q '"success": true'; then
    echo -e "${GREEN}✓ Test 1 PASSED${NC}"
    PDF_URL=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['pdf_url'])" 2>/dev/null)
    if [ ! -z "$PDF_URL" ]; then
        echo -e "PDF URL: ${GREEN}${PDF_URL}${NC}"
    fi
else
    echo -e "${RED}✗ Test 1 FAILED${NC}"
fi

echo ""
echo "=========================================="
echo ""

# Test 2: Test with missing lead_id
echo -e "${YELLOW}Test 2: Test with missing lead_id (should fail)${NC}"
echo "Request:"
echo '{}'
echo ""

RESPONSE=$(curl -s -X POST "${BASE_URL}${ENDPOINT}" \
  -H "Content-Type: application/json" \
  -d '{}')

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Check if it properly returns error
if echo "$RESPONSE" | grep -q '"success": false'; then
    echo -e "${GREEN}✓ Test 2 PASSED (Error handled correctly)${NC}"
else
    echo -e "${RED}✗ Test 2 FAILED${NC}"
fi

echo ""
echo "=========================================="
echo ""

# Test 3: Test with non-existent lead
echo -e "${YELLOW}Test 3: Test with non-existent lead ID (should fail)${NC}"
echo "Request:"
echo '{"lead_id": 99999}'
echo ""

RESPONSE=$(curl -s -X POST "${BASE_URL}${ENDPOINT}" \
  -H "Content-Type: application/json" \
  -d '{"lead_id": 99999}')

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Check if it properly returns error
if echo "$RESPONSE" | grep -q '"success": false'; then
    echo -e "${GREEN}✓ Test 3 PASSED (Error handled correctly)${NC}"
else
    echo -e "${RED}✗ Test 3 FAILED${NC}"
fi

echo ""
echo "=========================================="
echo ""

# Test 4: Test with specific package ID
echo -e "${YELLOW}Test 4: Generate PDF with specific package ID${NC}"
echo "Request:"
echo '{"lead_id": 1, "lead_package_id": 1}'
echo ""

RESPONSE=$(curl -s -X POST "${BASE_URL}${ENDPOINT}" \
  -H "Content-Type: application/json" \
  -d '{"lead_id": 1, "lead_package_id": 1}')

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Check if successful
if echo "$RESPONSE" | grep -q '"success": true'; then
    echo -e "${GREEN}✓ Test 4 PASSED${NC}"
else
    echo -e "${RED}✗ Test 4 FAILED${NC}"
fi

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
echo "All tests completed!"
echo ""
echo "Note: For Test 1 and Test 4 to pass, you need:"
echo "  1. A lead with ID 1 in the database"
echo "  2. WeasyPrint properly installed"
echo "  3. Django server running on localhost:8000"
echo ""
echo "To view generated PDFs, check:"
echo "  ./media/pdfs/leads/"
echo ""

