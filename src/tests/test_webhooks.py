import base64
import datetime
import uuid
from typing import Union

import pytest
from pydantic import ValidationError
from standardwebhooks.webhooks import Webhook

from spaire_sdk.models.checkout import Checkout
from spaire_sdk.models.checkoutbillingaddressfields import (
    CheckoutBillingAddressFields,
)
from spaire_sdk.models.billingaddressfieldmode import BillingAddressFieldMode
from spaire_sdk.models.checkoutproduct import CheckoutProduct
from spaire_sdk.models.checkoutstatus import CheckoutStatus
from spaire_sdk.models.paymentprocessor import PaymentProcessor
from spaire_sdk.models.productpricefixed import ProductPriceFixed
from spaire_sdk.models.productpricesource import ProductPriceSource
from spaire_sdk.models.productpricetype import ProductPriceType
from spaire_sdk.models.webhookcheckoutcreatedpayload import WebhookCheckoutCreatedPayload
from spaire_sdk.webhooks import WebhookVerificationError, validate_event

ORGANIZATION_ID = str(uuid.uuid4())
PRODUCT_ID = str(uuid.uuid4())
PRICE_ID = str(uuid.uuid4())

price = ProductPriceFixed(
    id=PRICE_ID,
    created_at=datetime.datetime.now(datetime.timezone.utc),
    modified_at=None,
    is_archived=False,
    product_id=PRODUCT_ID,
    source=ProductPriceSource.CATALOG,
    price_currency="usd",
    price_amount=1000,
    type=ProductPriceType.ONE_TIME,
    recurring_interval=None,
)

product = CheckoutProduct(
    id=PRODUCT_ID,
    created_at=datetime.datetime.now(datetime.timezone.utc),
    modified_at=None,
    name="Product",
    description=None,
    is_recurring=False,
    is_archived=False,
    organization_id=ORGANIZATION_ID,
    recurring_interval=None,
    recurring_interval_count=None,
    trial_interval=None,
    trial_interval_count=None,
    prices=[price],
    benefits=[],
    medias=[],
)

billing_address_fields = CheckoutBillingAddressFields(
    country=BillingAddressFieldMode.REQUIRED,
    state=BillingAddressFieldMode.DISABLED,
    city=BillingAddressFieldMode.DISABLED,
    postal_code=BillingAddressFieldMode.DISABLED,
    line1=BillingAddressFieldMode.DISABLED,
    line2=BillingAddressFieldMode.DISABLED,
)

checkout_created = WebhookCheckoutCreatedPayload(
    TYPE="checkout.created",
    timestamp=datetime.datetime.now(datetime.timezone.utc),
    data=Checkout(
        id=str(uuid.uuid4()),
        created_at=datetime.datetime.now(datetime.timezone.utc),
        modified_at=None,
        status=CheckoutStatus.OPEN,
        client_secret="CLIENT_SECRET",
        url="https://example.com/checkout/CLIENT_SECRET",
        expires_at=datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=1),
        success_url="https://example.com/checkout/CLIENT_SECRET/confirmation",
        return_url=None,
        embed_origin=None,
        tax_amount=0,
        amount=0,
        discount_amount=0,
        currency="usd",
        net_amount=1000,
        total_amount=1000,
        allow_trial=None,
        active_trial_interval=None,
        active_trial_interval_count=None,
        trial_end=None,
        organization_id=ORGANIZATION_ID,
        product_id=PRODUCT_ID,
        product_price_id=PRICE_ID,
        discount_id=None,
        allow_discount_codes=True,
        is_discount_applicable=True,
        is_free_product_price=False,
        is_payment_required=True,
        is_payment_setup_required=False,
        is_payment_form_required=True,
        customer_id=None,
        customer_name=None,
        customer_email=None,
        customer_ip_address=None,
        customer_billing_address=None,
        customer_tax_id=None,
        payment_processor_metadata={},
        billing_address_fields=billing_address_fields,
        trial_interval=None,
        trial_interval_count=None,
        metadata={},
        external_customer_id=None,
        customer_external_id=None,
        product=product,
        products=[product],
        product_price=price,
        prices=None,
        discount=None,
        subscription_id=None,
        attached_custom_fields=[],
        custom_field_data=None,
        payment_processor=PaymentProcessor.STRIPE,
        customer_metadata={},
        require_billing_address=False,
        is_business_customer=False,
        customer_billing_name=None,
    ),
)

WEBHOOK_SECRET = "TestSecret"
WEBHOOK_SECRET_BASE64 = base64.b64encode(WEBHOOK_SECRET.encode()).decode()


def get_headers(
    body: str,
    webhook_id: str = "WEBHOOK_ID",
    timestamp: Union[datetime.datetime, None] = None,
) -> dict[str, str]:
    timestamp = timestamp or datetime.datetime.now(datetime.timezone.utc)
    signature = Webhook(WEBHOOK_SECRET_BASE64).sign(webhook_id, timestamp, body)
    return {
        "webhook-id": webhook_id,
        "webhook-signature": signature,
        "webhook-timestamp": str(timestamp.timestamp()),
    }


def test_valid_signature() -> None:
    body = checkout_created.model_dump_json(by_alias=True)
    headers = get_headers(body)

    payload = validate_event(body, headers, WEBHOOK_SECRET)
    assert payload == checkout_created


def test_invalid_signature() -> None:
    body = checkout_created.model_dump_json(by_alias=True)
    headers = get_headers(body)

    with pytest.raises(WebhookVerificationError):
        validate_event(body, headers, "AnotherSecret")


def test_invalid_payload() -> None:
    body = '{"type": "unknown"}'
    headers = get_headers(body)

    with pytest.raises(ValidationError):
        validate_event(body, headers, WEBHOOK_SECRET)
