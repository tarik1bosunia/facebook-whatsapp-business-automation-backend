# Long-Lived Access Tokens

If you need a long-lived User access token you can generate one from a short-lived User access token. A long-lived token generally lasts about 60 days.

You will need the following:
- A valid User Access Token
- Your App ID
- Your App Secre

Query the GET oauth/access_token endpoint.
```sh
curl -i -X GET "https://graph.facebook.com/{graph-api-version}/oauth/access_token?  
    grant_type=fb_exchange_token&          
    client_id={app-id}&
    client_secret={app-secret}&
    fb_exchange_token={your-access-token}" 
```
Sample Response
```sh
{
  "access_token":"{long-lived-user-access-token}",
  "token_type": "bearer",
  "expires_in": 5183944            //The number of seconds until the token expires
}
```