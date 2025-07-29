# [whatsapp cloud api](https://developers.facebook.com/docs/whatsapp/cloud-api)
## [setup webhook](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/set-up-webhooks)

### Create an endpoint
### Subscribe to webhooks
1. [Create a Business Type App in the Meta App Dashboard.](https://developers.facebook.com/docs/development/create-an-app)
2. [Add the Webhooks Product to your Meta app in the App Dashboard.](https://developers.facebook.com/micro_site/url/?click_from_context_menu=true&country=BD&destination=https%3A%2F%2Fdevelopers.facebook.com%2Fdocs%2Fgraph-api%2Fwebhooks%2Fgetting-started%23configure-webhooks-product&event_type=click&last_nav_impression_id=1NlOOfq8GBa86oNHZ&max_percent_page_viewed=31&max_viewport_height_px=695&max_viewport_width_px=1536&orig_http_referrer=https%3A%2F%2Fdevelopers.facebook.com%2Fdocs%2Fwhatsapp%2Fcloud-api%2Fguides%2Fset-up-webhooks&orig_request_uri=https%3A%2F%2Fdevelopers.facebook.com%2Fajax%2Fdocs%2Fnav%2F%3Fpath1%3Dwhatsapp%26path2%3Dcloud-api%26path3%3Dguides%26path4%3Dset-up-webhooks&region=apac&scrolled=true&session_id=1O3lUvQvPXsW6dyis&site=developers)

### Permissions
- [whatsapp_business_messaging](https://developers.facebook.com/micro_site/url/?click_from_context_menu=true&country=BD&destination=https%3A%2F%2Fdevelopers.facebook.com%2Fdocs%2Fpermissions%23w&event_type=click&last_nav_impression_id=1NlOOfq8GBa86oNHZ&max_percent_page_viewed=31&max_viewport_height_px=695&max_viewport_width_px=1536&orig_http_referrer=https%3A%2F%2Fdevelopers.facebook.com%2Fdocs%2Fwhatsapp%2Fcloud-api%2Fguides%2Fset-up-webhooks&orig_request_uri=https%3A%2F%2Fdevelopers.facebook.com%2Fajax%2Fdocs%2Fnav%2F%3Fpath1%3Dwhatsapp%26path2%3Dcloud-api%26path3%3Dguides%26path4%3Dset-up-webhooks&region=apac&scrolled=true&session_id=1O3lUvQvPXsW6dyis&site=developers) — for `messages` webhooks
- whatsapp_business_management — for all other webhooks

### Payload Size
Webhooks payloads can be up to 3MB.


# Create an App

## Before You Start
You must have registered as a Meta developer and be logged into your [Meta developer account](https://developers.facebook.com/docs/development/register). 

## To create a Meta app you need the following:

- A unique icon image for your app
- Files must be between 512 x 512 and 1024 x 1024 pixels and in JPEG, GIF or PNG format. File size limit 5 MB.
- Contact information for a Data Protection Officer, if you are doing business in the European Union
- A URL to your Privacy Policy for your app
- A URL to instructions or a callback that allows your app user to delete their data from your app

# Limitations
- You are permitted to have a developer or administrator role on a maximum of 15 apps that are not already linked to a Meta Verified Business Account
- If you have reached the app limit and are unable to create an application or accept a new pending role, take the following steps in the apps dashboard:

- Link any unlinked applications to a business that has completed Meta [Business Verification](https://developers.facebook.com/docs/development/release/business-verification)
- Remove an app – Archived apps count towards the app limit; if you no longer require these apps, we suggest removing them
Remove yourself as an administrator or developer from an app