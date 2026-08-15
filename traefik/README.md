# Traefik — gateway para herramientagde.byronrm.com

Expone el stack Mayan de este repo por HTTPS en el subdominio
`https://herramientagde.byronrm.com` (certificado Let's Encrypt).

- Backend: `nginx` del stack Mayan, que publica `MAYAN_HTTP_PORT=1987` en el
  host. Traefik corre en la misma maquina y lo alcanza por el gateway de
  Docker: `http://172.17.0.1:1987` (`dynamic/gde.yml`).

## Requisitos previos

1. **DNS:** crear un registro A en `byronrm.com`:
   - `herramientagde` → `161.97.140.245`
   - El certificado NO se emite hasta que el registro resuelva al IP.
2. **Firewall del servidor:** abrir los puertos entrantes **80** y **443**
   (TCP). Verificar con `sudo ufw allow 80/tcp && sudo ufw allow 443/tcp`
   (o el firewall que uses).
3. Docker Engine + Compose v2 instalados.
4. El stack Mayan debe estar levantado con `MAYAN_HTTP_PORT=1987` en su `.env`
   (ver README principal, seccion 3).

## Configuracion

```bash
cd traefik
cp .env.example .env          # editar ACME_EMAIL (tu correo real)
```

En el `.env` de Mayan agregar el nuevo origen (ver `.env.example` del repo):

```
MAYAN_CSRF_TRUSTED_ORIGINS=['https://herramientagde.byronrm.com']
```

y recargar el stack (`make restart`) para que lo tome.

## Puesta en marcha

```bash
docker compose up -d          # levanta Traefik (puertos 80 y 443)
docker compose ps             # traefik debe quedar "healthy"
```

## Verificacion

```bash
docker compose logs -f traefik | grep -i "herramientagde"   # ver rutas y certs
curl -I https://herramientagde.byronrm.com                   # 200/302 tras emitir cert
```

## Notas

- Redireccion automatica HTTP → HTTPS (entrypoint `web`).
- Renovacion automatica de certificados (ACME). El cert solo se genera cuando
  el DNS resuelve al IP y el puerto 80 es alcanzable desde internet.
- El backend usa `172.17.0.1:1987` (gateway de Docker) para evitar hairpin por
  la IP publica; funciona porque `nginx` del stack publica 1987 en el host.

## Archivos

| Archivo | Descripcion |
|---|---|
| `docker-compose.yml` | Servicio Traefik (80/443, acme.json, config dinamica) |
| `dynamic/gde.yml` | Router/servicio para `herramientagde.byronrm.com` |
| `.env` | `ACME_EMAIL` y nivel de log |
| `acme.json` | Almacen de certificados (permisos 600) |
