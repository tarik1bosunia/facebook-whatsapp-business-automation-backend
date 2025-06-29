# 📧 Check Email Existence – `/api/account/check-email/`

## 📍 URL  
`GET http://127.0.0.1:8000/api/account/check-email/`

---

## 📬 GET Request – Missing `email` Field

```http
GET /api/account/check-email/
Content-Type: application/json

{}
```

**Response (400 Bad Request):**
```json
{
  "errors": {
    "email": [
      "This field is required."
    ]
  }
}
```

---

## 📬 GET Request – Invalid Email Format

```json
{
    "errors": {
        "email": [
            "Enter a valid email address."
        ]
    }
}
```

**Response (400 Bad Request):**
```json
{
  "errors": {
    "email": [
      "Enter a valid email address."
    ]
  }
}
```

---

## 📬 GET Request – Email Exists

```json
{
  "email": "existing@example.com"
}
```

**Response (400 Bad Request):**
```json
{
    "exists": true,
    "message": "An account with this email already exists."
}
```

---

## ✅ GET Request – Email Does Not Exist

```json
{
  "email": "newuser@example.com"
}
```

**Response (200 OK):**
```json
{
    "exists": false,
    "message": "Email does not exist."
}
```

---

## 🔧 Notes:
- Requires `application/json` content type.
- Data should be passed as JSON in request **body**, not as query parameters.
```json
{
  "email": "you@example.com"
}
```
