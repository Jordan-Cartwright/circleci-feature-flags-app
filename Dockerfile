FROM python:3.14.2-slim AS build

ARG USER=demo
ARG GROUP=demo
ARG UID=1000
ARG GID=1000
ARG PORT=8080

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # set environment variables for Flask
    FLASK_APP=demo:create_app \
    PORT=${PORT}

# Add a group and user to avoid using root
RUN addgroup --gid "${GID}" "${GROUP}" \
    && adduser \
        --disabled-password \
        --no-create-home \
        --home "/app" \
        --gecos "" \
        --uid "${UID}" \
        --ingroup "${GROUP}" \
        "${USER}"

# Set the working directory
WORKDIR /app

# Copy in requirements file
COPY --chown=${USER}:${GROUP} requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && rm requirements.txt \
    && chown -R ${USER}:${GROUP} /app

# Copy in application code
COPY --chown=${USER}:${GROUP} ./docker/entrypoint.sh /
COPY --chown=${USER}:${GROUP} main.py .
COPY --chown=${USER}:${GROUP} ./migrations migrations/
COPY --chown=${USER}:${GROUP} ./demo demo/

# Switch to non-root user
USER "${USER}:${GROUP}"

# Expose port
EXPOSE "${PORT}"

ENTRYPOINT ["/entrypoint.sh"]

CMD ["python", "main.py"]
