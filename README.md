# facebook-whatsapp-business-automation-backend

## initial setup

- [creating project and apps](./guides/creating_project_and_apps.md)
- [dotenv](./guides/dotenv.md)
- [corsheaders](./guides/corsheaders.md)
- [gemini auto reply of messages from messenger](./guides/geimini.md)

## install request

```sh
pip install requests
```

## [facebook api guide](./guides/facebook_api.md)

## filtering

- pip install django-filter

## [TODO](./guides/TODO.md)

## [FUTURE PLAN](./guides/FUTURE_PLAN.md)

### For python-magic on Linux

```sh
pip install python-magic
```

For production use:

- Add proper monitoring for background tasks

- Implement a task queue (Celery) instead of thread pool

- Add file size limits

- Implement virus scanning

- Add rate limiting for downloads

## I need to work on torch for CPU in pip

- pip3 install torch torchvision torchaudio --index-url <https://download.pytorch.org/whl/cpu>
