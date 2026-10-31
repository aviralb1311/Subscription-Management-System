# DATABASE_DESIGN.md
*PostgreSQL Schema Design*

## Core Entities
- User, Role, Permission, UserRole
- Customer
- Product, ProductVariant
- Plan, PlanVersion
- Quotation, QuotationLine
- Subscription, SubscriptionLine
- Invoice, InvoiceLine, CreditNote
- Payment, PaymentAllocation
- DiscountRule, DiscountRedemption
- TaxRule
- Notification, BackgroundJob, AuditLog

## Financial Requirements
- All monetary fields use DECIMAL(12,2)
- Invoice lines immutable after confirmation
- Payment allocations with CHECK constraints
- Historical snapshots on all line items
- Idempotency keys on critical operations
- Billing periods tracked (start/end dates)

## Constraints
- CHECK constraints on amounts > 0
- Foreign keys with appropriate actions
- Unique constraints on numbers and keys
- Indexes for performance
