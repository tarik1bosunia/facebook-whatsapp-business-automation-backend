# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/

ARG PYTHON_VERSION=3.13.4
FROM python:${PYTHON_VERSION}-slim AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1


# HuggingFace cache configuration

# 1. First create the directory as root
RUN mkdir -p /app/model_cache

# 2. Then set the environment variables
ENV HF_HOME=/app/model_cache \
    TRANSFORMERS_CACHE=/app/model_cache \
    XDG_CACHE_HOME=/app/model_cache


# 3. Set proper permissions (more secure than 777)
RUN chmod -R 755 /app/model_cache && \
    chown -R 1000:1000 /app/model_cache



WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install PostgreSQL client libraries and build dependencies.
RUN apt-get update && apt-get install -y \
libpq-dev \
gcc \
git \ 
&& rm -rf /var/lib/apt/lists/*


# COPY requirements.txt .
# RUN --mount=type=cache,target=/root/.cache/pip \
#     pip install -r requirements.txt

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt


RUN pip uninstall python-dotenv -y
RUN pip install django-dotenv    


# Switch to the non-privileged user to run the application.

# Copy the source code into the container.
COPY . .

# Remove all migration files except __init__.py during build
RUN find . -path "*/migrations/*.py" ! -name "__init__.py" -delete && \
    find . -path "*/migrations/*.pyc" -delete


# Copy entrypoint and give execute permissions as root
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh    

# Set ownership and switch to non-root user
# RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Expose the port that the application listens on.
EXPOSE 8000

# Use a script for complex startup commands
ENTRYPOINT ["/entrypoint.sh"]

# development
# CMD python manage.py runserver 0.0.0.0:8000
# CMD python manage.py migrate && python manage.py create_initial_users && python manage.py seed_products && python manage.py runserver 0.0.0.0:8000

# Run the application:
# 1. Apply migrations
# 2. Conditionally load the countries and states data (if they don't exist)
# 3. Start the Gunicorn server
#CMD python manage.py migrate && python manage.py account_initial_data && python manage.py ratings_initial_data && gunicorn 'ratemyprofessorsapi.wsgi' --bind=0.0.0.0:8000