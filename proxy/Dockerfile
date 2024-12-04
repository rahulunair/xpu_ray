FROM traefik:latest

COPY traefik.yml /etc/traefik/traefik.yml
COPY dynamic /etc/traefik/dynamic/

RUN chmod 600 /etc/traefik/traefik.yml \
    && chmod 600 /etc/traefik/dynamic/middleware.yml