/**
 * Clientside helper functions
 */

let stripe;
let card;

$(document).ready(function() {
  var amounts = document.getElementsByClassName("amount");

  // iterate through all "amount" elements and convert from cents to dollars
  for (var i = 0; i < amounts.length; i++) {
    amount = amounts[i].getAttribute('data-amount') / 100;
    amounts[i].innerHTML = amount.toFixed(2);
  }
});

document.addEventListener("DOMContentLoaded", function () {
  
  stripe = Stripe('pk_test_abc123');  
  const elements = stripe.elements();
  card = elements.create('card');
  card.mount('#card-element');
  const form = document.getElementById('payment-form');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const item = new URLSearchParams(window.location.search).get('item');
    const amount = document.querySelector('.amount')?.dataset.amount || '2000';
    const shippingAddress = {
      line1: document.getElementById('shipping-address').value,
      city: document.getElementById('shipping-city').value,
      state: document.getElementById('shipping-state').value,
      postal_code: document.getElementById('shipping-zip').value
    }
    
    try{
      const { clientSecret } = await fetch('/create-payment-intent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name, email: email, amount: parseInt(amount), item: item, shippingAddress: shippingAddress, metadata: { item: item }})
      }).then(res => res.json());

      const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
        payment_method: {
          card: card,
          billing_details: { name: name, email: email, address: shippingAddress }
        },
      });
      if (error) {
        document.getElementById('error-message').textContent = error.message;
      } else if (paymentIntent.status === 'succeeded') {
        window.location.href = `/success/${paymentIntent.id}`;
      }
    }
    catch (err) {
      console.error('Unexpected error', err);
    document.getElementById('error-message').textContent = 'An unexpected error occurred.';
    }
  });
});
