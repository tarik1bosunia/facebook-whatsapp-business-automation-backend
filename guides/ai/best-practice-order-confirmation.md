# The Definitive Guide to Handling Ambiguous User Input in LLM Tools

When building robust AI systems, especially for critical tasks like order confirmation, relying on a single line of defense is risky. The best practice is a hybrid, two-layer approach that combines clear instructions for the LLM with a final, decisive validation layer in your code.

This model ensures the AI is both conversationally intelligent and functionally reliable, providing a seamless user experience while preventing bad data from being processed.

## Layer 1: Guide the LLM with an Enhanced Schema (The "Soft" Check)

This is the first and most important layer. The goal is to empower the LLM to resolve ambiguity on its own *before* it even attempts to call the tool. This makes the conversation feel natural and intelligent.

We achieve this by enriching the tool's schema with clear, descriptive instructions.

### Enhanced Pydantic Schema

```python
from pydantic import BaseModel, Field
from typing import Optional

class OrderConfirmationDetails(BaseModel):
    """
    Use this tool ONLY after you have gathered all required information from the customer.
    If information is missing, ambiguous, or contradictory, you MUST ask clarifying questions first.
    DO NOT call this tool with placeholder or uncertain data.

    Ambiguity Check: If the user provides the same value for 'city' and 'police_station',
    you must ask for confirmation before calling this tool. For example:
    "I see you've entered 'Rajshahi' for both city and police station. Is that correct?"
    """
    items: str = Field(..., description="The list of products and quantities. Example: '1 iPhone 14, 2 chargers'")
    name: str = Field(..., description="The customer's full name.")
    phone_number: str = Field(..., description="The customer's contact phone number.")
    city: str = Field(..., description="The city for the delivery address. This is a major administrative area.")
    police_station: str = Field(..., description="The name of the police station nearest to the delivery address. This is a local landmark for delivery coordination.")
    # This new field allows the LLM to tell our code that the ambiguity has been confirmed.
    is_ambiguity_resolved: Optional[bool] = Field(False, description="Set this to True only if you have already asked the user to confirm an ambiguous 'city' and 'police_station' and they have confirmed it is correct.")

```

**Why this is the best first layer:**

1.  **Explicit Instructions:** The docstring gives the LLM a clear directive: **ask, don't assume**. It even provides an example of what to do in the exact scenario we're solving.
2.  **The `is_ambiguity_resolved` Flag:** This is the key. It creates a communication channel between the LLM and the tool. The LLM can now signal that it has already handled the ambiguity. This prevents the tool from re-asking the same question.

## Layer 2: Implement a Final Validation Layer in Code (The "Hard" Check)

The LLM will follow instructions most of the time, but we cannot assume it will be perfect every time. A final validation layer in our code acts as a safety net, ensuring that no bad data ever gets through to our system backend (e.g., the order database).

This layer catches anything the LLM might have missed.

### The Tool's Implementation Logic

```python
def confirm_order(details: OrderConfirmationDetails):
    """
    This function is the implementation of the order confirmation tool.
    It contains the final validation logic.
    """
    # Layer 2: The "Hard" Check
    # This check runs regardless of what the LLM did.
    if details.city.lower() == details.police_station.lower():
        # If the values are the same, we check if the LLM has already resolved this.
        if not details.is_ambiguity_resolved:
            # The LLM failed to follow instructions. We override its response and ask for clarification.
            # This is our safety net.
            return f"I see you've entered '{details.city}' for both your city and the nearest police station. To avoid any delivery errors, could you please confirm if this is correct?"

    # If we reach this point, the data is considered valid.
    # Proceed with the actual order confirmation logic (e.g., save to database).
    print(f"Order confirmed for {details.name}. Items: {details.items}.")
    return f"Thank you, {details.name}! Your order for {details.items} has been confirmed. We will contact you at {details.phone_number} for delivery details."

```

**Why this is the best second layer:**

1.  **Reliability:** This code will *always* run, providing a 100% reliable check against this specific error condition.
2.  **Graceful Failure:** If the LLM makes a mistake, the system doesn't crash or process bad data. Instead, it gracefully degrades to a helpful, scripted response.
3.  **Trust but Verify:** This approach follows the principle of "trust, but verify." We trust the LLM to handle the conversation, but we verify the final data before committing it.

## Summary: The Hybrid Advantage

By combining these two layers, you get the best of both worlds:

*   **An Intelligent Conversationalist:** In most cases, the LLM (Layer 1) will handle the ambiguity perfectly, providing a smooth and natural user experience.
*   **A Rock-Solid Backend:** The validation code (Layer 2) acts as a final guarantee, ensuring data integrity and preventing errors even if the LLM misinterprets its instructions.

This hybrid model is the most robust, scalable, and professional way to build reliable, LLM-powered tools.