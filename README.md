Команды для зпапуска с семинара

```bash
# terminal 1
docker build -t cs-hse-sem02-server .
docker network create my-network
docker run --network=my-network --name=server-host cs-hse-sem02-server

# terminal 2
docker run --network=my-network -it ubuntu bash
apt update && apt install curl
curl server-host:8080/biba
```