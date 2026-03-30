"""
Stripe Integration for Botwave Business Platform
Handles payments, subscriptions, and invoicing for service business automation.

Contact: Kyle Jimenez - botwave1904@gmail.com
"""

import os
import stripe
from typing import Dict, Any, Optional, List
from datetime import datetime
from core.config import Config


class StripeService:
    """
    Stripe payment integration for Botwave business platform.

    Features:
    - Payment processing
    - Subscription management
    - Invoice generation
    - Customer management
    """

    def __init__(self):
        self.api_key = os.getenv("STRIPE_SECRET_KEY")
        self.publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        if self.api_key and not self.api_key.startswith("sk_live_") and not self.api_key.startswith("sk_test_"):
            raise ValueError("Invalid Stripe secret key format")

        stripe.api_key = self.api_key

    def is_configured(self) -> bool:
        """Check if Stripe is properly configured."""
        return bool(self.api_key and not self.api_key.startswith("sk_live_") and not self.api_key.startswith("sk_test_"))

    def create_customer(self, email: str, name: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new Stripe customer."""
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata=metadata or {}
        )
        return {
            "id": customer.id,
            "email": customer.email,
            "name": customer.name,
            "created": datetime.fromtimestamp(customer.created).isoformat()
        }

    def create_payment_intent(self, amount: int, currency: str = "usd", customer_id: Optional[str] = None,
                              description: str = "Botwave Service Payment") -> Dict[str, Any]:
        """
        Create a payment intent.

        Args:
            amount: Amount in cents (e.g., 1000 = $10.00)
            currency: Three-letter ISO currency code
            customer_id: Optional Stripe customer ID
            description: Payment description
        """
        params = {
            "amount": amount,
            "currency": currency,
            "description": description,
            "automatic_payment_methods": {"enabled": True}
        }
        if customer_id:
            params["customer"] = customer_id

        intent = stripe.PaymentIntent.create(**params)
        return {
            "id": intent.id,
            "client_secret": intent.client_secret,
            "amount": intent.amount,
            "currency": intent.currency,
            "status": intent.status
        }

    def create_subscription(self, customer_id: str, price_id: str, trial_days: int = 0) -> Dict[str, Any]:
        """
        Create a subscription for a customer.

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID for the subscription
            trial_days: Number of trial days (0 = no trial)
        """
        subscription_params = {
            "customer": customer_id,
            "items": [{"price": price_id}],
        }

        if trial_days > 0:
            subscription_params["trial_period_days"] = trial_days

        subscription = stripe.Subscription.create(**subscription_params)
        return {
            "id": subscription.id,
            "customer_id": subscription.customer,
            "status": subscription.status,
            "current_period_start": datetime.fromtimestamp(subscription.current_period_start).isoformat(),
            "current_period_end": datetime.fromtimestamp(subscription.current_period_end).isoformat(),
            "trial_end": datetime.fromtimestamp(subscription.trial_end).isoformat() if subscription.trial_end else None
        }

    def create_invoice(self, customer_id: str, items: List[Dict], description: str = "Botwave Services") -> Dict[str, Any]:
        """
        Create an invoice for a customer.

        Args:
            customer_id: Stripe customer ID
            items: List of invoice items with amount and description
            description: Invoice description
        """
        invoice = stripe.Invoice.create(
            customer=customer_id,
            description=description
        )

        for item in items:
            stripe.InvoiceItem.create(
                customer=customer_id,
                amount=item["amount"],
                currency=item.get("currency", "usd"),
                description=item["description"]
            )

        return {
            "id": invoice.id,
            "customer_id": invoice.customer,
            "amount_due": invoice.amount_due,
            "status": invoice.status,
            "invoice_pdf": invoice.invoice_pdf
        }

    def list_subscriptions(self, customer_id: str) -> List[Dict[str, Any]]:
        """List all subscriptions for a customer."""
        subscriptions = stripe.Subscription.list(customer=customer_id)
        return [
            {
                "id": sub.id,
                "status": sub.status,
                "current_period_end": datetime.fromtimestamp(sub.current_period_end).isoformat()
            }
            for sub in subscriptions.data
        ]

    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription."""
        subscription = stripe.Subscription.delete(subscription_id)
        return {
            "id": subscription.id,
            "status": "canceled",
            "canceled_at": datetime.fromtimestamp(subscription.ended_at).isoformat() if subscription.ended_at else None
        }

    def get_checkout_session(self, session_id: str) -> Dict[str, Any]:
        """Retrieve a checkout session."""
        session = stripe.checkout.Session.retrieve(session_id)
        return {
            "id": session.id,
            "customer_id": session.customer,
            "payment_status": session.payment_status,
            "amount_total": session.amount_total,
            "currency": session.currency
        }

    def create_checkout_session(self, success_url: str, cancel_url: str,
                                line_items: List[Dict], customer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a checkout session.

        Args:
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect after canceled payment
            line_items: List of items with price_id and quantity
            customer_id: Optional Stripe customer ID
        """
        params = {
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": line_items,
            "mode": "payment",
            "automatic_tax": {"enabled": True}
        }
        if customer_id:
            params["customer"] = customer_id

        session = stripe.checkout.Session.create(**params)
        return {
            "id": session.id,
            "url": session.url,
            "payment_status": session.payment_status
        }

    def verify_webhook_signature(self, payload: bytes, sig_header: str) -> Optional[Dict[str, Any]]:
        """Verify webhook signature and return event."""
        if not self.webhook_secret:
            return None

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, self.webhook_secret)
            return event
        except (ValueError, stripe.error.SignatureVerificationError):
            return None


# Global instance
stripe_service = StripeService()
