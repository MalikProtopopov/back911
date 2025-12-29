#!/bin/bash

# Script to load all data for 911 corporate website
# Usage: ./scripts/load_all_data.sh
# For Docker: docker-compose -f docker-compose.dev.yml exec web ./scripts/load_all_data.sh

set -e

echo "🚀 Starting data loading for 911 Corporate Website..."
echo ""

# Check if running in Docker or locally
if [ -f /.dockerenv ]; then
    PYTHON_CMD="python"
else
    PYTHON_CMD="poetry run python"
fi

echo "📦 Step 1: Loading base data fixtures..."
echo "   - Cities (82)"
$PYTHON_CMD manage.py loaddata website_api/fixtures/cities.json
echo "   - Services (4)"
$PYTHON_CMD manage.py loaddata website_api/fixtures/services.json
echo "   - Technic categories"
$PYTHON_CMD manage.py loaddata website_api/fixtures/technic_categories.json
echo "   - Options"
$PYTHON_CMD manage.py loaddata website_api/fixtures/options.json
echo "   - Option prices (sample)"
$PYTHON_CMD manage.py loaddata website_api/fixtures/option_prices.json
echo "✅ Base data loaded!"
echo ""

echo "📦 Step 2: Loading static content..."
echo "   - Advantages"
$PYTHON_CMD manage.py loaddata website_api/fixtures/initial_advantages.json
echo "   - Metrics"
$PYTHON_CMD manage.py loaddata website_api/fixtures/initial_metrics.json
echo "   - Contacts"
$PYTHON_CMD manage.py loaddata website_api/fixtures/initial_contacts.json
echo "   - App links"
$PYTHON_CMD manage.py loaddata website_api/fixtures/initial_app_links.json
echo "✅ Static content loaded!"
echo ""

echo "🔧 Step 3: Generating dynamic content..."
echo "   - Generating content for all cities and services..."
$PYTHON_CMD manage.py generate_content
echo "✅ Content generated!"
echo ""

echo "🔍 Step 4: Generating SEO metadata..."
echo "   - Generating SEO for all pages..."
$PYTHON_CMD manage.py generate_seo
echo "✅ SEO metadata generated!"
echo ""

echo "============================================"
echo "✅ All data loaded successfully!"
echo ""
echo "Summary:"
echo "  - 82 cities"
echo "  - 4 services"
echo "  - 50+ options"
echo "  - Sample prices for major cities"
echo "  - SEO metadata for all pages"
echo "  - Static content (advantages, metrics, contacts)"
echo ""
echo "Next steps:"
echo "  1. Review data in Django Admin: http://localhost:8000/admin/"
echo "  2. Test API endpoints: http://localhost:8000/api/docs/"
echo "  3. Add custom content as needed"
echo "============================================"

