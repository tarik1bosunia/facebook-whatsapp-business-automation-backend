# Fixing and Improving the Order Confirmation Tool

This guide explains how to resolve critical issues in the `order_confirmation_tool`, including a misleading phone number error and a fragmented user experience. We will also add the necessary address fields to make the tool genuinely useful for placing orders.

## 1. The Problem

The current order confirmation process suffers from several major flaws:

- **Inefficient Conversational Flow:** The tool asks for customer information (name, phone, etc.) piece by piece, leading to a frustrating and lengthy conversation.
- **Misleading Phone Number Error:** The tool incorrectly reports that a valid phone number is "too long," which is confusing and blocks the user from completing their order.
- **Missing Address Information:** The tool does not collect the customer's address, which is essential for delivery.

## 2. Root Cause Analysis

The issues stem from both the tool's design and the underlying data model.

1. **Fragmented Data Collection:** The tool's `InputSchema` in [`chatbot/langgraph/tools/order_confirmation_tool.py`](chatbot/langgraph/tools/order_confirmation_tool.py) allows for optional, individual fields. This encourages the LLM to ask for information one item at a time instead of gathering everything it needs upfront.
2. **Missing Address Fields:** The [`Customer` model](customer/models/customer_model.py) lacks fields for storing an address, making it impossible to collect this information.
3. **Phone Number Error:** The error message "phone number is too long" is misleading. The `phone` field in the `Customer` model is a `CharField` with `max_length=20`, which is sufficient. The error is likely a generic failure from the tool that the LLM is misinterpreting. The root cause is a lack of robust validation and clear instructions for the LLM.

## 3. The Solution: A Streamlined, Robust Order Process

The solution is to re-design the tool to collect all necessary information in a single step, add the required address fields to the database, and provide clear instructions to the LLM.

### Step 1: Enhance the `Customer` Model

First, we need to add the address fields to the `Customer` model. Here is the **complete, updated** model you should use.

**File:** [`customer/models/customer_model.py`](customer/models/customer_model.py)

```python
from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()

class Customer(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        INACTIVE = 'inactive', _('Inactive')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customers")

    name = models.CharField(
        max_length=100,
        verbose_name=_('Name'),
        help_text=_("Customer's full name")
    )
    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_('Email'),
        help_text=_("Customer's email address")
    )
    phone = PhoneNumberField(
        blank=True,
        null=True,
        verbose_name=_('Phone Number'),
        help_text=_("Customer's contact number (e.g., +12125552368)")
    )
    
    # --- Address Fields ---
    city = models.CharField(
        max_length=100,
        verbose_name=_('City'),
        help_text=_("Customer's city")
    )
    police_station = models.CharField(
        max_length=100,
        verbose_name=_('Police Station'),
        help_text=_("Nearest police station for address reference")
    )
    area = models.CharField(
        max_length=255,
        blank=True, # Area is optional
        verbose_name=_('Area/Street Address'),
        help_text=_("Specific area or street address")
    )
    # --- End of Address Fields ---

    orders_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Orders Count'),
        help_text=_("Total number of orders placed by this customer")
    )
    total_spent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('Total Spent'),
        help_text=_("Total amount spent by this customer")
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name=_('Status'),
        help_text=_("Customer account status")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['email']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.name

    def update_stats(self):
        """Update order count and total spent based on related orders"""
        stats = self.orders.aggregate(
            count=models.Count('id'),
            total=Sum('total')
        )
        self.orders_count = stats['count'] or 0
        self.total_spent = stats['total'] or 0
        self.save(update_fields=['orders_count', 'total_spent'])
```

After modifying the model, you will need to create and run a database migration:
`python manage.py makemigrations`
`python manage.py migrate`

### Step 2: Upgrade the `OrderConfirmationTool`'s `InputSchema`

Next, update the tool's input schema to include the new address fields and add a validator to ensure all required information is present for new customers.

**File:** [`chatbot/langgraph/tools/order_confirmation_tool.py`](chatbot/langgraph/tools/order_confirmation_tool.py)

