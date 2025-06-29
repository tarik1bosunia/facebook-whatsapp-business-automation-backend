# 📝 User Registration – `/api/account/registration/`

## 📍 URL  
`POST http://127.0.0.1:8000/api/account/registration/`

---

## ❌ POST Request – Missing Fields

```http
POST /api/account/registration/
Content-Type: application/json

{}
```

**Response (400 Bad Request):**
```json
{
  "errors": {
    "email": ["This field is required."],
    "password": ["This field is required."]
  }
}
```

---

## ❌ POST Request – Invalid Email Format

```json
{
  "email": "not-an-email",
  "password": "password123"
}
```

**Response (400 Bad Request):**
```json
{
  "errors": {
    "email": ["Enter a valid email address."]
  }
}
```

---

## ❌ POST Request – Existing Email

```json
{
  "email": "existing@example.com",
  "password": "password123"
}
```

**Response (400 Bad Request):**
```json
{
    "errors": {
        "email": [
            "A user with that email already exists."
        ]
    }
}
```

---

## ✅ POST Request – Successful Registration

```json
{
  "email": "newuser@example.com",
  "password": "securepassword"
}
```

**Response (201 Created):**
```json
{
  "token": {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "message": "Registration Successful"
}
```

---

## 📧 Email Sent

- A verification email is sent to the registered email address.
- It includes a link like:

```
http://127.0.0.1:8000/api/user/activate/<uid>/<token>/
```

---

## 🔧 Notes:
- Fields required: `email`, `password`
- `password` is write-only
- Returns JWT `access` and `refresh` tokens upon successful registration
- The user will need to activate their account via the email link
