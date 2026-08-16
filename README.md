# TESIS_DESPLIEGUE — Mayan EDMS

Despliegue reproducible de Mayan EDMS 4.11.5 con Docker Compose en cualquier
servidor (tenga o no Traefik previo). Incluye PostgreSQL, Redis, Mailpit (SMTP
de prueba), un **Traefik integrado** (HTTPS con Let's Encrypt) y una imagen
construida con parches locales.

- Imagen pública (sin login): `ghcr.io/paul1578/mayan-edms-preprod:latest`
- Repo: `https://github.com/Paul1578/TESIS_DESPLIEGUE.git`

## Modos de despliegue

| Modo | Cuándo | Cómo |
|---|---|---|
| **Compose (recomendado, reproducible)** | Cualquier servidor: limpio o con Traefik en otros puertos | `docker-compose.yml` incluye su propio Traefik (80/443 configurables) |
| **Swarm (`swarm/`)** | Host que YA tiene un Traefik Swarm ocupando 80/443 (ej. Contabo `161.97.140.245`) | `docker stack deploy -c swarm/mayan-stack.yml mayan` (ver `swarm/README.md`) |

---

## Instalación automática (todo el proceso en 1 comando)

En una máquina nueva (Ubuntu/Debian, aún sin Docker), descarga y ejecuta:

```
curl -fsSL https://raw.githubusercontent.com/Paul1578/TESIS_DESPLIEGUE/main/scripts/instalar.sh -o instalar.sh
bash instalar.sh
```

Ese script hace los pasos 1 a 5 del manual automáticamente e **idempotente**
(vuelve a ejecutarlo las veces que quieras; no duplica nada): instala
git/make/Docker, crea `/mnt/escaner`, clona el repo, genera el `.env`
(secret key + password admin + CSRF con tu IP), levanta el stack (incluye el
Traefik), espera a que Mayan responda y verifica la siembra.

Variantes:

```
INSTALL_ADMIN_PASSWORD=MiClaveSegura bash instalar.sh      # no pregunta nada
INSTALL_CSRF_ORIGINS=192.168.1.50 bash instalar.sh         # fuerza la IP del CSRF
INSTALL_DOMAIN=herramientagde.byronrm.com INSTALL_ACME_EMAIL=tu@correo.com bash instalar.sh  # HTTPS publico
bash instalar.sh --skip-prereqs                            # si ya tienes todo instalado
```

Si ya clonaste el repo, alcanza con: `make install`.

---

## 1. Requisitos

En la máquina destino (local o servidor):

| Software | Nota |
|---|---|
| Docker Engine | Daemon + CLI |
| Docker Compose v2 | Plugin de Docker |
| git | Para clonar y actualizar |
| make | Para usar los comandos cortos |

Instalación por distro:

**Ubuntu / Q4OS-Like:**
```
sudo apt-get install -y docker.io docker-compose-plugin git make
```

**Debian (trixie/12):** el paquete de compose se llama distinto
```
sudo apt-get install -y docker.io docker-compose git make
```

Agregar tu usuario al grupo docker (y **cerrar sesión y volver a entrar**):
```
sudo usermod -aG docker $USER
```

Verificar:
```
docker --version
docker compose version
```

---

## 2. Clonar el repo

```
git clone https://github.com/Paul1578/TESIS_DESPLIEGUE.git ~/mayan-docker
cd ~/mayan-docker
```

---

## 3. Configurar el .env

```
cp .env.example .env
nano .env
```

Valores obligatorios (los demás ya traen defaults razonables):

| Variable | Qué es | Valor sugerido |
|---|---|---|
| `MAYAN_SECRET_KEY` | Clave de Django (obligatoria) | `openssl rand -base64 64` |
| `MAYAN_AUTOADMIN_PASSWORD` | Password del admin inicial (solo se usa la primera vez) | una password fuerte |
| `MAYAN_HTTP_PORT` | Puerto LAN del nginx (acceso por IP, sin Traefik) | `1987` |
| `MAYAN_DOMAIN` | Dominio/subdominio público para HTTPS | vacío (solo LAN) o `herramientagde.byronrm.com` |
| `ACME_EMAIL` | Correo para Let's Encrypt (si hay dominio) | `tu@correo.com` |
| `TRAEFIK_HTTP_PORT` / `TRAEFIK_HTTPS_PORT` | Puertos host del Traefik | `80` / `443` (cámbialos si el host ya los usa) |

Generar la clave secreta (opcional, en otra terminal):
```
openssl rand -base64 64
```

**Producción** (opcional): reemplaza el bloque de email por tu proveedor real
en vez de Mailpit, por ejemplo:
```
MAYAN_EMAIL_HOST=smtp.gmail.com
MAYAN_EMAIL_PORT=587
MAYAN_EMAIL_USE_TLS=true
MAYAN_EMAIL_HOST_USER=tucorreo@gmail.com
MAYAN_EMAIL_HOST_PASSWORD=password-de-aplicacion
MAYAN_DEFAULT_FROM_EMAIL=mayan@tudominio.com
```

---

## 4. Levantar el ambiente

Hay dos formas de obtener la imagen:

- **Local / desarrollo:** construye la imagen con los parches en tu máquina.
- **Servidor:** baja la imagen ya construida desde GHCR (pública, sin login).

> El stack incluye su propio Traefik: en un servidor con 80/443 libres, al
> levantar con `MAYAN_DOMAIN` configurado el sitio queda en `https://<dominio>`.
> Si el host ya usa 80/443, cambia `TRAEFIK_HTTP_PORT`/`TRAEFIK_HTTPS_PORT` o
> usa el modo Swarm (`swarm/`).

### Local (PC de desarrollo)

```
make build        # construye imagen con parches + levanta
```

### Servidor (primera vez)

```
make up           # baja la imagen de GHCR + levanta
```

### Actualizar un despliegue (cualquiera)

```
git pull
make deploy       # = git pull + docker compose pull + up -d + limpiar imagenes viejas
```

### Estructura documental (siembra automática)

En el primer arranque un servicio `seed` crea tipos de documento, metadatos e
índices definidos en `scripts/seed_taxonomy.py` (edita la sección `EDITAR`
con la taxonomía real antes de desplegar). No se repite en arranques
posteriores. Para volver a sembrar:

```
make seed          # idempotente: no duplica lo que ya existe
make seed-force    # borra el marcador y siembra de nuevo
```

### Otros comandos útiles

```
make status       # estado de los contenedores
make logs         # logs en vivo de la app
make down         # apagar y borrar contenedores (conserva datos)
make restart      # reiniciar
make clean        # apagar y borrar VOLUMENES (borra documentos y BD). ¡CUIDADO!
```

---

## 5. Acceso

| Servicio | URL |
|---|---|
| Mayan EDMS (público) | `https://MAYAN_DOMAIN` (si `MAYAN_DOMAIN` está definido) |
| Mayan EDMS (LAN) | `http://IP_MAQUINA:MAYAN_HTTP_PORT` |
| Mailpit (correos capturados) | `http://IP_MAQUINA:8025` |

Credenciales de administrador: `MAYAN_AUTOADMIN_USERNAME` / `MAYAN_AUTOADMIN_PASSWORD`
del `.env`.

> El primer arranque ejecuta migraciones y crea el admin; puede tardar varios
> minutos. Espera hasta que `make logs` deje de mostrar "success: ... RUNNING".

---

## 6. Configuración avanzada

### OCR en español
El stack instala Tesseract con español al arrancar (sin reconstruir la imagen)
y lo deja como idioma por defecto:
```
MAYAN_APT_INSTALLS=tesseract-ocr-spa
MAYAN_OCR_LANGUAGE=spa
```

### Ingesta por carpeta (Watch Folder)
Los PDFs que caigan en `WATCH_FOLDER` del host se montan en
`/var/lib/mayan/watch_folder` del contenedor. Para activarlo:

1. Crea la carpeta en el servidor: `sudo mkdir -p /mnt/escaner`.
2. En Mayan: **Sources → Create source → Watch Folder**, apuntando a
   `/var/lib/mayan/watch_folder` (dentro del contenedor).
3. Copia los PDFs a `/mnt/escaner` y Mayan los ingesta automáticamente.

Si el escáner escribe por red (SMB/NFS), monta el recurso en el host primero
y luego la variable `WATCH_FOLDER` debe apuntar al punto de montaje.

### Reverse proxy y tamaño de subida
El stack incluye dos capas: **Traefik** (gateway público, HTTPS) delante de
**Nginx** (reverse proxy hacia la app, `MAYAN_HTTP_PORT` como puerto LAN).
Nginx permite subidas de hasta **500 MB** (`client_max_body_size` en
`nginx/default.conf`). El túnel de Cloudflare gratuito limita las subidas a
~100 MB; documentos más pesados funcionan por la red local o por Traefik.

### Acceso público (HTTPS con Traefik integrado)
Para publicar el sistema por internet:

1. Configura en el `.env`: `MAYAN_DOMAIN=tu.subdominio.com` y `ACME_EMAIL=tu@correo.com`.
2. El DNS del dominio debe resolver a la IP del servidor (registro A).
3. Abre los puertos `80` y `443` (TCP) en el firewall del servidor.
4. Recarga el stack: `docker compose up -d`. Traefik emite el certificado
   Let's Encrypt automáticamente y redirige HTTP → HTTPS.
5. Agrega el origen a `MAYAN_CSRF_TRUSTED_ORIGINS` en el `.env`
   (ej. `['https://tu.subdominio.com', 'http://IP:MAYAN_HTTP_PORT']`) y vuelve a recargar.

> Si el servidor ya tiene otro servicio en 80/443 (p. ej. un Traefik Swarm),
> cambia `TRAEFIK_HTTP_PORT`/`TRAEFIK_HTTPS_PORT` o usa `swarm/` (integración
> con el Traefik existente, ver `swarm/README.md`). Como último recurso
> (redes que bloquean 80/443) queda el túnel:
> `cloudflared tunnel --url http://127.0.0.1:MAYAN_HTTP_PORT`.

### Correo (SMTP)
Por defecto usa **Mailpit** (SMTP de prueba): los correos no salen a nadie y
se ven en `http://IP:8025`. Para enviar correos reales con Gmail:

1. En tu cuenta de Google activa la **verificación en 2 pasos**.
2. Genera un **password de aplicación** (Google → Seguridad → Passwords de aplicaciones).
3. En el `.env`, descomenta y completa el bloque Gmail (ver `.env.example`).
