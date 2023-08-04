# Checkout-Prototype Using Stripe
A checkout experience prototype for automation packages using Stripe APIs

## 1st Iteration:
- Model the business by building a product catalog
- Build a registration process that creates a customer
- Create a subscription and collect payment information
- Test and monitor payment and subscription status
- Let customers change their plan or cancel the subscription

### To Create and Activate a Subscription
- First create a Product to model what is being sold
- Next create a Price which determines the interval and amount to charge
- Also need a Customer to store PaymentMentods used to make each recurring payment

### 1: Set up Stripe
Stripe clinet for Python
`pip3 install --upgrade stripe`
Stripe CLI, provides webhook testing and run it tom ake API calls to Stripe

### 2: Create the pricing model
- Create products and their prices with the Stripe CLI
  - {
      "id": "prod_ONwX1qWpt6p9Ki",
      "object": "product",
      "active": true,
      "attributes": [],
      "created": 1691104164,
      "default_price": null,
      "description": null,
      "images": [],
      "livemode": false,
      "metadata": {},
      "name": "KeyMapPro",
      "package_dimensions": null,
      "shippable": null,
      "statement_descriptor": null,
      "tax_code": null,
      "type": "service",
      "unit_label": null,
      "updated": 1691104164,
      "url": null
    }
- Record the product ID for each product
  - prod_ONwX1qWpt6p9Ki
- Use the product ID to create a price for each product
  - `kashfi$ stripe prices create -d product=prod_ONwX1qWpt6p9Ki -d unit_amount=1500 -d currency=usd -d 'recurring[interval]'=month`
  {
  "id": "price_1NbPLEBe66jbosUcwKK9Vcje",
  "object": "price",
  "active": true,
  "billing_scheme": "per_unit",
  "created": 1691160660,
  "currency": "usd",
  "custom_unit_amount": null,
  "livemode": false,
  "lookup_key": null,
  "metadata": {},
  "nickname": null,
  "product": "prod_ONwX1qWpt6p9Ki",
  "recurring": {
    "aggregate_usage": null,
    "interval": "month",
    "interval_count": 1,
    "trial_period_days": null,
    "usage_type": "licensed"
  },
  "tax_behavior": "unspecified",
  "tiers_mode": null,
  "transform_quantity": null,
  "type": "recurring",
  "unit_amount": 1500,
  "unit_amount_decimal": "1500"
}
- The `unit_amount` number is in cents
- Record the price ID for each price. We can use them later.
  - price_1NbPLEBe66jbosUcwKK9Vcje

### 3 Create the customer
- Stripe needs a customer for each subscription.
- In our frontend we have to collect the necessary information from the user and pass it to the backend
- see `register.html`, `register.js`
- `server.py` uses the data to create `customer` via Stripe API call

### 3b Collect Payment Details (client-side)
- The Payment Element is a prebuilt UI Component that simplifies collecting payment details
- The Payment Element contains an iframe that securely sends payment information to Stripe over HTTPS connection
- Do not place the Payement Element within another iframe because some payment methods require redirecting to another page for payment confirmation
- The checkout page address must start with `https://` for the integration to work.
- We can test the integration without using HTTPS

#### Set up Stripe.js
- The Payment Element is automatically available as a feature of Stripe.js. 
- Include the Stripe.js script on your checkout page by adding it to the `head` of your HTML file
- Always load Stripe.js directly from js.stripe.com to remain PCI compliant
- `checkout.html`, `checkout.js`

### 4 Create the subscription
- Let new customer choose and then create the subscription
- Frontend, `price.js` pass the price Id and the ID of the customer record to the backend
- Backend, create the subscription with status `incomplete` using `payment_behavior=default_incomplete`
  - Return the `client_secret` from the subscription's first `payment intent` to the frontend to complete payment
- Set `save_default_payment_method` to `on_subscription` to save the payment method as the default for a subscription when a payment succeeds
  - Increases the success rate of future subscription payments
- At this point the Subscription is inactive and awaiting payment. 

### 5 Collect Payment Information
- `subscribe.html`
- Set up Stripe Elements in `subscribe.html`
- Create an instance of Stripe with subscribe.js on checkout page
- Add the Payment Element to your page

### 6 Listen for Webhooks
- To complete the integration we need to process webhooks sent by Stripe
 - events triggered whenever state inside of Stripe changes
- Set up an HTTP handler to accept POST request containing the webhook event and verify the signature of the event
- During develoment use Stripe CLI to observe webhooks and forward them to your application
 - `stripe listen --forward-to localhost:4242/webhook`
- For production, set up a webhook endpoint using Webhook Endpoints API

### 7 Provision Access to Your Servive
- Subscription is active, give your user access to your service.
 - Listen to `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted` events
  - These events pass a `subscription` object which contains a status field indicating whether the subscription is active. past due, or canceled.

### 8 Cancel the Subscription (Client and Server)
- `script.js`
- `server.py`
