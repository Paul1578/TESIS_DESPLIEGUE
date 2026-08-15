# Traefik — gateway para herramientagde.byronrm.com

Expone la app que corre en `http://161.97.140.245:1987` por HTTPS en el
subdominio `https://herramientagde.byronrm.com` (certificado Let's Encrypt).

## Requisitos previos

1. **DNS:** crear un registro A en `byronrm.com`:
   - `herramientagde` → `161.97.140.245`
   - El certificado NO se emite hasta que el registro resuelva al IP.
2. **Firewall del servidor:** abrir los puertos entrantes **80** y **443**
   (TCP). Verificar con `sudo ufw allow 80/tcp && sudo ufw allow 443/tcp`
   (o el firewall que uses).
3. Docker Engine + Compose v2 instalados.

## Configuracion

```bash
cd traefik-gde
cp .env.example .env          # editar ACME_EMAIL (tu correo real)
# si la app no esta en 161.97.140.245:1987, cambiar la URL en dynamic/gde.yml
```

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
- Si `http://161.97.140.245:1987` es el propio host (hairpin) y da problemas,
  cambiar la URL en `dynamic/gde.yml` a `http://172.17.0.1:1987` (gateway de Docker).
- La app en :1987 debe aceptar el origen `https://herramientagde.byronrm.com`
  (en Mayan: agregarlo a `MAYAN_CSRF_TRUSTED_ORIGINS` y `MAYAN_ALLOWED_HOSTS`).

## Archivos

| Archivo | Descripcion |
|---|---|
| `docker-compose.yml` | Servicio Traefik (80/443, acme.json, config dinamica) |
| `dynamic/gde.yml` | Router/servicio para `herramientagde.byronrm.com` |
| `.env` | `ACME_EMAIL` y nivel de log |
| `acme.json` | Almacen de certificados (permisos 600) |
