# Regional-event notifications

| | |
| --- | --- |
| Provides | **CP**: administers events, creates the topics, sends the favourited event and city, owns favourites and the search route |
| Consumes | **PP**: returns the two highest-rated providers in the event's city (price per night, logo URL, type, name, overall rating) |
| Requirement IDs | PP-EVENT-S01–S02, M01, U01–U02 · CP-EVENT-S01, M01–M03, U01–U03 |

REST at Simplex, real-time socket at Medium, Kafka at Ultimo (CP creates the topic, PP publishes, CP consumes). Only active Premium customers who favourited the event get it. Ultimo timing: notify immediately if the event is ongoing or starts within two months; otherwise notify exactly two months before it starts.

## Agreed details

_Fill in before the contract deadline: fields, access scope, limits and failure behaviour that the SRS leaves to the teams._

## Endpoints

_Add one section per endpoint, copied from [`_TEMPLATE.md`](_TEMPLATE.md)._
