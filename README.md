# TESIS_DESPLIEGUE — Mayan EDMS

Despliegue de Mayan EDMS 4.11.5 con Docker Compose. Incluye PostgreSQL, Redis,
Mailpit (SMTP de prueba) y una imagen construida con parches locales.

- Imagen pública (sin login): `ghcr.io/paul1578/mayan-edms-preprod:latest`
- Repo: `https://github.com/Paul1578/TESIS_DESPLIEGUE.git`

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
| `MAYAN_HTTP_PORT` | Puerto HTTP donde escucha Mayan | `80` en servidor, `18080` en PC local si el 80 está ocupado |

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
| Mayan EDMS | `http://IP_MAQUINA:MAYAN_HTTP_PORT` |
| Mailpit (correos capturados) | `http://IP_MAQUINA:8025` |

Credenciales de administrador: `MAYAN_AUTOADMIN_USERNAME` / `MAYAN_AUTOADMIN_PASSWORD`
del `.env`.

> El primer arranque ejecuta migraciones y crea el admin; puede tardar varios
> minutos. Espera hasta que `make logs` deje de mostrar "success: ... RUNNING".
