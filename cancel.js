function cancelSubscription(subscriptionId) {
    return fetch('/cancel-subscription', {
      method: 'post',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        subscriptionId: subscriptionId,
      }),
    })
      .then(response => {
        return response.json();
      })
      .then(cancelSubscriptionResponse => {
        // Display to the user that the subscription has been canceled.
      });
  }