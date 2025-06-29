# 🔐 Step-by-Step: Generate and Use a Long-Lived Page Access Token

---

## Step 1: Get a Short-Lived User Access Token

Use the [Graph API Explorer](https://developers.facebook.com/tools/explorer/):

1. Select your app.
2. Click **"Get User Access Token"**.
3. Select the following **scopes**:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `pages_show_list`
4. Click **"Generate Access Token"**.

You will now have a **short-lived user token**.

---

## Step 2: Exchange for Long-Lived User Token

Use this endpoint (replace `APP_ID`, `APP_SECRET`, and `USER_ACCESS_TOKEN`):

```bash
https://graph.facebook.com/v22.0/oauth/access_token?
  grant_type=fb_exchange_token&
  client_id=APP_ID&
  client_secret=APP_SECRET&
  fb_exchange_token=USER_ACCESS_TOKEN
```
this will return
```
{
  "access_token": "LONG_LIVED_USER_TOKEN",
  "token_type": "bearer",
  "expires_in": 5184000
}
```
## Step 3: Get Page Access Token
```sh
curl -X GET \
  "https://graph.facebook.com/v22.0/me/accounts?access_token=LONG_LIVED_USER_TOKEN"
```
this will return 
```sh
{
  "data": [
    {
      "access_token": "LONG_LIVED_PAGE_ACCESS_TOKEN",
      "name": "Page Name",
      "id": "123456789"
    }
  ]
}
```
## Example: Use the Long-Lived Page Token in curl
```sh
curl -X POST "https://graph.facebook.com/v22.0/{page_id}/feed" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer LONG_LIVED_PAGE_ACCESS_TOKEN" \
     -d '{
           "message": "Scheduled post",
           "link": "https://example.com",
           "published": false,
           "scheduled_publish_time": 1730000000
         }'

```