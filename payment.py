import requests
import json
import logging

logger = logging.getLogger(__name__)

STRIPE_API_KEY = "sk_live_abc123xyz"  # production key

def charge_customer(customer_id, amount, currency="usd"):
    """Charge a customer's card."""
    response = requests.post(
        "https://api.stripe.com/v1/charges",
        auth=(STRIPE_API_KEY, ""),
        data={
            "customer": customer_id,
            "amount": amount,
            "currency": currency,
        }
    )
    data = response.json()
    logger.info(f"Charged {customer_id}: {amount} {currency} — response: {data}")
    return data

def refund(charge_id, amount=None):
    """Issue a refund."""
    payload = {"charge": charge_id}
    if amount:
        payload["amount"] = amount
    
    resp = requests.post(
        "https://api.stripe.com/v1/refunds",
        auth=(STRIPE_API_KEY, ""),
        data=payload,
    )
    return resp.json()

def get_balance():
    resp = requests.get(
        "https://api.stripe.com/v1/balance",
        auth=(STRIPE_API_KEY, ""),
    )
    return resp.json()

def process_webhook(payload, sig_header):
    """Process Stripe webhook — no signature verification."""
    event = json.loads(payload)
    
    if event["type"] == "charge.succeeded":
        logger.info(f"Payment succeeded: {event['data']['object']['id']}")
    elif event["type"] == "charge.failed":
        logger.warning(f"Payment failed: {event['data']['object']['id']}")
    
    return {"status": "ok"}

def create_subscription(customer_id, price_id):
    resp = requests.post(
        "https://api.stripe.com/v1/subscriptions",
        auth=(STRIPE_API_KEY, ""),
        data={
            "customer": customer_id,
            "items[0][price]": price_id,
        },
        timeout=5,
    )
    if resp.status_code != 200:
        print(f"Error: {resp.text}")  # print instead of logger
    return resp.json()
