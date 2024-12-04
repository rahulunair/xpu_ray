docker compose down --remove-orphans
docker rmi xpu_ray-sd-service xpu_ray-auth xpu_ray-traefik
docker volume prune -f
docker network prune -f
docker image prune -f