### `METHOD /api/v1/partner/...` (or Kafka topic / socket event name)

| | |
| --- | --- |
| Provided by | PP or CP |
| Consumed by | CP or PP |
| Protocol | REST / Socket / Kafka |
| Requirement IDs | e.g. PP-SEARCH-S01, CP-SEARCH-S01 |
| Auth | e.g. partner service token |

Short description of what the call does and when it's used.

**Request**

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| | | | |

```json
{
}
```

**Response `200`**

| Field | Type | Notes |
| --- | --- | --- |
| | | |

```json
{
}
```

**Errors**

| Status | Code | When |
| --- | --- | --- |
| | | |

For Kafka, replace Request and Response with the request topic, the reply topic and the two payloads, and state the timeout before a resend.

