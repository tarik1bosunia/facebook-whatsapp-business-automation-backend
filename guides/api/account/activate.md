
# Frontend Code For Acitvate
```js
// In your frontend code
const registerUser = async (userData) => {
  const response = await fetch('http://127.0.0.1:8000/api/register/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Frontend-Base-Url': window.location.origin  // Sends current frontend URL
    },
    body: JSON.stringify(userData)
  });
  return response.json();
}
```