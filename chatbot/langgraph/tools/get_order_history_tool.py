from langchain_core.tools import BaseTool
from typing import Optional, Type, List
from pydantic import BaseModel, Field
import logging

from account.models import User
from customer.models import Customer, Order, OrderItem
from messaging.models import SocialMediaUser

logger = logging.getLogger(__name__)

class GetOrderHistoryTool(BaseTool):
    name: str = "get_order_history_tool"
    description: str = (
        "Use this tool to fetch a customer's order history. "
        "ALWAYS use this tool when a customer asks about their previous, past, or last order. "
        "The tool can automatically identify the customer from their social media profile. "
        "You can also look up by a specific 'order_number', or by 'customer_phone'. "
        "Do not ask for this information if the user does not provide it; the tool will handle it."
    )

    _user: User
    _social_user: SocialMediaUser

    def __init__(self, user: User, social_user: SocialMediaUser = None, **kwargs):
        super().__init__(**kwargs)
        self._user = user
        self._social_user = social_user

    class InputSchema(BaseModel):
        customer_id: Optional[int] = Field(None, description="The ID of the customer.")
        customer_phone: Optional[str] = Field(None, description="The phone number of the customer.")
        order_number: Optional[str] = Field(None, description="The specific order number to look up.")
        show_more: bool = Field(False, description="Set to true to show the last 10 orders if the user confirms.")

    args_schema: Type[BaseModel] = InputSchema

    def _run(self, customer_id: Optional[int] = None, customer_phone: Optional[str] = None, order_number: Optional[str] = None, show_more: bool = False) -> str:
        try:
            # 1. Direct Order Number Lookup
            if order_number:
                order = Order.objects.filter(order_number__iexact=order_number, customer__user=self._user).first()
                if not order:
                    return f"❌ I couldn't find any order with the number '{order_number}'. Would you like to search by the phone number you used to place the order?"
                return self._format_order_details(order)

            # 2. Customer Lookup
            customer = self._find_customer(customer_id, customer_phone)
            if not customer:
                return "I couldn't find any customer profile. Could you please provide the phone number you used when placing your order?"

            # 3. Fetch Orders
            orders = Order.objects.filter(customer=customer).order_by('-created_at')
            if not orders.exists():
                return f"✅ It looks like {customer.name} (ID: {customer.id}) hasn't placed any orders yet. Would you like to place a new order?"

            # 4. Format Response
            if show_more:
                return self._format_multiple_orders(orders[:10], customer)
            else:
                last_order = orders.first()
                response = f"I found your last order, {last_order.order_number}.\n"
                response += self._format_order_details(last_order, include_header=False)
                if orders.count() > 1:
                    response += "\nWould you like to see your full history for the last 10 orders?"
                return response

        except Exception as e:
            logger.error(f"Failed to retrieve order history: {str(e)}", exc_info=True)
            return f"❌ An unexpected error occurred while fetching order history. Reason: {str(e)}"

    def _find_customer(self, customer_id: Optional[int], customer_phone: Optional[str]) -> Optional[Customer]:
        """Finds a customer based on social ID, explicit ID, or phone."""
        # Priority 1: Customer is already linked to the social profile
        if self._social_user and self._social_user.customer:
            return self._social_user.customer

        # Priority 2: Explicitly provided customer ID
        if customer_id:
            return Customer.objects.filter(id=customer_id, user=self._user).first()

        # Priority 3: Explicitly provided phone number
        if customer_phone:
            return Customer.objects.filter(phone=customer_phone, user=self._user).first()

        # Priority 4: Find customer via social media ID
        if self._social_user:
            try:
                social_user = SocialMediaUser.objects.get(id=self._social_user.id)
                if social_user.customer:
                    return social_user.customer
            except SocialMediaUser.DoesNotExist:
                pass # Fall through to return None
        
        return None

    def _format_order_details(self, order: Order, include_header: bool = True) -> str:
        """Formats the details for a single order."""
        header = f"✅ Details for Order {order.order_number}:\n" if include_header else ""
        details = (
            f"{header}"
            f"Status: {order.get_status_display()}\n"
            f"Total: ${order.total:.2f}\n"
            f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"Items:\n"
        )
        order_items = order.items.all()
        for item in order_items:
            details += f"  - {item.product.name} (x{item.quantity})\n"
        return details

    def _format_multiple_orders(self, orders: List[Order], customer: Customer) -> str:
        """Formats a list of the last few orders."""
        response = f"✅ Here is the order history for {customer.name} (ID: {customer.id}):\n"
        for order in orders:
            response += (
                f"  - Order: {order.order_number}, "
                f"Status: {order.get_status_display()}, "
                f"Total: ${order.total:.2f}, "
                f"Date: {order.created_at.strftime('%Y-%m-%d')}\n"
            )
        return response

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported.")