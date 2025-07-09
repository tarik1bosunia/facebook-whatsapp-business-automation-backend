# 🔍 Why not use only `is_active`?

You **can**, but it’s not ideal.

---

## 🔁 Option 1: Use `is_active = False` until email is verified

### ✅ Pros:
- Simpler: no need for a separate `is_email_verified` field.
- Login is blocked automatically.

### ❌ Cons:
You lose distinction between:
- Users who never verified their email
- Users manually deactivated by admin
- Users who broke rules (banned)

---

## ✅ Recommended: Use **both** fields

- `is_active`: for **account-level status** (ban, suspend, delete).
- `is_email_verified`: for **email verification flow only**.

### ✏️ Login logic example:

```python
if not user.is_email_verified:
    return Response({"detail": "Please verify your email."}, status=403)

if not user.is_active:
    return Response({"detail": "Your account is inactive."}, status=403)
```