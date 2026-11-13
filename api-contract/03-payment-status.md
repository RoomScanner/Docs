# Monetary order and status

| | |
| --- | --- |
| Provides | **PP**: approval or cancellation outcome and the status of the separate return payout (Medium), or escrow release/refund (Ultimo) |
| Consumes | **CP**: simulated order (Simplex), sandbox payment reference sent before the booking order (Medium), captured-and-held payment reference (Ultimo), customer cancellation requests |
| Requirement IDs | PP-MONEY-S01, M01–M03, U01 · CP-MONEY-S01, M01–M03, U01–U04 |

CP is the payer, PP is the beneficiary. Approval must never charge the customer a second time. At Medium, cancelling a paid booking triggers a separate provider-to-customer payout, not the original payment's refund API; report pending, failed and successful payouts separately, with the payment provider's failure cause when available, and keep both payment references. At Ultimo, escrow replaces this for the affected bookings.

## Agreed details

_Fill in before the contract deadline: fields, access scope, limits and failure behaviour that the SRS leaves to the teams._

## Endpoints

_Add one section per endpoint, copied from [`_TEMPLATE.md`](_TEMPLATE.md)._
