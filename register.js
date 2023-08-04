const emailInput = document.querySelector('#email');

fetch('/create-customer', {
  method: 'post',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: emailInput.value,
  }),
}).then(r => r.json());