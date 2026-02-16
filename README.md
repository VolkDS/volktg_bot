# VolkTG_bot

## Telegram
For a description of the Bot API, see this page: https://core.telegram.org/bots/api

## Useful commands
Build image
```
docker build --no-cache --progress=plain -t test/volktg_bot --build-arg PY_BUILD_VERSION=1.0.0 .
```

Run container
```
docker run -it --rm --env-file .env test/volktg_bot:latest /usr/local/bin/volktg_bot -v
```
