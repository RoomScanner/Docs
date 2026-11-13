# PMS API Contract

| | |
| --- | --- |
| Version | 0.1.0 (draft) |
| Owner | Squad (shared with partner squad) |
| Consumers | Provider Portal, Customer Portal, partner squad |
| Last updated | 2026-11-13 |

## Background

Cross-ecosystem Property Management System shared with the partner squad (BE-U09, DEP-U05). Rooms published for sharing become visible and bookable on both platforms, with their ratings and reviews. Providers get access through a USD 200 annual PMS subscription, which is separate from the customer's USD 100 Premium membership. Shared rules are in [common.md](common.md).

| Exchange | This squad provides | Partner squad provides | Requirement IDs |
| --- | --- | --- | --- |
| Cross-ecosystem PMS | Only agreed room, customer and order fields needed for authorised PMS operations | The same, from their platform | PP-PMS-S01–S02 · BE-U09 · DEP-U05 |

## Design Decisions

_None agreed yet. Number each decision and give a one-line reason._

## Identity Model

| Identifier | Type | Description | Usage |
| --- | --- | --- | --- |
| platformId | string | Which squad's platform owns a record. | Prefix or field on every shared record. |
| providerId | string (uuid) | Provider account on the owning platform. | Checked for an active PMS subscription. |

## Endpoint Summary

| # | Method | Path | Protocol | Description |
| --- | --- | --- | --- | --- |

## Enums

### SubscriptionStatus

| Value | Description |
| --- | --- |
| ACTIVE | Paid and within the annual period. |
| EXPIRED | Annual period ended. |

## Endpoints

_No endpoints yet. Copy endpoint blocks from [_TEMPLATE.md](_TEMPLATE.md)._

## Core Schemas

_No shared schemas yet._

## Open Points

| ID | Topic | Status |
| --- | --- | --- |
| OP-1 | Partner squad name and repository link | Open |
| OP-2 | Shared fields, identifiers and operations, and who implements each | Open |
| OP-3 | Who runs the PMS machine (DEP-U05) | Open |

## Changelog

| Version | Date | Change |
| --- | --- | --- |
| 0.1.0 | 2026-11-13 | Skeleton. |
