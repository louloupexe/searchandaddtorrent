You need run pip install -r requirement.txt

You need change QB_URL,USER,PASS

You need qbittorrent serveur you can use docker 

docker compose/docker cli for qbittorrent

CLI
docker run --rm \
    --name qbittorrent \
    -p 8080:8080 \
    -e PUID=1000 \
    -e PGID=1000 \
    -e UMASK=002 \
    -e TZ="Etc/UTC" \
    -e WEBUI_PORTS="8080/tcp,8080/udp" \
    -v /<host_folder_config>:/config \
    -v /<host_folder_data>:/data \
    ghcr.io/hotio/qbittorrent


docker compose

services:
  qbittorrent:
    container_name: qbittorrent
    image: ghcr.io/hotio/qbittorrent
    ports:
      - "8080:8080"
    environment:
      - PUID=1000
      - PGID=1000
      - UMASK=002
      - TZ=Etc/UTC
      - WEBUI_PORTS=8080/tcp,8080/udp
    volumes:
      - /<host_folder_config>:/config
      - /<host_folder_data>:/data

you can use swag for make own URL example qbittorrent.com or you can use duckdns qbittorrent.yoururl.duckdns.org
duckdns.org
