# How to Check Django DEBUG Status in Docker

This guide explains how to verify the `DEBUG` status of your Django application when it's running inside a Docker container.

## Steps to Check DEBUG Status

1. **Ensure your Docker containers are running:**
    If your Docker containers are not already running, navigate to your project's root directory in the terminal and execute the following command:

    ```sh
    docker compose up -d
    ```

2. **Access the Django application container's shell:**
    First, identify the name of your Django server container. This can typically be found in your `docker-compose.yml` file under the `container_name` key for the `server` service (e.g., `fbaserver-container`).

    Once you have the container name, execute a shell session inside the running container using the `docker exec` command:

    ```sh
    docker exec -it fbaserver-container bash
    ```

    *(Replace `fbaserver-container` with the actual name of your Django container if it differs.)*

3. **Open the Django shell:**
    After successfully entering the container's shell, launch the Django management shell by running:

    ```sh
    python manage.py shell
    ```

4. **Check the DEBUG setting:**
    Within the Django shell, import the `settings` module from `django.conf` and then print the value of the `DEBUG` attribute:

    ```python
    from django.conf import settings
    print(settings.DEBUG)
    ```

    This command will output either `True` (if `DEBUG` is enabled, typically when `DEBUG=1` in your `.env` file) or `False` (if `DEBUG` is disabled).

5. **Exit the shells:**
    To exit the Django shell, type `exit()` and press Enter. Then, to exit the Docker container's shell, type `exit` and press Enter again.

This process allows you to directly inspect the `DEBUG` status as interpreted by your Django application within its Dockerized environment.
