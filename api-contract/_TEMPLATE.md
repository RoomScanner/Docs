# Example API Contract

<!--
Copy this file to start a new contract document, or copy single endpoint blocks into an existing one.
CI (scripts/check_contract.py) checks every contract against this structure. Run it locally with:
  python3 scripts/check_contract.py
Everything below is a worked example. Replace it with real content.
-->

| | |
| --- | --- |
| Version | 0.1.0 (draft) |
| Owner | Provider Portal |
| Consumers | Customer Portal |
| Last updated | 2026-11-13 |

## Background

One paragraph on what this API is for and which SRS exchanges it covers. Shared rules (headers, error envelope, status codes, pagination, Kafka envelope) live in [common.md](common.md) and apply to every endpoint here.

| Exchange | This team provides | Partner provides | Requirement IDs |
| --- | --- | --- | --- |
| Room search | Matching providers and rooms | Search criteria | PP-SEARCH-S01, CP-SEARCH-S01 |

## Design Decisions

Numbered decisions the two teams agreed, each with a one-line reason. Example:

1. Partner endpoints live under `/api/v1/partner/` so they can be protected with the partner service token separately from user endpoints.
2. Search is read-only and never reserves rooms. Reservation happens only through the booking endpoint.

## Identity Model

| Identifier | Type | Description | Usage |
| --- | --- | --- | --- |
| providerId | string (uuid) | Accommodation provider account. Owned by PP. | Path parameter on provider reads. Returned in search results. |
| roomId | string (uuid) | Room listing. Owned by PP. | Sent by CP when booking. |
| customerId | string (uuid) | Customer account. Owned by CP. | Sent by CP in booking requests. Never exposed to other customers. |

## Endpoint Summary

| # | Method | Path | Protocol | Description |
| --- | --- | --- | --- | --- |
| 1 | GET | /api/v1/partner/providers | REST | Search accommodation providers. |
| 2 | POST | /api/v1/partner/bookings | REST | Create a pending booking. |
| 3 | GET | /api/v1/partner/bookings/{bookingId} | REST | Get one booking's status. |
| 4 | KAFKA | roomscanner.pp.rating-stats.request | Kafka | Ask CP for a provider's rating statistics. |
| 5 | SOCKET | event-suggestions | Socket | Push top two providers for a favourited event. |

## Enums

### ProviderCategory

| Value | Description |
| --- | --- |
| RESORT | Resort |
| HOTEL | Hotel |
| MOTEL_HOSTEL | Motel or hostel |
| HOMESTAY | Homestay |

### BookingStatus

| Value | Description |
| --- | --- |
| PENDING | Rooms reserved, waiting for receptionist approval. No automatic expiry. |
| CONFIRMED | Approved by the receptionist. |
| CANCELLED | Cancelled by the customer or the receptionist. |

## Endpoints

### 1. GET /api/v1/partner/providers

Search accommodation providers whose name contains the keyword (case-insensitive) and that have available rooms in the city. Read-only.

| Protocol | Provided by | Consumed by | Requirement IDs |
| --- | --- | --- | --- |
| REST | PP | CP | PP-SEARCH-S01, PP-SEARCH-S02, CP-SEARCH-S01 |

#### Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| city | string | Yes | City name in the squad's sub-region. |
| keyword | string | No | Case-insensitive substring of the provider name. |
| category | string enum (ProviderCategory) | No | Filter by provider category. |
| page | integer | No | Page number, from 0. Default 0. |
| size | integer | No | Page size. Default 20, max 100. |

#### 200 OK Response

