# Despliegue en Swarm con Traefik Swarm existente

> **Alternativa al stack compose principal.** El despliegue reproducible
> recomendado es `docker-compose.yml` (incluye su propio Traefik y funciona en
> CUALQUIER servidor, con o sin Traefik previo; ver README raiz).
>
> Este `swarm/` es SOLO para hosts que ya tienen un Traefik de Swarm ocupando
> los puertos 80/443 (caso del servidor Contabo `161.97.140.245 / vmi1469533`)
> y que rutean **por labels** (`providers.docker` con `swarmMode: true`).
> Aqui el stack de Mayan se desplega como servicio de Swarm y el Traefik del
> host lo expone en `https://${MAYAN_DOMAIN}` (se toma de `MAYAN_DOMAIN` en el
> `.env`; exportalo antes de desplegar con `set -a; source .env; set +a`).

## 1. Estado actual del Traefik del host (verificado)

- Config estatica: `/root/herramientas_docker/traefik/traefik-data/traefik.yml`
  (montada como `/traefik.yml`, solo lectura).
- Ruteo: docker provider, swarmMode, `exposedByDefault: false` → solo servicios
  con label `traefik.enable=true`.
- Entrypoints: `http` (:80) y `https` (:443). Resolver ACME: `http`
  (httpChallenge en :80). Email ACME ya configurado.
- **IMPORTANTE (bug actual):** el archivo tiene `network: traefik-pubic`
  (le falta la "l"). Si no se corrige, Traefik NO encuentra la IP de los
  servicios sobre `traefik-public` y ninguna ruta funciona.

## 2. Corregir el typo del Traefik del host

No hace falta sudo: el grupo docker equivale a root. Se edita el archivo desde
un contenedor y se fuerza el reinicio de Traefik:

```bash
docker run --rm -v /root/herramientas_docker/traefik/traefik-data:/data alpine \
  sh -c "sed -i 's/traefik-pubic/traefik-public/' /data/traefik.yml && grep -n 'network:' /data/traefik.yml"
docker service update --force traefik_traefik
```

Debe mostrar: `network: traefik-public`.

## 3. Clonar el repo y configurar el .env

```bash
git clone https://github.com/Paul1578/TESIS_DESPLIEGUE.git ~/mayan-docker
cd ~/mayan-docker
cp .env.example .env
nano .env
```

Valores minimos:

- `MAYAN_SECRET_KEY` (generar con `openssl rand -base64 64`)
- `MAYAN_AUTOADMIN_PASSWORD` (password del admin inicial)
- `MAYAN_CSRF_TRUSTED_ORIGINS=['https://herramientagde.byronrm.com', 'http://161.97.140.245:1987']`

## 4. Crear la carpeta de ingesta (/mnt/escaner)

Sin sudo (por docker):

```bash
docker run --rm -v /mnt:/host alpine sh -c "mkdir -p /host/escaner && chmod 777 /host/escaner"
```

## 5. Desplegar el stack

`docker stack deploy` no lee `.env` por si solo; se exportan las variables primero:

```bash
cd ~/mayan-docker
set -a; source .env; set +a
docker stack deploy -c swarm/mayan-stack.yml mayan
```

## 6. Verificar

```bash
docker service ls
docker service ps mayan_app          # que la app este "Running" (primera vez tarda varios min)
docker service logs -f mayan_app     # esperar "success: ... RUNNING"
docker service logs mayan_seed       # debe decir "Seed completado"
```

Accesos:

- LAN: `http://161.97.140.245:1987` (nginx del stack)
- Publico: `https://herramientagde.byronrm.com` (via Traefik, certificado LE)
- Mailpit: `http://161.97.140.245:8025`

El certificado se emite solo cuando el DNS resuelve (ya resuelve a
161.97.140.245) y el puerto 80 es alcanzable desde internet.

## Notas

- `docker compose` del repo NO se usa en este servidor (puerto 80 ocupado por
  el Traefik Swarm y `swarmMode` no descubre contenedores de compose).
- El servicio `nginx` publica el puerto host 1987 solo como acceso LAN de
  respaldo; el trafico publico entra por Traefik (80/443).
- Para actualizar: `git pull`, `set -a; source .env; set +a`,
  `docker stack deploy -c swarm/mayan-stack.yml mayan` (vuelve a sembrar de
  forma idempotente si hace falta).