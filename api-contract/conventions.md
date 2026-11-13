# Contract conventions

These are proposed defaults. Both teams should confirm or change them at the first contract meeting, then delete this line.

## REST

- Base path: `/api/v1/...`. Partner-facing endpoints go under `/api/v1/partner/...` so they're easy to protect separately.
- JSON bodies, `camelCase` field names.
- IDs are strings (UUIDs), so either team can change storage or sharding without breaking the contract.
- Dates and times: ISO 8601 in UTC, e.g. `2026-12-04T11:00:00Z`. Stay dates without a time use `YYYY-MM-DD`.
- Money: `{ "amount": 12000, "currency": "USD" }`, with `amount` in minor units (cents) to avoid floating-point errors.
- Lists are paginated with `?page=0&size=20` or a cursor. Lazy loading in search (PP-SEARCH-M02 / CP-SEARCH-M02) depends on this.

## Partner authentication (INT-M03)

From Medium integration onwards, only the trusted partner subsystem may call partner endpoints. Proposed scheme: each subsystem has a client ID and secret, and sends `Authorization: Bearer <service token>` on every partner call. Requests from anything else get `401`. Write the agreed scheme here once chosen.

## Errors

Every error response uses the same shape:

```json
{
  "status": 409,
  "code": "ROOM_UNAVAILABLE",
  "message": "Only 1 room of this type is left for the selected dates.",
  "timestamp": "2026-12-04T11:00:00Z"
}
```

Use `400` for validation errors, `401` for missing or bad credentials, `403` when the caller is authenticated but not allowed, `404` when the resource doesn't exist, `409` for conflicts such as no availability, and `503` when a dependency is down. The circuit-breaker requirements need `503` kept separate from `401`.

## Kafka (Ultimo integration, INT-U01 to INT-U03)

- Every request has a request topic and a separate reply topic (INT-U02).
- Topic names: `roomscanner.<owner>.<feature>.<request|reply>`, e.g. `roomscanner.pp.search.request`.
- Every message carries a `correlationId` (UUID) and a `sentAt` timestamp. The reply copies the request's `correlationId` so the requester can match them.
- If no reply arrives within the agreed timeout, the requester resends with the same `correlationId` (INT-U03). Consumers must therefore handle duplicates safely.

Message envelope:

```json
{
  "correlationId": "7b1c...",
  "sentAt": "2026-12-04T11:00:00Z",
  "source": "customer-portal",
  "payload": { }
}
```

## Socket (Medium real-time features)

Write the agreed library, namespace and event names here (e.g. Socket.IO or STOMP over WebSocket) once chosen.
