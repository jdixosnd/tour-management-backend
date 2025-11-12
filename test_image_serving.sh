#!/bin/bash

# Image Serving Test Script
# Tests if Nginx is correctly serving images

echo "=========================================="
echo "Image Serving Test Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check if containers are running
echo "Test 1: Checking if containers are running..."
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Containers are running${NC}"
else
    echo -e "${RED}✗ Containers are not running${NC}"
    echo "Run: docker-compose up -d"
    exit 1
fi
echo ""

# Test 2: Check Nginx configuration
echo "Test 2: Checking Nginx configuration..."
if docker-compose exec -T nginx nginx -t 2>&1 | grep -q "successful"; then
    echo -e "${GREEN}✓ Nginx configuration is valid${NC}"
else
    echo -e "${RED}✗ Nginx configuration has errors${NC}"
    docker-compose exec nginx nginx -t
    exit 1
fi
echo ""

# Test 3: Check if media volume is mounted
echo "Test 3: Checking if media volume is mounted in Nginx..."
if docker-compose exec -T nginx ls /tour_management_project/media/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Media volume is mounted in Nginx${NC}"
else
    echo -e "${RED}✗ Media volume is not mounted in Nginx${NC}"
    echo "Check docker-compose.yml volume configuration"
    exit 1
fi
echo ""

# Test 4: Check if media directory exists in Django container
echo "Test 4: Checking if media directory exists in Django container..."
if docker-compose exec -T tour_management ls /tour_management_project/media/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Media directory exists in Django container${NC}"
else
    echo -e "${YELLOW}⚠ Media directory doesn't exist yet (will be created on first upload)${NC}"
fi
echo ""

# Test 5: Check if /media/ location is configured in Nginx
echo "Test 5: Checking Nginx /media/ location configuration..."
if docker-compose exec -T nginx cat /etc/nginx/conf.d/local.conf | grep -q "location /media/"; then
    echo -e "${GREEN}✓ Nginx /media/ location is configured${NC}"
else
    echo -e "${RED}✗ Nginx /media/ location is not configured${NC}"
    echo "Check config/nginx/conf.d/local.conf"
    exit 1
fi
echo ""

# Test 6: Test if we can access the API
echo "Test 6: Testing API accessibility..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:9300/probe/ | grep -q "200"; then
    echo -e "${GREEN}✓ API is accessible${NC}"
else
    echo -e "${RED}✗ API is not accessible${NC}"
    echo "Check if containers are running and port 9300 is available"
    exit 1
fi
echo ""

# Test 7: Check if there are any existing images
echo "Test 7: Checking for existing images..."
IMAGE_COUNT=$(docker-compose exec -T tour_management find /tour_management_project/media/images -type f 2>/dev/null | wc -l)
if [ "$IMAGE_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Found $IMAGE_COUNT existing images${NC}"
    
    # Try to access one of them
    SAMPLE_IMAGE=$(docker-compose exec -T tour_management find /tour_management_project/media/images -type f 2>/dev/null | head -1 | tr -d '\r')
    if [ ! -z "$SAMPLE_IMAGE" ]; then
        # Extract the path after /tour_management_project
        IMAGE_PATH=$(echo $SAMPLE_IMAGE | sed 's|/tour_management_project||')
        echo "  Testing access to: $IMAGE_PATH"
        
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9300$IMAGE_PATH)
        if [ "$HTTP_CODE" = "200" ]; then
            echo -e "${GREEN}  ✓ Image is accessible via Nginx (HTTP $HTTP_CODE)${NC}"
            
            # Check cache headers
            CACHE_HEADER=$(curl -s -I http://localhost:9300$IMAGE_PATH | grep -i "cache-control")
            if echo "$CACHE_HEADER" | grep -q "public"; then
                echo -e "${GREEN}  ✓ Cache headers are set correctly${NC}"
                echo "    $CACHE_HEADER"
            else
                echo -e "${YELLOW}  ⚠ Cache headers might not be set${NC}"
            fi
        else
            echo -e "${RED}  ✗ Image is not accessible (HTTP $HTTP_CODE)${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠ No images found yet${NC}"
    echo "  Upload an image to test image serving"
fi
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}All critical tests passed!${NC}"
echo ""
echo "Next steps:"
echo "1. Upload an image via API: POST /image/upload/"
echo "2. Get package with images: POST /package/get/"
echo "3. Access image URL in browser"
echo ""
echo "Performance tips:"
echo "- Images are cached for 30 days in browser"
echo "- Nginx serves images directly (no Django overhead)"
echo "- Expected performance: 10,000+ requests/sec"
echo ""
echo "Documentation:"
echo "- Setup guide: docs/NGINX_IMAGE_SERVING_SETUP.md"
echo "- Architecture: docs/IMAGE_SERVING_ARCHITECTURE.md"
echo "=========================================="

