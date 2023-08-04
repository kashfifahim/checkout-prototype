import stripe
stripe.api_key = "sk_test_51NTS1zBe66jbosUcuLJb56SKhnfxdf83I3ilopgQQwLg07wqN2orHaqPYCSHC9mey3bp5WrpL5tLSuXOE7XqiuNk00dx0qPbc0"

stripe.Customer.create(
    email="{{CUSTOMER_EMAIL}}",
    name="{{CUSTOMER_NAME}}",
)

@app.route('/create-subscription', methods=['POST'])
def create_subscription():
  data = json.loads(request.data)
  customer_id = data['customerId']
  price_id = data['priceId']

  try:
    # Create the subscription. Note we're expanding the Subscription's
    # latest invoice and that invoice's payment_intent
    # so we can pass it to the front end to confirm the payment
    subscription = stripe.Subscription.create(
      customer=customer_id,
      items=[{
        'price': price_id,
      }],
      payment_behavior='default_incomplete',
      payment_settings={'save_default_payment_method': 'on_subscription'},
      expand=['latest_invoice.payment_intent', 'pending_setup_intent'],
    )
    if subscription.pending_setup_intent is not None:
      return jsonify(type='setup', clientSecret=subscription.pending_setup_intent.client_secret)
    else:
      return jsonify(type='payment', clientSecret=subscription.latest_invoice.payment_intent.client_secret)

  except Exception as e:
    return jsonify(error={'message': e.user_message}), 400  

@app.route('/webhook', methods=['POST'])
def webhook_received():
    # You can use webhooks to receive information about asynchronous payment events.
    # For more about our webhook events check out https://stripe.com/docs/webhooks.
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    request_data = json.loads(request.data)

    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']

    data_object = data['object']

    if event_type == 'invoice.paid':
        # Used to provision services after the trial has ended.
        # The status of the invoice will show up as paid. Store the status in your
        # database to reference when a user accesses your service to avoid hitting rate
        # limits.
        print(data)

    if event_type == 'invoice.payment_failed':
        # If the payment fails or the customer does not have a valid payment method,
        # an invoice.payment_failed event is sent, the subscription becomes past_due.
        # Use this webhook to notify your user that their payment has
        # failed and to retrieve new card details.
        print(data)

    if event_type == 'customer.subscription.deleted':
        # handle subscription canceled automatically based
        # upon your subscription settings. Or if the user cancels it.
        print(data)

    return jsonify({'status': 'success'})

@app.route('/cancel-subscription', methods=['POST'])
def cancelSubscription():
    data = json.loads(request.data)
    try:
         # Cancel the subscription by deleting it
        deletedSubscription = stripe.Subscription.delete(data['subscriptionId'])
        return jsonify(deletedSubscription)
    except Exception as e:
        return jsonify(error=str(e)), 403