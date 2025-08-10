# IF MESSAGE RELATED CHAGE THEN MUST BE FOLLOW THE BELLOW

## 1. Start ngrok on the same domain port

```sh
ngrok http --url=wholly-notable-raccoon.ngrok-free.app http://127.0.0.1:8000
```

## setup messenger webhook

- <https://wholly-notable-raccoon.ngrok-free.app/api/messaging/webhook/messenger/>

## setup whatsapp webhook


- <https://wholly-notable-raccoon.ngrok-free.app/api/messaging/webhook/whatsapp/>

## run in docker

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```
