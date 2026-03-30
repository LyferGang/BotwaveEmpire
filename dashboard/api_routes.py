"""
Dashboard API Routes - Stripe Integration
Payment and subscription endpoints for Botwave business platform
"""

import os
from flask import Blueprint, request, jsonify, session
from integrations.stripe_integration import stripe_service

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create a Stripe checkout session for a subscription plan."""
    data = request.json or {}
    plan = data.get('plan', 'professional')

    # Plan configuration - update with your actual Stripe Price IDs
    PLANS = {
        'starter': {
            'price_id': os.getenv('STRIPE_PRICE_ID_STARTER', 'price_xxxxx_starter'),
            'amount': 4900,  # $49.00 in cents
            'name': 'Starter Plan'
        },
        'professional': {
            'price_id': os.getenv('STRIPE_PRICE_ID_PROFESSIONAL', 'price_xxxxx_pro'),
            'amount': 14900,  # $149.00 in cents
            'name': 'Professional Plan'
        }
    }

    if plan not in PLANS:
        return jsonify({'error': 'Invalid plan'}), 400

    plan_config = PLANS[plan]

    try:
        checkout_data = stripe_service.create_checkout_session(
            success_url=f"{request.host_url}checkout/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{request.host_url}checkout/canceled",
            line_items=[{
                'price': plan_config['price_id'],
                'quantity': 1
            }]
        )

        return jsonify({
            'session_id': checkout_data['id'],
            'url': checkout_data['url']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    """Create a Stripe payment intent for one-time payments."""
    data = request.json or {}
    amount = data.get('amount', 4900)  # Default $49.00
    description = data.get('description', 'Botwave Service Payment')

    try:
        intent_data = stripe_service.create_payment_intent(
            amount=amount,
            currency='usd',
            description=description
        )

        return jsonify(intent_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/subscriptions', methods=['GET'])
def list_subscriptions():
    """List subscriptions for a customer."""
    customer_id = request.args.get('customer_id')

    if not customer_id:
        return jsonify({'error': 'customer_id required'}), 400

    try:
        subscriptions = stripe_service.list_subscriptions(customer_id)
        return jsonify({'subscriptions': subscriptions})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/cancel-subscription', methods=['POST'])
def cancel_subscription():
    """Cancel a subscription."""
    data = request.json or {}
    subscription_id = data.get('subscription_id')

    if not subscription_id:
        return jsonify({'error': 'subscription_id required'}), 400

    try:
        result = stripe_service.cancel_subscription(subscription_id)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events."""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    event = stripe_service.verify_webhook_signature(payload, sig_header)

    if not event:
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle different event types
    event_type = event.get('type')

    if event_type == 'checkout.session.completed':
        # Payment successful - activate the service
        session_data = event.get('data', {}).get('object', {})
        customer_id = session_data.get('customer')
        # TODO: Activate customer subscription in your database

    elif event_type == 'customer.subscription.deleted':
        # Subscription canceled - deactivate service
        subscription_data = event.get('data', {}).get('object', {})
        customer_id = subscription_data.get('customer')
        # TODO: Deactivate customer subscription in your database

    return jsonify({'status': 'success'})


@api.route('/stripe-status', methods=['GET'])
def stripe_status():
    """Check Stripe configuration status."""
    return jsonify({
        'configured': stripe_service.is_configured(),
        'has_secret_key': bool(stripe_service.api_key),
        'has_publishable_key': bool(stripe_service.publishable_key),
        'has_webhook_secret': bool(stripe_service.webhook_secret)
    })
