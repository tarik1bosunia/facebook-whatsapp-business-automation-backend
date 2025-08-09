from langchain_core.tools import BaseTool
from typing import List, Optional, Type
from pydantic import BaseModel, Field, model_validator
from django.db import transaction
from django.utils import timezone
import uuid
import logging

from account.models import User
from customer.models import Customer
from business.models import Product
from customer.models import Order, OrderItem  # Adjust import if your app name differs

logger = logging.getLogger(__name__)

class OrderItemInput(BaseModel):
    product_id: int = Field(..., description="ID of the product to order")
    quantity: int = Field(..., gt=0, description="Quantity of the product")

class OrderConfirmationTool(BaseTool):
    name: str = "order_confirmation_tool"
    description: str = (
        "CONFIRM AND CREATE A NEW ORDER. Requires: "
        "1) List of items with product IDs and quantities. "
        "2) Customer info: either customer_id or (name, phone, city, police_station). "
        "Area is optional. "
        "If any required info is missing, ask for all details at once. "
        "Do not ask one by one."
    )

    _user: User

    def __init__(self, user: User, **kwargs):
        super().__init__(**kwargs)
        self._user = user

    class InputSchema(BaseModel):
        order_items: List[OrderItemInput] = Field(..., description="List of order items")
        customer_id: Optional[int] = Field(None, description="Existing customer ID")
        customer_name: Optional[str] = Field(None, description="Name if new customer")
        customer_phone: Optional[str] = Field(None, description="Phone if new customer")
        customer_city: Optional[str] = Field(None, description="City if new customer")
        customer_police_station: Optional[str] = Field(None, description="Police station if new customer")
        customer_area: Optional[str] = Field(None, description="Area/Street, optional")

        @model_validator(mode="after")
        def validate_customer_info(self):
            if self.customer_id is None:
                required = [self.customer_name, self.customer_phone, self.customer_city, self.customer_police_station]
                if not all(required):
                    raise ValueError(
                        "For new customers, 'customer_name', 'customer_phone', 'customer_city', "
                        "and 'customer_police_station' are required."
                    )
            return self

    args_schema: Type[BaseModel] = InputSchema

    def _run(self, **kwargs) -> str:
        try:
            with transaction.atomic():
                # Get or create customer
                customer = self._get_or_create_customer(
                    user_id=self._user.id,
                    customer_id=kwargs.get('customer_id'),
                    customer_name=kwargs.get('customer_name'),
                    customer_phone=kwargs.get('customer_phone'),
                    customer_city=kwargs.get('customer_city'),
                    customer_police_station=kwargs.get('customer_police_station'),
                    customer_area=kwargs.get('customer_area'),
                )
                if not customer:
                    return "❌ Error: Could not find or create customer. Please provide complete customer details."

                order_items_data = kwargs['order_items']
                if not order_items_data:
                    return "❌ Error: Order items list cannot be empty."

                total_items = 0
                total_price = 0
                products_cache = {}

                # Validate product existence and stock
                for item in order_items_data:
                    product = Product.objects.filter(id=item.product_id, user=self._user).first()
                    if not product:
                        return f"❌ Error: Product with ID {item.product_id} not found."
                    if product.stock < item.quantity:
                        return f"❌ Error: Not enough stock for product '{product.name}'. Available: {product.stock}."
                    products_cache[item.product_id] = product
                    total_items += item.quantity
                    total_price += product.price * item.quantity

                # Create order
                order_number = f"ORD-{timezone.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
                order = Order.objects.create(
                    order_number=order_number,
                    customer=customer,
                    items=total_items,
                    total=total_price,
                    status=Order.Status.PENDING,
                    payment_status=Order.PaymentStatus.PENDING,
                    source=Order.Source.MANUAL,
                )

                # Create order items
                order_items_bulk = [
                    OrderItem(order=order, product=products_cache[item.product_id], quantity=item.quantity)
                    for item in order_items_data
                ]
                OrderItem.objects.bulk_create(order_items_bulk)

                logger.info(f"Order {order_number} created for customer {customer.id}.")

                return (
                    f"✅ Order confirmed!\n"
                    f"Order Number: {order.order_number}\n"
                    f"Customer: {customer.name} (ID: {customer.id})\n"
                    f"Total Items: {order.items}\n"
                    f"Total Price: ${order.total:.2f}\n"
                    f"Status: {order.status}"
                )

        except Exception as e:
            logger.error(f"Order creation failed: {str(e)}", exc_info=True)
            return f"❌ Error: Failed to create order. Reason: {str(e)}"

    def _get_or_create_customer(self, user_id, customer_id, customer_name, customer_phone, customer_city, customer_police_station, customer_area):
        try:
            if customer_id:
                return Customer.objects.get(id=customer_id, user_id=user_id)

            # Try to get by phone or create new
            if customer_phone:
                customer, created = Customer.objects.get_or_create(
                    user_id=user_id,
                    phone=customer_phone,
                    defaults={
                        'name': customer_name,
                        'city': customer_city,
                        'police_station': customer_police_station,
                        'area': customer_area,
                    }
                )
                if created:
                    logger.info(f"New customer created: {customer.name} (ID: {customer.id})")
                return customer

            # fallback: search by name (not reliable)
            if customer_name:
                customer = Customer.objects.filter(user_id=user_id, name__iexact=customer_name).first()
                if customer:
                    return customer

            return None

        except Exception as e:
            logger.error(f"Customer lookup/creation failed: {str(e)}")
            return None

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported.")
