# making facebook post from api
## Architecture
```
[Frontend (Next.js)] --> [Backend (Django DRF)] --> [Facebook Graph API]
```
## Flow:
1. User submits a post request via your form on the frontend (Next.js + RTK Query).

2. RTK Query sends a POST request to your Django backend (e.g., /api/facebook/post/).

3. Django backend:

   - Validates the request.

   - Retrieves the Page Access Token.

   - Sends a POST request to https://graph.facebook.com/{page_id}/feed.

4. Facebook returns a success or error response.

5. Django returns the result back to the frontend to show a success/failure message.