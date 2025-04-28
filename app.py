import os
import stripe

from dotenv import load_dotenv
from flask import Flask, request, render_template, jsonify

load_dotenv()

app = Flask(__name__,
  static_url_path='',
  template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "views"),
  static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "public"))

stripe.api_key = 'sk_test_abc123'

ITEMS = {
  '1': {'title': 'The Art of Doing Science and Engineering', 'price': 2300},
  '2': {'title': 'The Making of Prince of Persia: Journals 1985-1993', 'price': 2500},
  '3': {'title': 'Working in Public: The Making and Maintenance of Open Source', 'price': 2800}
}

# Home route
@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')

# Checkout route
@app.route('/checkout', methods=['GET'])
def checkout():
  # Just hardcoding amounts here to avoid using a database
  item = request.args.get('item')
  email = request.args.get('email')
  title = None
  amount = None
  error = None

  if item == '1':
    title = 'The Art of Doing Science and Engineering'
    amount = 2300
  elif item == '2':
    title = 'The Making of Prince of Persia: Journals 1985-1993'
    amount = 2500
  elif item == '3':
    title = 'Working in Public: The Making and Maintenance of Open Source'
    amount = 2800
  else:
    # Included in layout view, feel free to assign error
    error = 'No item selected'

  return render_template('checkout.html', title=title, amount=amount, error=error, item=item, email=email)

#Payment Route
@app.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
  try:
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    item_id = data.get('item')
    item = ITEMS.get(item_id)
    title = item['title']
    amount = item['price']
    print(title)
    shipping_address = data.get('shippingAddress')
    intent = stripe.PaymentIntent.create(
      amount = amount,
      currency = 'sgd',
      receipt_email = email,
      shipping = {
        'name': name,
        'address': {
          'line1': shipping_address.get('line1'),
          'city': shipping_address.get('city'),
          'state': shipping_address.get('state'),
          'postal_code': shipping_address.get('postal_code'),
        }
      },
      metadata = {
        'name': name,
        'email': email,
        'item_id': item_id,
        'item_title': title,
        'shipping_line1': shipping_address.get('line1'),
        'shipping_city': shipping_address.get('city'),
        'shipping_state': shipping_address.get('state'),
        'shipping_postal_code': shipping_address.get('postal_code'),
      }
    )
    return jsonify({'clientSecret': intent.client_secret})
  except Exception as e:
    return jsonify(error=str(e)), 403

@app.route('/success/<payment_intent_id>')
def success(payment_intent_id):
  try:
    intent = stripe.PaymentIntent.retrieve(
      payment_intent_id,
      expand = ['latest_charge']
      )
    
    charge = intent.latest_charge
    email = charge.billing_details.email
    amount = intent.amount
    currency = intent.currency.upper()
    item = intent.metadata.get('item_title')
    shipping_address = (
      f"{intent.metadata.get('shipping_line1')}, "
      f"{intent.metadata.get('shipping_city')}, "
      f"{intent.metadata.get('shipping_state')}, "
      f"{intent.metadata.get('shipping_postal_code')}"
    )

    return render_template(
      'success.html', 
      payment_intent_id = payment_intent_id,
      email = email,
      amount = amount,
      currency = currency,
      item = item,
      shipping_address = shipping_address
      )
  except Exception as e:
    return f"Error retrieve payment: {str(e)}", 500

if __name__ == '__main__':
  app.run(port=5000, host='0.0.0.0', debug=True)