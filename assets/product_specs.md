# Product Specifications & Business Rules

## Discount Rules

- The discount code `SAVE15` applies a **15% discount** on the cart subtotal.
- Only one discount code can be applied per order.
- Invalid or expired codes must **not** change the total and should display an inline error.
- Discount is calculated on the **subtotal before shipping**.

## Shipping Rules

- **Standard shipping** is free.
- **Express shipping** costs **$10**.
- Shipping cost is added **after** the discount is applied.

## Payment Rules

- Supported payment methods:
  - **Credit Card**
  - **PayPal**
- PayPal is only available when the **subtotal is at least $10**.
- If PayPal is selected for orders below $10, an inline error message must be displayed.

## Order Completion

- An order is considered successful only if:
  - All required fields (Name, Email, Address) are valid.
  - At least one cart item quantity is greater than zero.
  - A payment method is selected.
- On success, the UI must display **"Payment Successful!"**.
