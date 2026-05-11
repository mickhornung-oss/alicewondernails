# API Module – v1 Read-only

## Purpose

The API module provides a read-only REST API foundation for Alice Wonder Nails, specifically designed for:

- Local and development use
- Product catalog queries
- Shipping method availability checks
- Payment method availability checks  
- Legal document metadata retrieval
- Health/status checking

This module does NOT handle:

- Checkout submission
- Order creation
- Payment processing
- Shipping booking
- User authentication/login
- User registration
- Admin operations

---

## Scope & Boundaries

### What This Module Does

**v1 Read-only API**

- 7 read-only endpoints
- GET requests only
- JSON/DRF responses
- Standardized success/error format
- Query parameter validation (customer_group)
- 404 handling for missing resources

### What This Module Does NOT Do

- User authentication/login (out of scope)
- JWT/OAuth/Session management (not in this block)
- Order/Checkout submission (frozen in checkout module)
- Payment execution (read-only methods only)
- Shipping booking (read-only methods only)
- Email sending (not in API)
- Admin operations (read-only endpoints only)
- Webhooks (not in this block)
- External provider integrations (not in this block)

### Production Status

- **Local/Dev**: ✅ Ready
- **Staging**: ❌ Not ready (awaiting full deployment infrastructure)
- **Production**: ❌ Not ready (5 security warnings persist from `check --deploy`)

---

## API Endpoints

### Health & Status

#### GET `/api/v1/health/`

Returns service health information.

**Response (200):**

```json
{
  "success": true,
  "data": {
    "status": "ok",
    "service": "alice-wonder-nails-api",
    "version": "v1",
    "environment": "local-dev"
  }
}
```

**Notes:**
- No secrets in response
- Simple status check for health monitoring
- Always GET only

---

### Catalog Endpoints

#### GET `/api/v1/catalog/categories/`

Returns all active product categories.

**Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Gel",
      "slug": "gel",
      "sort_order": 1
    },
    ...
  ]
}
```

**Notes:**
- Read-only list of categories
- Ordered by sort_order and name
- No pricing info included

---

#### GET `/api/v1/catalog/products/`

Returns list of active products visible to specified customer group.

**Query Parameters:**
- `customer_group` (required): `b2c` or `b2b` (default: `b2c`)
- `category` (optional): Category slug to filter by

**Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Product Name",
      "slug": "product-slug",
      "short_description": "...",
      "category": {
        "id": 1,
        "name": "Gel",
        "slug": "gel",
        "sort_order": 1
      },
      "variants": [...]
    },
    ...
  ]
}
```

**Error (400):**

```json
{
  "success": false,
  "error": {
    "code": "invalid_customer_group",
    "message": "customer_group must be \"b2c\" or \"b2b\", got \"invalid\""
  }
}
```

**Notes:**
- Filtered by visibility (public, b2c_only, b2b_only)
- No pricing info included in list
- Variants included but without prices

---

#### GET `/api/v1/catalog/products/<slug>/`

Returns detailed product information by slug.

**Query Parameters:**
- `customer_group` (optional): `b2c` or `b2b` (default: `b2c`)

**Response (200):**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Product Name",
    "slug": "product-slug",
    "description": "...",
    "short_description": "...",
    "category": {...},
    "variants": [...]
  }
}
```

**Error (404):**

```json
{
  "success": false,
  "error": {
    "code": "product_not_found",
    "message": "Product with slug \"invalid-slug\" not found"
  }
}
```

**Notes:**
- Respects customer_group visibility
- Returns 404 if product invisible for group
- No pricing info included

---

### Shipping Endpoints

#### GET `/api/v1/shipping/methods/`

Returns available shipping methods for specified customer group.

**Query Parameters:**
- `country` (optional): Country code (default: `DE`)
- `customer_group` (optional): `b2c` or `b2b` (default: `b2c`)

**Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Standard Shipping",
      "code": "standard",
      "customer_group": "b2c",
      "base_price": "5.00",
      "currency": "EUR",
      "estimated_min_days": 2,
      "estimated_max_days": 5
    },
    ...
  ]
}
```

**Error (400):**

```json
{
  "success": false,
  "error": {
    "code": "invalid_customer_group",
    "message": "customer_group must be \"b2c\" or \"b2b\", got \"invalid\""
  }
}
```

**Notes:**
- Only active methods returned
- Only active zones included
- base_price includes customer_group "all" + specific group
- No shipping booking/calculation in this endpoint
- Estimated days are informational only

---

### Payment Endpoints

#### GET `/api/v1/payments/methods/`

Returns available payment methods for specified customer group.

**Query Parameters:**
- `customer_group` (optional): `b2c` or `b2b` (default: `b2c`)

**Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Credit Card",
      "code": "credit-card",
      "provider": "stripe",
      "customer_group": "b2c",
      "description": "Pay by credit card"
    },
    ...
  ]
}
```

**Error (400):**

```json
{
  "success": false,
  "error": {
    "code": "invalid_customer_group",
    "message": "customer_group must be \"b2c\" or \"b2b\", got \"invalid\""
  }
}
```

**Notes:**
- Only active methods returned
- Provider is classification only, not real integration
- No payment processing in this endpoint
- No transaction recording

---

### Legal Endpoints

#### GET `/api/v1/legal/active/`

Returns metadata of active legal documents for specified customer group.

**Query Parameters:**
- `customer_group` (optional): `b2c` or `b2b` (default: `b2c`)

**Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "document_type": "privacy_policy",
      "title": "Datenschutzrichtlinie",
      "version": "1.0",
      "target_group": "all",
      "effective_from": "2026-01-01T00:00:00Z"
    },
    ...
  ]
}
```

**Error (400):**

```json
{
  "success": false,
  "error": {
    "code": "invalid_customer_group",
    "message": "customer_group must be \"b2c\" or \"b2b\", got \"invalid\""
  }
}
```

**Notes:**
- Returns only active document versions
- Metadata only (not full document content)
- Respects target_group (all, b2c, b2b)
- No legal advice guarantee

---

## Response Format

### Success Response

```json
{
  "success": true,
  "data": {
    ...
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "error_code",
    "message": "Human-readable error message"
  }
}
```

**HTTP Status Codes:**
- `200 OK` – Successful request
- `400 Bad Request` – Invalid query parameters
- `404 Not Found` – Resource not found
- `405 Method Not Allowed` – Non-GET request (POST/PUT/DELETE)

---

## Technology Stack

- **Framework**: Django 5.2+
- **REST Library**: Django REST Framework (DRF) 3.15+
- **Function-based Views**: @api_view decorators
- **Serializers**: DRF ModelSerializer
- **Database**: PostgreSQL (read-only queries only)

---

## Testing

**Test File**: `backend/apps/api/tests/test_api.py`

**Test Coverage:**

1. **Health endpoint**: 4 tests
   - 200 response
   - success=true
   - correct data fields
   - no secrets in response

2. **Catalog endpoints**: 9 tests
   - Categories list (3 tests)
   - Products list (6 tests)
   - Product detail (4 tests)
   - Invalid customer_group (400)
   - Missing product (404)

3. **Shipping endpoints**: 4 tests
   - Methods list (3 tests)
   - Invalid customer_group (400)

4. **Payment endpoints**: 4 tests
   - Methods list (3 tests)
   - Invalid customer_group (400)

5. **Legal endpoints**: 3 tests
   - Active documents list (3 tests)
   - Invalid customer_group (400)

6. **API Boundaries**: 4 tests
   - POST not allowed on health
   - POST not allowed on products
   - POST not allowed on shipping
   - POST not allowed on payments

**Total**: 33 tests, all passing

---

## Known Limitations & Open Points

1. **No authentication** – All endpoints are public (intentional for v1)
2. **No pagination** – All lists are unfiltered (acceptable for v1)
3. **No rate limiting** – Not in this block
4. **No caching** – Queries direct to DB
5. **No webhook support** – Not in this block
6. **No search** – Basic slug filtering only
7. **No advanced filtering** – Limited to customer_group + category
8. **No API versioning beyond v1** – Future work

---

## Freeze Status

**Status**: `frozen` (as of Arbeitsblock 14.1)

**Freezing Rules** (when change requests arise):

1. Document the requested change and its business rationale
2. Assess impact on all 7 endpoints and 33 tests
3. Run full regression test suite (expect 304+ tests passing)
4. Update this module documentation
5. Update PROGRESS.md and DECISIONS.md
6. Commit with clear message explaining the change

**Change Types Allowed Without Full Review:**
- Bug fixes (e.g., missing 404 handling)
- Documentation corrections
- Test additions for uncovered scenarios

**Change Types Requiring Full Impact Review:**
- New endpoints
- New query parameters
- Response format changes
- Customer_group logic changes

---

## Related Modules

- `catalog` – Product, ProductCategory, ProductVariant models
- `shipping` – ShippingZone, ShippingMethod models
- `payments` – PaymentMethod model
- `legal` – LegalDocument, LegalDocumentVersion models
- `core` – Health check infrastructure (separate from API)

---

## Changelog

### 2026-05-05 – Arbeitsblock 14.1 – API Module Frozen

- 7 read-only endpoints implemented
- 33 comprehensive tests (100% passing)
- DRF integrated with standardized response format
- All boundary tests pass (POST rejected)
- No production freigabe (5 security warnings remain)
- Local/dev API green
- Module frozen pending business change requests
