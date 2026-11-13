# Common Contract Rules

These rules apply to every endpoint in [provider-portal.md](provider-portal.md), [customer-portal.md](customer-portal.md) and [pms.md](pms.md). They are proposed defaults: both teams confirm or change them at the first contract meeting.

General conventions:

- JSON bodies with `camelCase` field names.
- IDs are UUID strings, so either team can change storage or sharding without breaking the contract.
- Date-times are ISO 8601 in UTC (`2026-12-04T11:00:00Z`). Stay dates without a time use `YYYY-MM-DD`.
- Money is `{ "amount": 12000, "currency": "USD" }` with `amount` in minor units (cents).
- Enum values are `UPPER_SNAKE_CASE`.
- Partner-facing REST endpoints go under `/api/v1/partner/`.

## Common Headers

| Header | Type | Required | Description |
| --- | --- | --- | --- |
| Authorization: Bearer &lt;token&gt; | string | Yes | Partner calls use the partner service token (INT-M03). User calls use the user's JWS/JWE access token. |
| X-Correlation-Id | string (uuid) | No | Request tracing. Echoed back in the response. |
| Content-Type: application/json | string | For request bodies | JSON payload. |
| Accept: application/json | string | Yes | JSON response. |

Requests from systems other than the trusted partner subsystem are rejected with 401 (INT-M03). Record the agreed partner authentication scheme here once chosen.

## Common Error Response

Every 4xx and 5xx response uses this body (schema name `ErrorResponse`):

```json
{
  "error": {
    "code": "BadRequest",
    "message": "Human-readable summary",
    "details": [
      {
        "code": "InvalidField",
        "message": "Field 'quantity' must be at most adults + children",
        "target": "quantity",
        "severity": "error"
      }
    ]
  }
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| error | object | Yes | Error envelope. |
| error.code | string enum | Yes | Stable top-level code, from the Status Codes table. |
| error.message | string | Yes | Human-readable summary. |
| error.details | array&lt;object&gt; | No | Field-level or validation details. |
| error.details[].code | string | Yes | Stable detail code. |
| error.details[].message | string | Yes | Human-readable detail message. |
| error.details[].target | string | No | Related request field, parameter or path. |
| error.details[].severity | string enum: error, warning, info | No | Detail severity. |

## Status Codes

| Code | error.code | When |
| --- | --- | --- |
| 400 | BadRequest | Validation failure, missing fields, malformed payload, invalid parameter. |
| 401 | Unauthorized | Missing, expired or revoked token, or an untrusted caller. |
| 403 | Forbidden | Valid token but not allowed, e.g. a provider editing another provider's room, or no active PMS subscription. |
| 404 | NotFound | Resource does not exist or isn't visible to the caller. |
| 409 | Conflict | Not enough rooms, duplicate email, booking already decided. |
| 423 | Locked | Account locked after five failed logins in 60 seconds (PP-LOGIN-M02, CP-LOGIN-M02). |
| 429 | TooManyRequests | Rate limit exceeded (BE-U04). |
| 500 | InternalServerError | Unexpected server-side failure. |
| 502 | BadGateway | A downstream partner or payment sandbox returned an error. Include the provider's cause in `details`. |
| 503 | ServiceUnavailable | Destination unavailable or circuit open (BE-U07, BE-U08). Never used for bad credentials. |

## Pagination and Sorting

| Parameter | Type | Default | Max | Description |
| --- | --- | --- | --- | --- |
| page | integer | 0 | - | Page number, from 0. |
| size | integer | 20 | 100 | Page size. |
| sort | string | endpoint-specific | - | `field,asc` or `field,desc`. Each endpoint lists the fields it supports. |

Paged responses use `{ "count": <total>, "value": [ ... ] }`.

## Kafka Message Envelope

Every Kafka message (request, reply or event) uses this envelope:

```json
{
  "correlationId": "1d3c5e7a-9b2f-4c6d-8e0a-2b4c6d8e0f12",
  "sentAt": "2026-12-01T03:15:00Z",
  "source": "provider-portal",
  "payload": {}
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| correlationId | string (uuid) | Yes | Set by the requester. The reply copies it (INT-U02). A resend reuses it (INT-U03). |
| sentAt | string (date-time) | Yes | When this message was sent. |
| source | string enum: provider-portal, customer-portal, pms | Yes | Sending subsystem. |
| payload | object | Yes | Endpoint-specific data. |

Topics are named `roomscanner.<pp|cp|pms>.<feature>.<request|reply|event>`, where the owner segment is the subsystem that publishes to it. Consumers must handle a duplicate correlationId safely, because resends are expected.

## Socket Events

Record the agreed library (e.g. Socket.IO or STOMP over WebSocket), connection URL, namespace and authentication here. Each event is documented as a `SOCKET <event-name>` endpoint in the owning team's contract.
