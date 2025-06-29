# 🔄 JWT Token Refresh – `/api/account/token/refresh/`

## 📍 URL
`POST http://127.0.0.1:8000/api/account/token/refresh/`

---

## 📬 GET Request

```http
GET /api/account/token/refresh/
```

**Response (405 Method Not Allowed):**
```json
{
    "errors": {
        "detail": "Token is invalid",
        "code": "token_not_valid"
    }
}
```

---

## 📬 POST Request – Missing Refresh Token

```http
POST /api/account/token/refresh/
Content-Type: application/json

{}
```

**Response (400 Bad Request):**
```json
{
    "errors": {
        "refresh": [
            "This field is required."
        ]
    }
}
```

---

## 📬 POST Request – Invalid Refresh Token

```json
{
  "refresh": "invalid_refresh_token"
}
```

**Response (401 Unauthorized):**
```json
{
    "errors": {
        "detail": "Token is invalid",
        "code": "token_not_valid"
    }
}
```

---

## ✅ POST Request – Valid Refresh Token

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```
