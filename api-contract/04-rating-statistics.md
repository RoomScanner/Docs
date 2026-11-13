# Reviews and rating statistics

| | |
| --- | --- |
| Provides | **CP**: reviews and CP-calculated statistics (Overall, Service, Friendliness, Room, counts, preset-option percentages) |
| Consumes | **PP**: requests statistics for one accommodation provider on demand |
| Requirement IDs | PP-RATING-S01, M01, U01–U02 · CP-RATING-S01–S04, M01–M03, U01–U02 |

Reviews apply to the accommodation provider, not a room. PP must not recalculate statistics. Overall is 1–5 with no preset options; each subcategory is 1–5 with two preset options per star group (1–2, 3, 4–5), and a customer may pick zero, one or both. Agree the statistical measures and the percentage denominators here. No real-time rating push is required. At Ultimo this is a Kafka request/reply with correlation and resend.

## Agreed details

_Fill in before the contract deadline: fields, access scope, limits and failure behaviour that the SRS leaves to the teams._

## Endpoints

_Add one section per endpoint, copied from [`_TEMPLATE.md`](_TEMPLATE.md)._
