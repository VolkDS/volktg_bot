FROM python:3.10-trixie AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install build

# Copy requirements.txt
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Build application
COPY . /app
ARG PY_BUILD_VERSION
ENV BUILD_VERSION=${PY_BUILD_VERSION:-0.0.0}
RUN python -m build --wheel -o /app/wheels

## Beginning of runtime image
# Remember to use the same python version
# and the same base distro as the builder image
FROM python:3.10-slim-trixie AS runtime

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN --mount=type=bind,from=builder,source=/app/wheels,target=/wheels \
    PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir --no-compile /wheels/*

CMD [ "/usr/local/bin/volktg_bot" ]
