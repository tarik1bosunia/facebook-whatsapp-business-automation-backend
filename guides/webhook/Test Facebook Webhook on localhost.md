# [Test Facebook Webhook on localhost](https://dashboard.ngrok.com/get-started/setup/windows)
## 1. Install ngrok -> from cmd run as adminstrator
```sh
choco install ngrok
```
## Run the following command to add your authtoken to the default ngrok.yml configuration file.
```sh
ngrok config add-authtoken 2xOQBEl0GXQB2XnCNjKrcidqjsH_sRYMDyxxRwJRnQukNheJ44M
```
##  92ac-103-99-177-138.ngrok-free.app need to add in allowed host
```py
ALLOWED_HOSTS = [
    '92ac-103-99-177-138.ngrok-free.app'
]

```
## 2. Run Django server locally
```sh
python manage.py runserver 8000
```
## 3. Start ngrok on the same port
```sh
ngrok http http://127.0.0.1:8000
ngrok http --domain=myapp.ngrok-free.app 8000
```
# static/percistent domain ngrok
```sh
ngrok http --domain=fitting-ladybug-mistakenly.ngrok-free.app 8000
```
## https://fitting-ladybug-mistakenly.ngrok-free.app -> http://localhost:8000

## webhook setup url on facebook messenger
-  https://fitting-ladybug-mistakenly.ngrok-free.app/api/messaging/webhook/messenger/
-  https://612498680b28.ngrok-free.app/api/messaging/webhook/messenger/
- https://developers.facebook.com/apps/1405936334088402/webhooks/?business_id=1786552525544080
## webhook setup url on whatsapp
- https://fitting-ladybug-mistakenly.ngrok-free.app/api/messaging/webhook/whatsapp/
- https://728b-103-99-177-138.ngrok-free.app/api/messaging/webhook/whatsapp/
- https://business.facebook.com/latest/settings/system_users?business_id=1786552525544080&selected_user_id=61576759232765
- https://developers.facebook.com/apps/686555444118209/whatsapp-business/wa-settings/?business_id=1786552525544080

# common
-  https://developers.facebook.com/apps/686555444118209/whatsapp-business/wa-settings/?business_id=1786552525544080
-  https://developers.facebook.com/apps/1405936334088402/webhooks/?business_id=1786552525544080

# WhatsApp Cloud API Webhook Permissions

To properly receive and manage WhatsApp messages via the Meta (Facebook) Cloud API, you must subscribe to the following webhook events during your Webhook Configuration.

## 1. Required Permissions (Events to Subscribe)

| Permission (Event)         | Description                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| `messages`                | Receive incoming messages (text, images, documents, etc.)                   |
| `message_statuses`        | Get delivery updates (sent, delivered, read, failed)                        |
| `message_template_statuses` | Track template message statuses (approved, rejected, etc.)                  |


### 5. Request Required Permissions

| Permission                    | Description                                                    |
|------------------------------|----------------------------------------------------------------|
| `whatsapp_business_management` | Manage WABA and phone numbers                                 |
| `whatsapp_business_messaging`  | Send and receive WhatsApp messages via the Cloud API          |
| `business_management`          | Required only if accessing business portfolio endpoints    

**Steps to request:**

1. Go to **App Dashboard**
2. Click **App Review → Permissions and Features**
3. Click **Request Advanced Access** for the above scopes
4. Provide business use case, privacy policy, and screencast (for production approval)


### Notes:
- These permissions ensure your webhook can handle both **incoming user messages** and **delivery status updates** for messages sent from your system.
- You can configure these events under your [Meta App Dashboard](https://developers.facebook.com/apps/) > Webhooks section.

