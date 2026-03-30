"""
Stripe Integration for Botwave
Handles subscription payments for the business platform
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Try to import stripe
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    logger.warning("Stripe library not installed. Run: pip install stripe")


class StripeService:
    """Stripe payment service for subscriptions."""

    def __init__(self):
        self.api_key = os.getenv("STRIPE_SECRET_KEY", "")
        self.publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

        if STRIPE_AVAILABLE and self.api_key:
            stripe.api_key = self.api_key
            self._configured = True
        else:
            self._configured = False

    def is_configured(self) -> bool:
        """Check if Stripe is properly configured."""
        return self._configured and bool(self.api_key)

    def create_customer(self, email: str, name: str = None) -> Optional[Dict]:
        """Create a new Stripe customer."""
        if not self.is_configured():
            logger.error("Stripe not configured")
            return None

        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={"source": "botwave"}
            )
            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name
            }
        except Exception as e:
            logger.error(f"Failed to create customer: {e}")
            return None

    def create_checkout_session(
        self,
        success_url: str,
        cancel_url: str,
        line_items: list = None,
        mode: str = "subscription",
        customer_email: str = None
    ) -> Optional[Dict]:
        """Create a Stripe checkout session."""
        if not self.is_configured():
            logger.error("Stripe not configured")
            return None

        # Default line items for Professional plan
        if not line_items:
            price_id = os.getenv("STRIPE_PRICE_ID_PROFESSIONAL")
            if not price_id:
                logger.error("No price ID configured")
                return None
            line_items = [{"price": price_id, "quantity": 1}]

        try:
            session_params = {
                "success_url": success_url,
                "cancel_url": cancel_url,
                "line_items": line_items,
                "mode": mode,
            }

            if customer_email:
                session_params["customer_email"] = customer_email

            session = stripe.checkout.Session.create(**session_params)

            return {
                "id": session.id,
                "url": session.url,
                "customer_email": session.customer_details.email if session.customer_details else None
            }
        except Exception as e:
            logger.error(f"Failed to create checkout session: {e}")
            return None

    def get_subscription(self, subscription_id: str) -> Optional[Dict]:
        """Get subscription details."""
        if not self.is_configured():
            return None

        try:
            sub = stripe.Subscription.retrieve(subscription_id)
            return {
                "id": sub.id,
                "status": sub.status,
                "current_period_end": sub.current_period_end,
                "plan": sub.plan.nickname if sub.plan else None
            }
        except Exception as e:
            logger.error(f"Failed to get subscription: {e}")
            return None

    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a subscription."""
        if not self.is_configured():
            return False

        try:
            stripe.Subscription.delete(subscription_id)
            return True
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {e}")
            return False

    def verify_webhook(self, payload: bytes, sig_header: str) -> Optional[Dict]:
        """Verify and parse a webhook event."""
        if not self.webhook_secret:
            logger.error("Webhook secret not configured")
            return None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            return {
                "type": event["type"],
                "data": event["data"]["object"]
            }
        except Exception as e:
            logger.error(f"Webhook verification failed: {e}")
            return None


# Singleton instance
stripe_service = StripeService()


# For backwards compatibility
def create_checkout_session(plan: str, customer_email: str = None) -> Optional[Dict]:
    """Legacy function for checkout session creation."""
    price_ids = {
        "starter": os.getenv("STRIPE_PRICE_ID_STARTER"),
        "professional": os.getenv("STRIPE_PRICE_ID_PROFESSIONAL")
    }

    price_id = price_ids.get(plan)
    if not price_id:
        return None

    return stripe_service.create_checkout_session(
        success_url="http://localhost:5000/checkout/success",
        cancel_url="http://localhost:5000/checkout/canceled",
        line_items=[{"price": price_id, "quantity": 1}],
        customer_email=customer_email
    )