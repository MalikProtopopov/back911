#!/bin/bash
set -e

echo "=========================================="
echo "  911 Backend - Full Data Import"
echo "=========================================="
echo ""

# 1. Import base data from SQL dump
echo "📦 STEP 1: Importing base data from SQL dump..."
echo ""

echo "  → Importing cities..."
python manage.py import_cities

echo ""
echo "  → Importing services..."
python manage.py import_services

echo ""
echo "  → Importing technic categories..."
python manage.py import_technic_categories

echo ""
echo "  → Importing options..."
python manage.py import_options

echo ""
echo "  → Importing prices (this may take a while)..."
python manage.py import_prices

# 2. Load static fixtures
echo ""
echo "📋 STEP 2: Loading static fixtures..."
python manage.py loaddata \
    website_api/fixtures/initial_advantages.json \
    website_api/fixtures/initial_metrics.json \
    website_api/fixtures/initial_contacts.json \
    website_api/fixtures/initial_app_links.json

# 3. Generate content
echo ""
echo "✍️  STEP 3: Generating HTML content..."
python manage.py generate_content

# 4. Generate SEO
echo ""
echo "🔍 STEP 4: Generating SEO metadata..."
python manage.py generate_seo

# 5. Show statistics
echo ""
echo "=========================================="
echo "  ✓ Import Complete!"
echo "=========================================="
echo ""

CITIES=$(python manage.py shell -c "from website_api.models import City; print(City.objects.count())")
SERVICES=$(python manage.py shell -c "from website_api.models import Service; print(Service.objects.count())")
OPTIONS=$(python manage.py shell -c "from website_api.models import Option; print(Option.objects.count())")
PRICES=$(python manage.py shell -c "from website_api.models import OptionPrice; print(OptionPrice.objects.count())")
SERVICE_CONTENT=$(python manage.py shell -c "from website_api.models import ServiceContent; print(ServiceContent.objects.count())")
SEO_META=$(python manage.py shell -c "from website_api.models import SeoMeta; print(SeoMeta.objects.count())")

echo "📊 Database Statistics:"
echo "  • Cities:           $CITIES"
echo "  • Services:         $SERVICES"
echo "  • Options:          $OPTIONS"
echo "  • Prices:           $PRICES"
echo "  • Service Content:  $SERVICE_CONTENT"
echo "  • SEO Metadata:     $SEO_META"
echo ""
echo "🎉 Your website is ready for production!"
echo ""

