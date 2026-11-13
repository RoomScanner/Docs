# Provider Portal API Contract

| | |
| --- | --- |
| Version | 0.1.0 (draft) |
| Owner | Provider Portal |
| Consumers | Customer Portal |
| Last updated | 2026-11-13 |

## Background

APIs that Provider Portal (PP) provides to Customer Portal (CP). PP owns rooms, availability and bookings. Shared rules are in [common.md](common.md). Scope, from section 3 of both SRS documents:

| Exchange | PP provides | CP provides | Requirement IDs |
| --- | --- | --- | --- |
| Room search, catalogue and availability | Matching providers and rooms, quantities, images, amenities, full-text search and shard retrieval | Search criteria, selected provider or room ID, query context | PP-SEARCH-S01–S03, M01–M02, U01–U02 · CP-SEARCH-S01–S03, M01–M03 |
| Booking creation, eligibility and outcomes | Booking storage and references, reservation, review eligibility, receptionist approval or cancellation, inventory outcomes | Customer and membership details, selected room, dates, quantity, adult and child counts | PP-BOOK-S01–S02, U01 · PP-ROOM-M02, U02 · CP-BOOK-S01–S02 |
| Monetary order and status | Approval or cancellation outcome, return payout status (Medium), escrow release or refund (Ultimo) | Simulated order (Simplex), payment reference (Medium), held payment reference (Ultimo), customer cancellation requests | PP-MONEY-S01, M01–M03, U01 · CP-MONEY-S01, M01–M03, U01–U04 |
| Premium discounts | Discount packages, the policy on each room, calculation rules | Membership and order information | PP-DISCOUNT-S01–S02 |
| Regional-event suggestions | Two highest-rated providers in the event's city | Event and city information, topic | PP-EVENT-S01–S02, M01, U01–U02 · CP-EVENT-M02, U01 |

## Design Decisions

_None agreed yet. Number each decision and give a one-line reason._

## Identity Model

| Identifier | Type | Description | Usage |
| --- | --- | --- | --- |
| providerId | string (uuid) | Accommodation provider account. Owned by PP. | Returned in search results. Used to fetch a provider's rooms. |
| branchId | string (uuid) | A property at one address. Owned by PP. | Returned with rooms. |
| roomId | string (uuid) | Room listing with a quantity. Owned by PP. | Sent by CP when booking. |
| bookingId | string (uuid) | Booking. Owned by PP. | Returned on creation. Used for status, cancellation and review eligibility. |
| customerId | string (uuid) | Customer account. Owned by CP. | Sent by CP in booking requests. |

## Endpoint Summary

| # | Method | Path | Protocol | Description |
| --- | --- | --- | --- | --- |

## Enums

### ProviderCategory

| Value | Description |
| --- | --- |
| RESORT | Resort |
| HOTEL | Hotel |
| MOTEL_HOSTEL | Motel or hostel |
| HOMESTAY | Homestay |

### RoomType

| Value | Description |
| --- | --- |
| BUNK_BED | Bunk bed (CP-SEARCH-S01) |
| SINGLE_TWIN_BED | Single or twin bed |
| DOUBLE_BED | Double bed |

### Amenity

| Value | Description |
| --- | --- |
| FREE_WIFI | Free WiFi (PP-ROOM-S06) |
| KITCHEN | Kitchen |
| WASHING_MACHINE | Washing machine |
| PETS_ALLOWED | Pets allowed |

### ServiceFilter

| Value | Description |
| --- | --- |
| FREE_WIFI | Free WiFi (PP-SEARCH-S01, CP-SEARCH-S02) |
| PRIVATE_BATHROOM | Private bathroom |
| AIR_CONDITIONING | Air-conditioning |
| DISABLED_FACILITIES | Facilities for disabled guests |

### BookingStatus

| Value | Description |
| --- | --- |
| PENDING | Rooms reserved, waiting for receptionist approval. No automatic expiry. |
| CONFIRMED | Approved by the receptionist. |
| CANCELLED | Cancelled by the customer or the receptionist. |

## Endpoints

_No endpoints yet. Copy endpoint blocks from [_TEMPLATE.md](_TEMPLATE.md)._

## Core Schemas

_No shared schemas yet._

## Open Points

| ID | Topic | Status |
| --- | --- | --- |
| OP-1 | Search: searchable fields, date and availability rules, result contents, page size for lazy loading | Open |
| OP-2 | Booking: date and capacity rules, what review-eligibility data PP returns (stay dates) | Open |
| OP-3 | Booking redundancy (Ultimo): how CP's entry point reaches the redundant booking service | Open |
| OP-4 | Payment: who calls the sandbox, which references PP stores, how payout and refund outcomes are reported back | Open |
| OP-5 | Discounts: calculation, when eligibility is checked, effect of changing or cancelling a policy on existing bookings | Open |
| OP-6 | Event suggestions: transport per level (REST, Socket, Kafka) and timing rules | Open |

## Changelog

| Version | Date | Change |
| --- | --- | --- |
| 0.1.0 | 2026-11-13 | Skeleton with scope, identifiers and SRS-defined enums. |
