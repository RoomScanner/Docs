# RoomScanner: shared docs and API contract

This repository holds the API contract between [Customer Portal](https://github.com/RoomScanner/CustomerPortal) (CP) and [Provider Portal](https://github.com/RoomScanner/ProviderPortal) (PP), plus anything else both teams own together, such as the squad-level system design and data model. The course requires the contract to live in its own repo inside the squad organization (TW-S06).

## Deadlines

The contract is due by 18:00 on Friday of week N-2 for a milestone submitted in week N.

| Contract | Due | Git tag |
| --- | --- | --- |
| Milestone 1 | Fri 20 Nov 2026, 18:00 | `m1-contract` |
| Milestone 2 | Fri 1 Jan 2027, 18:00 (public holiday, confirm with the lecturer) | `m2-contract` |

When the contract is final for a milestone, tag the commit so the submitted version is easy to find:

```bash
git tag m1-contract && git push origin m1-contract
```

## Contract format

Every contract document follows one structure, and the `contract-format` check fails any pull request that breaks it. [`api-contract/_TEMPLATE.md`](api-contract/_TEMPLATE.md) is a complete worked example with REST, Kafka and Socket endpoints. Copy blocks from it.

Each document has these sections, in this order: Background, Design Decisions, Identity Model, Endpoint Summary, Enums, Endpoints, Core Schemas, Open Points, Changelog. Each endpoint has:

- a numbered heading such as `### 2. POST /api/v1/partner/bookings`, `### 4. KAFKA roomscanner.pp.rating-stats.request` or `### 5. SOCKET event-suggestions`, matching a row in the Endpoint Summary
- a one-line description and a table giving protocol, provider, consumer and requirement IDs
- a JSON example and a `| Field | Type | Required | Description |` table for every request, response and message (Simplex TW-S06, Medium TW-M01, Ultimo TW-U04 in one go)
- a Response Codes table for REST, or a Failure and Retry section for Kafka

Headers, the error envelope, status codes, pagination and the Kafka envelope are defined once in [`api-contract/common.md`](api-contract/common.md).

Run the check locally before pushing:

```bash
python3 scripts/check_contract.py
```

## Layout

```
api-contract/
├── _TEMPLATE.md          # Worked example of the required format
├── common.md             # Headers, error envelope, status codes, pagination, Kafka envelope
├── provider-portal.md    # APIs Provider Portal provides
├── customer-portal.md    # APIs Customer Portal provides
└── pms.md                # Cross-squad PMS, shared with the partner squad
scripts/check_contract.py # Format check run by CI
squad-design/             # Squad-level system design and data model for Milestone 1
```

Each team documents the APIs it provides in its own file. The scope tables at the top follow section 3 ("Subsystem Exchange Responsibilities") of both SRS documents.

## Changing the contract

1. Branch as `<type>/short-name` (`feat`, `fix`, `docs` or `chore`, e.g. `docs/room-search-endpoints`) and open a pull request. Nobody can push straight to `main`.
2. GitHub doesn't require an approval here, so changes can land quickly. Still, tag someone from the other team on the PR. A contract change only one side has seen doesn't count as agreed.
3. Bump the document's Version and add a Changelog row.
4. Once `contract-format` passes, squash merge it. The PR title becomes the commit message.
5. If the change breaks an existing endpoint, say so in the PR title and post it in both teams' stand-up notes.
