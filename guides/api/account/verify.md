# ✅ Verify Authenticated User – `/api/account/verify/`

## 📍 URL
`POST http://127.0.0.1:8000/api/account/verify/`

---

## 🔐 Requires Authentication  
**Header:**
```http
Authorization: Bearer <your_access_token>
```

---

## 📬 GET Request

```http
GET /api/account/verify/
```

**Response (401 Unauthorized):**
```json
{
    "errors": {
        "detail": "Authentication credentials were not provided."
    }
}
```

---

## 📬 POST Request – Without Token

```http
POST /api/account/verify/
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## 📬 POST Request – With Invalid Token

```http
POST /api/account/verify/
Authorization: Bearer invalid.token.here
```

**Response (401 Unauthorized):**
```json
{
    "errors": {
        "detail": "Given token not valid for any token type",
        "code": "token_not_valid",
        "messages": [
            {
                "token_class": "AccessToken",
                "token_type": "access",
                "message": "Token is invalid"
            }
        ]
    }
}
```

---

## ✅ POST Request – With Valid Token

```http
POST /api/account/verify/
Authorization: Bearer <valid_access_token>
```

**Response (200 OK):**
```json
{
    "token": {
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc0OTg4MDE0MiwiaWF0IjoxNzQ5NzkzNzQyLCJqdGkiOiJhN2QxY2VhNTY4ZjA0MTZkODAzNDBlMDA3N2M2YmM4YiIsInVzZXJfaWQiOjF9.eyIKC7niRpN8pPDlWVDTarzFMIFFngH6s7zgXW6DOiw",
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ5Nzk0OTQyLCJpYXQiOjE3NDk3OTM3NDIsImp0aSI6IjhhOWZlZmIzMDY1ZTQ0NWRiNjVhNDkyYWE0YmUyNzQxIiwidXNlcl9pZCI6MX0.tZN77-Ntvw2izaGvvGeO4z6GU4AOv7RiCuqn4sbZIpc"
    },
    "message": "User is verified"
}
```
