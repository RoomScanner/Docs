# Room search, catalogue and availability

| | |
| --- | --- |
| Provides | **PP**: authoritative matching providers and rooms, quantities, images, amenities, full-text search and shard retrieval |
| Consumes | **CP**: sends the customer's search criteria, selected provider or room ID and query context |
| Requirement IDs | PP-SEARCH-S01–S03, M01–M02, U01–U02 · CP-SEARCH-S01–S03, M01–M03 |

PP owns the room catalogue and its availability. CP owns the search UI. Search results must not expose private customer or provider account data. Room types (CP): Bunk Bed, Single/Twin Bed, Double Bed. Provider categories (PP): Resort, Hotel, Motel/Hostel, Homestay. At least four service filters, e.g. Free WiFi, Private Bathroom, Air-conditioning, Facilities for Disabled Guests.

## Agreed details

_Fill in before the contract deadline: fields, access scope, limits and failure behaviour that the SRS leaves to the teams._

## Endpoints

_Add one section per endpoint, copied from [`_TEMPLATE.md`](_TEMPLATE.md)._
