# Customer Portal API Contract

| | |
| --- | --- |
| Version | 0.1.0 (draft) |
| Owner | Customer Portal |
| Consumers | Provider Portal |
| Last updated | 2026-11-13 |

## Background

APIs that Customer Portal (CP) provides to Provider Portal (PP). CP owns customers, membership, reviews, rating statistics and regional events. Shared rules are in [common.md](common.md). Scope, from section 3 of both SRS documents:

| Exchange | CP provides | PP provides | Requirement IDs |
| --- | --- | --- | --- |
| Reviews and rating statistics | Reviews and CP-calculated statistics: Overall, Service, Friendliness, Room, counts, preset-option percentages | Statistics requests for one provider | PP-RATING-S01, M01, U01–U02 · CP-RATING-S01–S04, M01–M03, U01–U02 |
| Premium discounts | Customer membership and order information | Discount packages and room policies | PP-DISCOUNT-S02 |
| Regional-event notifications | Events, topics, favourited event and city, search route | Top two providers for the event's city | CP-EVENT-S01, M01–M03, U01–U03 · PP-EVENT-S01–S02, M01, U01–U02 |
| Monetary order and status | Order or payment reference, customer cancellation requests | Approval, cancellation and payout or refund outcomes | CP-MONEY-S01, M01–M03, U01–U04 · PP-MONEY-S01, M01–M03, U01 |

## Design Decisions

_None agreed yet. Number each decision and give a one-line reason._

## Identity Model

| Identifier | Type | Description | Usage |
| --- | --- | --- | --- |
| customerId | string (uuid) | Customer account. Owned by CP. | Sent with bookings and membership lookups. |
| reviewId | string (uuid) | Review of a provider. Owned by CP. | Returned with comments. |
| eventId | string (uuid) | Regional event. Owned by CP. | Sent when an event is favourited. |
| providerId | string (uuid) | Accommodation provider. Owned by PP. | Key for rating statistics requests. |

## Endpoint Summary

| # | Method | Path | Protocol | Description |
| --- | --- | --- | --- | --- |

## Enums

### MembershipTier

| Value | Description |
| --- | --- |
| STANDARD | Standard customer |
| PREMIUM | Premium customer, USD 100 per year |

### RatingCategory

| Value | Description |
| --- | --- |
| OVERALL | Entered independently, 1 to 5, no preset options |
| SERVICE | 1 to 5, with preset options per star group |
| FRIENDLINESS | 1 to 5, with preset options per star group |
| ROOM | 1 to 5, with preset options per star group |

### StarGroup

| Value | Description |
| --- | --- |
| ONE_TO_TWO | 1 or 2 stars |
| THREE | 3 stars |
| FOUR_TO_FIVE | 4 or 5 stars |

## Endpoints

_No endpoints yet. Copy endpoint blocks from [_TEMPLATE.md](_TEMPLATE.md)._

## Core Schemas

_No shared schemas yet._

## Open Points

| ID | Topic | Status |
| --- | --- | --- |
| OP-1 | Rating statistics: which measures, percentage denominators (including reviews with no preset option) | Open |
| OP-2 | Membership lookup: which fields PP may see, and the access scope | Open |
| OP-3 | Events: topic names, payload, and the two-month notification timing (CP-EVENT-U03) | Open |
| OP-4 | Payment and cancellation: who calls the sandbox and how outcomes reach the customer in real time | Open |

## Changelog

| Version | Date | Change |
| --- | --- | --- |
| 0.1.0 | 2026-11-13 | Skeleton with scope, identifiers and SRS-defined enums. |
