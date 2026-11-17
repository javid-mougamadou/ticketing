############################
# Tailwind build stage
############################
FROM alpine:3.20 AS tailwind

RUN apk add --no-cache curl
WORKDIR /build

# Pin volontaire du binaire standalone (pas de runtime Node nécessaire) --
# éviter qu'un changement de format d'URL upstream casse le build.
RUN curl -sLo tailwindcss https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.14/tailwindcss-linux-x64 \
    && chmod +x tailwindcss

COPY tailwind.config.js ./tailwind.config.js
COPY static/src/input.css ./static/src/input.css
COPY templates ./templates

RUN ./tailwindcss -i ./static/src/input.css -o ./static/dist/tailwind.css --minify

############################
# Application image
############################
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=tailwind /build/static/dist/tailwind.css ./static/dist/tailwind.css

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
