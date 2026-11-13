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

## What each endpoint must document

The level of detail depends on the Teamwork level the squad is aiming for. Ultimo needs all of it.

| Level | Requirement | What to write |
| --- | --- | --- |
| Simplex | TW-S06 | Endpoint, protocol (REST, Socket or Kafka), short description, abstract request and response objects |
| Medium | TW-M01 | JSON request and response structures with every field and its type |
| Ultimo | TW-U04 | An example JSON object for every request and response |

Copy [`api-contract/_TEMPLATE.md`](api-contract/_TEMPLATE.md) for each new endpoint.

## Layout

```
api-contract/
├── conventions.md            # Rules every endpoint follows (auth, errors, dates, money, Kafka)
├── _TEMPLATE.md              # Copy this for each endpoint
├── 01-room-search.md         # PP provides, CP consumes
├── 02-booking.md             # PP provides, CP consumes
├── 03-payment-status.md      # Both directions
├── 04-rating-statistics.md   # CP provides, PP consumes
├── 05-premium-discounts.md   # Both directions
├── 06-regional-events.md     # CP creates topics, PP publishes
└── 07-pms.md                 # Cross-squad, shared PMS
squad-design/                 # Squad-level system design and data model for Milestone 1
```

The exchange files follow section 3 ("Subsystem Exchange Responsibilities") of both SRS documents.

## Changing the contract

1. Branch as `<type>/short-name` (`feat`, `fix`, `docs` or `chore`, e.g. `docs/room-search-endpoints`) and open a pull request. Nobody can push straight to `main`.
2. GitHub doesn't require an approval here, so changes can land quickly. Still, tag someone from the other team on the PR. A contract change only one side has seen doesn't count as agreed.
3. Squash merge it. The PR title becomes the commit message.
4. If the change breaks an existing endpoint, say so in the PR title and post it in both teams' stand-up notes.
