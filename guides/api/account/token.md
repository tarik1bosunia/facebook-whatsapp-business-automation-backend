# 🔐 JWT Token Endpoint – `/api/account/token/`

## 📍 URL
`POST http://127.0.0.1:8000/api/account/token/`

---

## 📬 GET Request

```http
GET /api/account/token/
```

**Response (405 Method Not Allowed):**
```json
{
    "errors": {
        "detail": "Method \"GET\" not allowed."
    }
}
```

---

## 📬 POST Request – Missing Fields

```http
POST /api/account/token/
Content-Type: application/json

{}
```

**Response (400 Bad Request):**
```json
{
    "errors": {
        "email": [
            "This field is required."
        ],
        "password": [
            "This field is required."
        ]
    }
}
```

---

## 📬 POST Request – Invalid Credentials

```json
{
  "email": "email",
  "password": "password"
}
```

**Response:**
```json
{
    "errors": {
        "detail": "No active account found with the given credentials"
    }
}
```

---

## ✅ POST Request – Valid Credentials

```json
{
  "email": "t@t.com",
  "password": "t"
}
```

**Response:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```
