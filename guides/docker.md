# Remove python-dotenv
## Double-check Python packages installed in the container
```sh
docker compose exec server pip freeze | grep dotenv
```