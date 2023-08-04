const stripe = Stripe('pk_test_51NTS1zBe66jbosUcKYhW41mrpWE7edriRzGHtzFrFoJaUKxxlJlkVHjajjizUHBuPEYglszkoFspB4kPyBJwlbjm00jWFy9FoK')

const options = {
    mode: 'subscription',
    amount: 1500,
    currency: 'usd',
    // Fully customizable with appearance API.
    // appearance: {/*...*/},
};
  
// Set up Stripe.js and Elements to use in checkout form
const elements = stripe.elements(options);
  
// Create and mount the Payment Element
const paymentElement = elements.create('payment');
paymentElement.mount('#payment-element');

const form = document.getElementById('payment-form');
const submitBtn = document.getElementById('submit');

const handleError = (error) => {
  const messageContainer = document.querySelector('#error-message');
  messageContainer.textContent = error.message;
  submitBtn.disabled = false;
}

form.addEventListener('submit', async (event) => {
  // We don't want to let default form submission happen here,
  // which would refresh the page.
  event.preventDefault();

  // Prevent multiple form submissions
  if (submitBtn.disabled) {
    return;
  }

  // Disable form submission while loading
  submitBtn.disabled = true;

  // Trigger form validation and wallet collection
  const {error: submitError} = await elements.submit();
  if (submitError) {
    handleError(submitError);
    return;
  }

  // Create the subscription
  const res = await fetch('/create-subscription', {
    method: "POST",
  });
  const {type, clientSecret} = await res.json();
  const confirmIntent = type === "setup" ? stripe.confirmSetup : stripe.confirmPayment;

  // Confirm the Intent using the details collected by the Payment Element
  const {error} = await confirmIntent({
    elements,
    clientSecret,
    confirmParams: {
      return_url: 'https://example.com/order/123/complete',
    },
  });

  if (error) {
    // This point is only reached if there's an immediate error when confirming the Intent.
    // Show the error to your customer (for example, "payment details incomplete").
    handleError(error);
  } else {
    // Your customer is redirected to your `return_url`. For some payment
    // methods like iDEAL, your customer is redirected to an intermediate
    // site first to authorize the payment, then redirected to the `return_url`.
  }
});
