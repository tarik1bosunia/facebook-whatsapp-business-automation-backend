# 🔐 User Login – `/api/account/login/`

## 📍 URL  
`POST http://127.0.0.1:8000/api/account/login/`

---

## ❌ POST Request – Missing Fields

```http
POST /api/account/login/
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

## ❌ POST Request – Invalid Credentials

```json
{
  "email": "invalid@example.com",
  "password": "wrongpassword"
}
```

**Response (404 Not Found):**
```json
{
  "errors": {
    "non_field_errors": [
      "Email or Password is not Valid"
    ]
  }
}
```

---

## ✅ POST Request – Successful Login

```json
{
  "email": "t@t.com",
  "password": "t"
}
```

**Response (200 OK):**
```json
{
  "token": {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "message": "Login Success"
}
```

---

## 🔧 Notes:
- Required fields: `email`, `password`
- Returns JWT `access` and `refresh` tokens if credentials are valid
- Uses Django's `authenticate()` method to validate the user
```
