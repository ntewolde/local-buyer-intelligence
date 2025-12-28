# CSV Import Guide

This guide explains how to import data via CSV files for the Local Buyer Intelligence Platform.

## Overview

The platform supports CSV imports for three data types:
1. **Property Data** - Property characteristics (non-PII)
2. **Events Data** - Public events and calendars
3. **Channels Data** - Institutional channels and gatekeepers

## Important: PII Compliance

**⚠️ CRITICAL**: CSV files must NOT contain any PII (Personal Identifiable Information).

### Disallowed Columns
The following columns will be rejected:
- `email`, `e-mail`, `email_address`
- `phone`, `phone_number`, `mobile`, `cell`
- `first_name`, `last_name`, `full_name`, `name`, `owner_name`
- `address`, `street`, `street_address`, `apt`, `apartment`, `unit`
- `ssn`, `social_security_number`
- `dob`, `date_of_birth`, `birthday`
- Social media fields (`facebook`, `instagram`, `linkedin`, `twitter`)

**Only aggregated, non-personal data is allowed.**

## Property CSV Format

### Required Columns
- `zip_code` - ZIP code (string)

### Optional Columns
- `property_type` - SINGLE_FAMILY, MULTI_FAMILY, CONDO, APARTMENT, MOBILE_HOME, COMMERCIAL, UNKNOWN
- `ownership_type` - OWNER_OCCUPIED, RENTER_OCCUPIED, UNKNOWN
- `lot_size_sqft` - Lot size in square feet (integer)
- `year_built` - Year property was built (integer)
- `estimated_income_band` - LOW, MID, HIGH (optional proxy)
- `block_group` - Census block group (string, preferred for aggregation)
- `lat`, `lon` - Latitude/longitude (will be jittered for privacy)

### Example

See `examples/property_template.csv`:

```csv
zip_code,property_type,ownership_type,lot_size_sqft,year_built,estimated_income_band,block_group,lat,lon
10001,SINGLE_FAMILY,OWNER_OCCUPIED,8000,1995,HIGH,360610001001,40.7505,-73.9973
10001,CONDO,OWNER_OCCUPIED,0,2010,MID,360610001002,40.7510,-73.9970
```

### How It Works

- Property data is **aggregated** before storage
- Data is grouped by ZIP code, property type, and ownership type
- Stored as DemandSignal rows (not individual household records)
- This ensures no individual property can be identified

## Events CSV Format

### Required Columns
- `event_name` - Name of the event (string)
- `start_date` - Start date (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)

### Optional Columns
- `end_date` - End date (ISO format)
- `zip_code` - ZIP code where event occurs
- `category` - Event category (string)
- `estimated_attendance` - Estimated attendance (integer)
- `source_url` - URL to event source

### Example

See `examples/events_template.csv`:

```csv
event_name,start_date,end_date,zip_code,category,estimated_attendance,source_url
Summer Festival,2024-07-04,2024-07-04,10001,community_event,5000,https://example.com/events/summer-festival
City Market,2024-06-15,2024-06-15,10002,market,1000,https://example.com/events/city-market
```

### How It Works

- Events are stored as DemandSignal rows
- Service category is inferred from event category (fireworks, outdoor events, etc.)
- Used for timing recommendations in reports

## Channels CSV Format

### Required Columns
- `channel_type` - HOA, PROPERTY_MANAGER, SCHOOL, CHURCH, VENUE, MEDIA, COMMUNITY_NEWSLETTER, OTHER
- `name` - Channel name (string)

### Optional Columns
- `zip_code` - ZIP code (string)
- `estimated_reach` - Estimated reach (integer)
- `website` - Website URL (generic, no personal contacts)
- `source_url` - Source URL (public page)
- `notes` - Additional notes (text)
- `city`, `state` - Location information

### Example

See `examples/channels_template.csv`:

```csv
channel_type,name,city,state,zip_code,estimated_reach,website,source_url,notes
HOA,Sunset Hills HOA,New York,NY,10001,150,https://example.com/sunset-hills,https://example.com/hoa-directory,Active community association
PROPERTY_MANAGER,ABC Property Management,New York,NY,10001,500,https://example.com/abc-properties,https://example.com/pm-directory,Manages multiple residential buildings
```

### Important Notes

- **NO personal emails or phone numbers**
- Only generic website URLs (office pages, not contact forms)
- Deduplication: If a channel with same name/type/geography exists, it will be updated

## Import Process

### Step 1: Upload CSV File

1. Navigate to "Data Import" in the frontend
2. Select geography
3. Select import type (property, events, or channels)
4. Choose CSV file
5. Click "Upload File"

The file will be validated for PII columns before upload completes.

### Step 2: Start Import

1. After upload, click "Start Import"
2. Import runs as a background job (Celery)
3. Check status in the "Import History" section
4. Status will show: queued → running → success/failed

### Step 3: Verify Import

- Check geography freshness timestamps
- View imported data via API or frontend
- For channels, check the Channels page
- For events/property, check Demand Signals via API

## API Import (Alternative)

You can also import via API:

```bash
# 1. Upload file
curl -X POST http://localhost:8000/api/v1/uploads/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@property_data.csv"

# Response: {"file_ref": "uuid-here", ...}

# 2. Start import
curl -X POST "http://localhost:8000/api/v1/import/property?geography_id=1&file_ref=uuid-here" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response: {"ingestion_run_id": "uuid-here", "status": "queued", ...}
```

## Best Practices

1. **Use Templates**: Start with the example templates in `examples/`
2. **Validate Locally**: Check your CSV for disallowed columns before uploading
3. **Start Small**: Test with a small file first
4. **Check Status**: Monitor import status in the Import History
5. **Verify Data**: After import, verify data appears correctly
6. **Handle Errors**: If import fails, check error message and fix CSV

## Troubleshooting

### "CSV contains disallowed PII columns" Error

- Check column headers for any PII fields
- Remove or rename columns to non-PII names
- Use the example templates as reference

### Import Stuck in "Running" Status

- Check Celery worker logs
- Verify Redis is running
- May need to restart Celery worker

### No Data After Import

- Check import status for errors
- Verify geography_id matches
- Check CSV format matches template
- Verify data in database via API

### Memory Issues with Large Files

- Split large CSVs into smaller batches
- Process ZIP codes in groups
- Consider increasing Celery worker memory

## Data Quality Tips

1. **ZIP Codes**: Use 5-digit ZIP codes consistently
2. **Dates**: Use ISO format (YYYY-MM-DD)
3. **Enums**: Use exact enum values (see templates)
4. **Numbers**: Ensure numeric fields are actually numbers
5. **Encoding**: Use UTF-8 encoding for CSV files

## Questions?

- Check API docs: http://localhost:8000/docs
- Review example templates in `examples/` folder
- See main README.md for general information






