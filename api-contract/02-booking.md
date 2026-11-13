# Booking creation, eligibility and outcomes

| | |
| --- | --- |
| Provides | **PP**: stores and reserves bookings, booking references, review eligibility, receptionist approval or cancellation, inventory outcomes |
| Consumes | **CP**: sends customer and membership details, selected room, dates, room quantity and adult/child counts |
| Requirement IDs | PP-BOOK-S01–S02, U01 · PP-ROOM-M02, U02 · CP-BOOK-S01–S02 |

Requested rooms stay reserved while pending receptionist approval, with no automatic expiry. Room quantity must be ≤ adults + children. Only the receptionist (the provider account) approves; the customer or the receptionist may cancel. PP must also supply the stay dates CP needs to allow a review from the first day of the stay. At Ultimo, booking requests must keep working through a redundant PP booking service.

## Agreed details

_Fill in before the contract deadline: fields, access scope, limits and failure behaviour that the SRS leaves to the teams._

## Endpoints

_Add one section per endpoint, copied from [`_TEMPLATE.md`](_TEMPLATE.md)._