```json
{
  "count": 1,
  "value": [
    {
      "providerId": "5f0c2a8e-8a1b-4a51-9c3e-2f7d1b9e4a10",
      "name": "Sheraton Saigon",
      "category": "HOTEL",
      "logoUrl": "https://cdn.example.com/logos/sheraton.png",
      "overallRating": 4.6
    }
  ]
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| count | integer | Yes | Total matches across all pages. |
| value | array<ProviderSummary> | Yes | This page of results. Empty when nothing matches. |

#### Response Codes

| Code | Meaning |
| --- | --- |
| 200 | Results returned, possibly empty. |
| 400 | Missing city or invalid parameter. |
| 401 | Missing or invalid partner token. |
| 500 | Unexpected server-side failure. |

### 2. POST /api/v1/partner/bookings

Create a booking and reserve the rooms until the receptionist approves or someone cancels.

| Protocol | Provided by | Consumed by | Requirement IDs |
| --- | --- | --- | --- |
| REST | PP | CP | PP-BOOK-S01, PP-BOOK-S02, CP-BOOK-S01 |

#### Request Body

```json
{
  "customerId": "c9d98b52-2f55-4e52-a170-bd4d1c4653f1",
  "membership": "PREMIUM",
  "roomId": "0b9f6f5e-31c4-4b8e-9d0a-6e2f3b1c7d22",
  "checkIn": "2026-12-20",
  "checkOut": "2026-12-23",
  "quantity": 2,
  "adults": 2,
  "children": 1
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| customerId | string (uuid) | Yes | Customer making the booking. |
| membership | string enum: STANDARD, PREMIUM | Yes | Customer's membership when booking, used for discounts. |
| roomId | string (uuid) | Yes | Room listing to book. |
| checkIn | string (date) | Yes | First night, YYYY-MM-DD. |
| checkOut | string (date) | Yes | Departure day, YYYY-MM-DD. Must be after checkIn. |
| quantity | integer | Yes | Rooms requested. Must be ≤ adults + children. |
| adults | integer | Yes | Number of adults. |
| children | integer | Yes | Number of children. |

#### 201 Created Response

```json
{
  "bookingId": "8e2d4c1a-7b3f-4f0e-a9d2-5c6b7e8f9a01",
  "status": "PENDING"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| bookingId | string (uuid) | Yes | New booking. |
| status | string enum (BookingStatus) | Yes | Always PENDING on creation. |

#### Response Codes

| Code | Meaning |
| --- | --- |
| 201 | Booking created and rooms reserved. |
| 400 | Invalid dates, or quantity > adults + children. |
| 401 | Missing or invalid partner token. |
| 404 | Room does not exist. |
| 409 | Not enough rooms available for those dates. |
| 500 | Unexpected server-side failure. |

### 3. GET /api/v1/partner/bookings/{bookingId}

Get the current status of one booking.

| Protocol | Provided by | Consumed by | Requirement IDs |
| --- | --- | --- | --- |
| REST | PP | CP | PP-MONEY-S01, CP-MONEY-S01 |

#### Path Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| bookingId | string (uuid) | Yes | Booking to read. |

#### 200 OK Response

```json
{
  "bookingId": "8e2d4c1a-7b3f-4f0e-a9d2-5c6b7e8f9a01",
  "status": "CONFIRMED",
  "decidedAt": "2026-12-01T03:15:00Z"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| bookingId | string (uuid) | Yes | Booking identifier. |
| status | string enum (BookingStatus) | Yes | Current status. |
| decidedAt | string (date-time) or null | No | When the receptionist approved or someone cancelled. Null while PENDING. |

#### Response Codes

| Code | Meaning |
| --- | --- |
| 200 | Booking found. |
| 401 | Missing or invalid partner token. |
| 404 | Booking does not exist. |

### 4. KAFKA roomscanner.pp.rating-stats.request

PP asks CP for one provider's rating statistics. CP replies on the reply topic with the same correlationId.

| Protocol | Provided by | Consumed by | Requirement IDs |
| --- | --- | --- | --- |
| Kafka | CP | PP | PP-RATING-U01, CP-RATING-U01 |

#### Request Message

Topic: `roomscanner.pp.rating-stats.request`

```json
{
  "correlationId": "1d3c5e7a-9b2f-4c6d-8e0a-2b4c6d8e0f12",
  "sentAt": "2026-12-01T03:15:00Z",
  "source": "provider-portal",
  "payload": { "providerId": "5f0c2a8e-8a1b-4a51-9c3e-2f7d1b9e4a10" }
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| correlationId | string (uuid) | Yes | Copied into the reply. Reused on resend. |
| sentAt | string (date-time) | Yes | When the message was sent. |
| source | string | Yes | Sending subsystem. |
| payload.providerId | string (uuid) | Yes | Provider to report on. |
| payload | object | Yes | Request data. |

#### Reply Message

Topic: `roomscanner.cp.rating-stats.reply`

```json
{
  "correlationId": "1d3c5e7a-9b2f-4c6d-8e0a-2b4c6d8e0f12",
  "sentAt": "2026-12-01T03:15:01Z",
  "source": "customer-portal",
  "payload": { "providerId": "5f0c2a8e-8a1b-4a51-9c3e-2f7d1b9e4a10", "overall": 4.6, "ratingCount": 132 }
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| correlationId | string (uuid) | Yes | Same value as the request. |
| sentAt | string (date-time) | Yes | When the reply was sent. |
| source | string | Yes | Sending subsystem. |
| payload | object | Yes | Statistics. |
| payload.overall | number | Yes | Mean Overall rating, 1 to 5. |
| payload.ratingCount | integer | Yes | Number of reviews counted. |

#### Failure and Retry

If no reply arrives within 5 seconds, PP resends with the same correlationId, up to 3 times, then shows "statistics unavailable". CP must treat a repeated correlationId as the same request.

### 5. SOCKET event-suggestions

PP pushes the two highest-rated providers in a favourited event's city to CP in real time.

| Protocol | Provided by | Consumed by | Requirement IDs |
| --- | --- | --- | --- |
| Socket | PP | CP | PP-EVENT-M01, CP-EVENT-M02 |

#### Event Message

```json
{
  "eventId": "e1f2a3b4-c5d6-4e7f-8a9b-0c1d2e3f4a5b",
  "providers": []
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| eventId | string (uuid) | Yes | CP's regional event. |
| providers | array<ProviderSummary> | Yes | Top two providers in the event's city. |

## Core Schemas

### ProviderSummary

```json
{
  "providerId": "5f0c2a8e-8a1b-4a51-9c3e-2f7d1b9e4a10",
  "name": "Sheraton Saigon",
  "category": "HOTEL",
  "logoUrl": "https://cdn.example.com/logos/sheraton.png",
  "overallRating": 4.6
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| providerId | string (uuid) | Yes | Provider account. |
| name | string | Yes | Public provider name. |
| category | string enum (ProviderCategory) | Yes | Provider category. |
| logoUrl | string (uri) or null | No | Logo image. |
| overallRating | number or null | No | CP-calculated Overall rating. Null when there are no reviews. |

## Open Points

| ID | Topic | Status |
| --- | --- | --- |
| OP-1 | Do search results include a price range per provider? | Open |

## Changelog

| Version | Date | Change |
| --- | --- | --- |
| 0.1.0 | 2026-11-13 | First draft. |