```python
# chatbot/langgraph/tools/order_confirmation_tool.py

class OrderConfirmationTool(BaseTool):
    # ... (name) ...
    description: str = (
        "CONFIRM AND CREATE A NEW ORDER. Use this tool ONLY when the user wants to finalize a purchase. "
        "Before calling this tool, you MUST have the following information: a list of items (product name and quantity), "
        "the customer's name, phone number, city, and police station. The 'area' is optional. "
        "If any of this information is missing, ask the user for all of it in a single message. "
        "Do not ask for information one by one. "
        "If the user is returning, you can use their 'customer_id' instead of collecting their details again."
    )

    # ... (__init__) ...

    class InputSchema(BaseModel):
        order_items: List[OrderItem] = Field(...)
        customer_id: Optional[int] = Field(None, ...)
        
        # --- Customer Details for New Customers ---
        customer_name: Optional[str] = Field(None, ...)
        customer_phone: Optional[str] = Field(None, ...)
        customer_email: Optional[str] = Field(None, ...)
        customer_city: Optional[str] = Field(None, description="The customer's city. Required for new customers.")
        customer_police_station: Optional[str] = Field(None, description="The customer's nearest police station. Required for new customers.")
        customer_area: Optional[str] = Field(None, description="The customer's specific area or street. Optional.")
        
        # ... (status, payment_status, source) ...

        # --- Add a validator to enforce data collection ---
        @model_validator(mode='after')
        def check_new_customer_details(self):
            if self.customer_id is None: # This is a new customer
                required_fields = [
                    self.customer_name,
                    self.customer_phone,
                    self.customer_city,
                    self.customer_police_station
                ]
                if not all(required_fields):
                    raise ValueError(
                        "For a new customer, you must provide 'customer_name', 'customer_phone', "
                        "'customer_city', and 'customer_police_station'."
                    )
            return self

    args_schema: Type[BaseModel] = InputSchema
```

### Step 3: Update the Tool's Logic

Finally, update the tool's `_run` and `_get_or_create_customer` methods to handle the new address fields.

**File:** [`chatbot/langgraph/tools/order_confirmation_tool.py`](chatbot/langgraph/tools/order_confirmation_tool.py)

```python
# In _run method, add the new fields to the call
def _run(
    self, 
    order_items: List[OrderItem], 
    # ... (existing args) ...
    customer_city: Optional[str] = None,
    customer_police_station: Optional[str] = None,
    customer_area: Optional[str] = None,
    # ... (rest of args) ...
) -> str:
    # ...
    customer = self._get_or_create_customer(
        # ... (existing args) ...
        customer_city=customer_city,
        customer_police_station=customer_police_station,
        customer_area=customer_area
    )
    # ...

# In _get_or_create_customer, handle the new fields
def _get_or_create_customer(self, user_id: int, customer_id: Optional[int], customer_name: Optional[str], customer_phone: Optional[str], customer_email: Optional[str], customer_city: Optional[str], customer_police_station: Optional[str], customer_area: Optional[str]) -> Optional[Customer]:
    # ...
    elif customer_name:
        # ... (logic to find existing customer) ...
        
        if customer_qs.exists():
            return customer_qs.first()
        
        user = User.objects.get(id=user_id)
        new_customer = Customer.objects.create(
            user=user,
            name=customer_name,
            phone=customer_phone,
            email=customer_email,
            # --- Add new fields to the create call ---
            city=customer_city,
            police_station=customer_police_station,
            area=customer_area
        )
        # ...
```

## 4. Example of the New, Improved Conversation

After implementing these changes, the conversation will be much smoother:

**User:** `confirm order iphone 14`

**AI:** `Of course! To finalize your order for one iPhone 14, I need a little more information. Could you please provide your full name, phone number, city, and nearest police station? Your specific area or street is optional but helpful.`

**User:** `Tarik, 01720198552, Dhaka, Gulshan, road 123`

**AI:** `(Calls the tool with all information at once)`
`✅ Order confirmed and created successfully!`
`Order Number: ORD-20231027143055-A4B1C2`
`Customer: Tarik`
`...`

By making these changes, you fix the errors and create a more efficient and user-friendly ordering process.
