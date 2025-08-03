from langchain_core.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field, PrivateAttr
from customer.models import Order, Customer
from django.contrib.auth import get_user_model
import logging
from django.db import models
from django.utils import timezone
import uuid

logger = logging.getLogger(__name__)
from account.models import User

class OrderConfirmationTool(BaseTool):
    """
    A tool to confirm and add a new order to the system.
    This tool is used by the agent to create a new order after a customer has
    confirmed their purchase and provided all necessary details.
    If the customer does not exist, it will be automatically created.
    """
    
    name: str = "order_confirmation_tool"
    description: str = (
        "CONFIRM AND CREATE A NEW ORDER. Use this tool ONLY when the user explicitly "
        "wants to finalize a purchase. You must gather the number of 'items', "
        "and the 'total' monetary value. The order number will be generated automatically. "
        "The customer can be identified by an existing 'customer_id' or, if new, by "
        "providing a 'customer_name' (mandatory for new customers), and optionally "
        "'customer_phone' and 'customer_email'. "
        "Do not use this tool to answer questions about orders or products; use it strictly for creation."
    )

    _user: User = PrivateAttr()

    def __init__(self, user: User, **kwargs):
        super().__init__(**kwargs)
        self._user = user
    
    class InputSchema(BaseModel):
        # ✅ The 'order_number' field has been removed from the InputSchema
        items: int = Field(
            ...,
            description="The number of items in the order."
        )
        total: float = Field(
            ...,
            description="The total monetary value of the order."
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
            description="The current status of the order. Defaults to 'pending'. Allowed values are: 'pending', 'processing', 'shipped', 'delivered', 'cancelled'."
        )
        payment_status: Optional[str] = Field(
            Order.PaymentStatus.PENDING,
            description="The current payment status of the order. Defaults to 'pending'. Allowed values are: 'paid', 'pending', 'refunded'."
        )
        source: Optional[str] = Field(
            Order.Source.MANUAL,
            description="The source from which the order was placed. Defaults to 'manual'. Allowed values are: 'facebook', 'whatsapp', 'manual'."
        )
        
    args_schema: Type[BaseModel] = InputSchema
    
    def _run(
        self, 
        items: int, 
        total: float,
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
            # 1. Find or create the customer using the tool's self._user object
            customer = self._get_or_create_customer(
                user_id=self._user.id,
                customer_id=customer_id,
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_email=customer_email
            )
            if not customer:
                return f"❌ Error: Could not find or create a customer. 'customer_name' is required if 'customer_id' is not provided."
                
            # ✅ Generate a unique order number automatically
            # You can customize this format (e.g., "ORD-" + UUID)
            order_number = f"ORD-{timezone.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

            # 2. Check for existing order number to prevent duplicates (unlikely with this method but good practice)
            if Order.objects.filter(order_number=order_number).exists():
                 # If a rare collision occurs, try again with a new number.
                 order_number = f"ORD-{timezone.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
                 
            # 3. Create the new order
            new_order = Order.objects.create(
                order_number=order_number,
                customer=customer,
                items=items,
                total=total,
                status=status,
                payment_status=payment_status,
                source=source
            )
            
            logger.info(f"New order created: {new_order.order_number} for customer ID {customer.id}")
            
            return (
                f"✅ Order confirmed and created successfully!\n"
                f"Order Number: {new_order.order_number}\n"
                f"Customer: {customer.name} (ID: {customer.id})\n"
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
    
    def _get_or_create_customer(
        self, 
        user_id: int, 
        customer_id: Optional[int], 
        customer_name: Optional[str],
        customer_phone: Optional[str],
        customer_email: Optional[str]
    ) -> Optional[Customer]:
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