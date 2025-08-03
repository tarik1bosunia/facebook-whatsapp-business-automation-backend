from langchain_core.tools import BaseTool
from typing import List, Type, Optional
from pydantic import BaseModel, Field, PrivateAttr, model_validator # ✅ Use model_validator
from customer.models import Order, Customer
from django.db import models
from django.utils import timezone
import uuid
import logging
from account.models import User
from business.models import Product
from django.db import transaction

logger = logging.getLogger(__name__)

# ✅ Pydantic model for individual order items
class OrderItem(BaseModel):
    product_name: str = Field(..., description="The name of the product to be ordered.")
    quantity: int = Field(..., description="The number of items of this product.")
    
    # ✅ Pydantic V2 style model_validator
    @model_validator(mode='after')
    def check_positive_quantity(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")
        return self

class OrderConfirmationTool(BaseTool):
    """
    A tool to confirm and add a new order to the system.
    This tool is used by the agent to create a new order after a customer has
    confirmed their purchase and provided all necessary details.
    """
    
    name: str = "order_confirmation_tool"
    description: str = (
        "CONFIRM AND CREATE A NEW ORDER. Use this tool ONLY when the user explicitly "
        "wants to finalize a purchase. It requires a list of items to be ordered, each with a 'product_name' "
        "and a 'quantity'. The tool will automatically look up the product prices, "
        "calculate the total cost, and generate a unique order number. "
        "The customer can be identified by an existing 'customer_id' or, if new, by "
        "providing a 'customer_name' (mandatory for new customers), and optionally "
        "'customer_phone' and 'customer_email'. "
        "Do not use this tool for general inquiries; use it strictly for creating confirmed orders."
    )

    _user: User = PrivateAttr()

    def __init__(self, user: User, **kwargs):
        super().__init__(**kwargs)
        self._user = user
    
    class InputSchema(BaseModel):
        order_items: List[OrderItem] = Field(
            ...,
            description="A list of products to order, each with a product name and quantity."
        )
        customer_id: Optional[int] = Field(
            None,
            description="The ID of an existing customer. If not provided, a new customer will be created using 'customer_name'."
        )
        customer_name: Optional[str] = Field(
            None,
            description="The name of the customer. Required if 'customer_id' is not provided and a new customer needs to be created."
        )
        customer_phone: Optional[str] = Field(
            None,
            description="The phone number of the customer. Recommended for new customers."
        )
        customer_email: Optional[str] = Field(
            None,
            description="The email address of the customer. Recommended for new customers."
        )
        status: Optional[str] = Field(
            Order.Status.PENDING,
            description="The current status of the order. Defaults to 'pending'."
        )
        payment_status: Optional[str] = Field(
            Order.PaymentStatus.PENDING,
            description="The current payment status of the order. Defaults to 'pending'."
        )
        source: Optional[str] = Field(
            Order.Source.MANUAL,
            description="The source from which the order was placed. Defaults to 'manual'."
        )
    
    args_schema: Type[BaseModel] = InputSchema
    
    def _run(
        self, 
        order_items: List[OrderItem], 
        customer_id: Optional[int] = None,
        customer_name: Optional[str] = None,
        customer_phone: Optional[str] = None,
        customer_email: Optional[str] = None,
        status: str = Order.Status.PENDING,
        payment_status: str = Order.PaymentStatus.PENDING,
        source: str = Order.Source.MANUAL
    ) -> str:
        """
        Creates a new order in the database, creating the customer first if needed.
        """
        try:
            with transaction.atomic():
                customer = self._get_or_create_customer(
                    user_id=self._user.id,
                    customer_id=customer_id,
                    customer_name=customer_name,
                    customer_phone=customer_phone,
                    customer_email=customer_email
                )
                if not customer:
                    return f"❌ Error: Could not find or create a customer. 'customer_name' is required if 'customer_id' is not provided."
                
                order_total = 0
                total_items = 0
                for item in order_items:
                    product = Product.objects.filter(name__icontains=item.product_name, user=self._user).first()
                    if not product:
                        return f"❌ Error: Product '{item.product_name}' not found in the catalog. Please try a different product name."
                    
                    if product.stock < item.quantity:
                        return f"❌ Error: Not enough stock for '{product.name}'. Available stock: {product.stock}."
                    
                    order_total += product.price * item.quantity
                    total_items += item.quantity

                order_number = f"ORD-{timezone.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
                
                new_order = Order.objects.create(
                    order_number=order_number,
                    customer=customer,
                    items=total_items,
                    total=order_total,
                    status=status,
                    payment_status=payment_status,
                    source=source
                )
                
                logger.info(f"New order created: {new_order.order_number} for customer ID {customer.id}")
            
            return (
                f"✅ Order confirmed and created successfully!\n"
                f"Order Number: {new_order.order_number}\n"
                f"Customer: {customer.name} (ID: {customer.id})\n"
                f"Total Items: {new_order.items}\n"
                f"Total: ${new_order.total:.2f}\n"
                f"Status: {new_order.status}\n"
                f"Payment Status: {new_order.payment_status}"
            )
            
        except Exception as e:
            logger.error(
                f"Failed to create order: {str(e)}", 
                exc_info=True
            )
            return f"❌ Error: Failed to create the order. Reason: {str(e)}"
    
    def _get_or_create_customer(self, user_id: int, customer_id: Optional[int], customer_name: Optional[str], customer_phone: Optional[str], customer_email: Optional[str]) -> Optional[Customer]:
        """Helper method to find or create a customer."""
        try:
            if customer_id:
                return Customer.objects.get(id=customer_id)
            
            elif customer_name:
                customer_qs = Customer.objects.filter(user_id=user_id).filter(
                    models.Q(name__iexact=customer_name) |
                    models.Q(email__iexact=customer_email) |
                    models.Q(phone=customer_phone)
                ).distinct()

                if customer_qs.exists():
                    return customer_qs.first()
                
                user = User.objects.get(id=user_id)
                new_customer = Customer.objects.create(
                    user=user,
                    name=customer_name,
                    phone=customer_phone,
                    email=customer_email
                )
                logger.info(f"New customer created automatically: {new_customer.name} (ID: {new_customer.id})")
                return new_customer
            
            else:
                return None
        
        except (Customer.DoesNotExist, User.DoesNotExist) as e:
            logger.error(f"Error finding/creating customer: {str(e)}")
            return None

    def _arun(self, *args, **kwargs):
        """Async version not implemented."""
        raise NotImplementedError("Async operation not supported")