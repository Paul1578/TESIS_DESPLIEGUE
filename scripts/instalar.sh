#!/usr/bin/env bash
#
# instalar.sh - Despliegue automatico de Mayan EDMS desde cero (TESIS_DESPLIEGUE)
#
# Hace todo el "Parte B / Pasos 0 a 5" en un solo comando:
#   0. Requisitos (git, make, docker + compose v2)
#   1. Carpeta de ingesta del escaner (/mnt/escaner)
#   2. Clonar el repo (~/mayan-docker)
#   3. Generar .env (secret key, password admin, CSRF) si faltan
#   4. docker compose up -d + esperar a que Mayan responda
#   5. Verificacion: seed completado + resumen
#
# Uso:
#   bash instalar.sh                 # interactivo (pide password admin si quieres)
#   INSTALL_ADMIN_PASSWORD=MiClave bash instalar.sh
#   INSTALL_CSRF_ORIGINS=192.168.1.50 bash instalar.sh
#   bash instalar.sh --skip-prereqs  # si ya tenes todo instalado
#
# Nota: al primer arranque tarda varios minutos (migraciones + OCR + seed).

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/Paul1578/TESIS_DESPLIEGUE.git}"
REPO_DIR="${MAYAN_DOCKER_DIR:-$HOME/mayan-docker}"
WATCH_FOLDER="${WATCH_FOLDER:-/mnt/escaner}"
HTTP_PORT_DEFAULT=80
SKIP_PREREQS=0

# ---------- helpers ----------
if [ -t 1 ] && [ -n "$TERM" ] && [ "$TERM" != "dumb" ]; then
  C_INFO="\033[1;34m"; C_OK="\033[1;32m"; C_WARN="\033[1;33m"; C_ERR="\033[1;31m"; C_END="\033[0m"
else
  C_INFO=""; C_OK=""; C_WARN=""; C_ERR=""; C_END=""
fi

info(){ printf "${C_INFO}[INFO]${C_END} %s\n" "$*"; }
ok(){   printf "${C_OK}[OK]${C_END}   %s\n" "$*"; }
warn(){ printf "${C_WARN}[WARN]${C_END} %s\n" "$*"; }
fail(){ printf "${C_ERR}[ERROR]${C_END} %s\n" "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] && SUDO="" || SUDO="sudo"

detect_docker_access() {
  if docker ps >/dev/null 2>&1; then
    DOCK="docker"
  elif $SUDO docker ps >/dev/null 2>&1; then
    DOCK="$SUDO docker"
  else
    DOCK=""
  fi
}

# ---------- Paso 0 ----------
install_prereqs() {
  command -v apt-get >/dev/null 2>&1 || fail "Este script asume Debian/Ubuntu (apt)."
  command -v openssl >/dev/null 2>&1 || $SUDO apt-get install -y -qq openssl >/dev/null

  if ! command -v git >/dev/null 2>&1 || ! command -v make >/dev/null 2>&1; then
    info "Instalando git y make..."
    $SUDO apt-get update -qq
    $SUDO apt-get install -y -qq git make >/dev/null
  fi

  if ! command -v docker >/dev/null 2>&1; then
    info "Instalando Docker (docker-ce + plugin compose v2) via get.docker.com..."
    curl -fsSL https://get.docker.com | $SUDO sh
  fi

  if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1 \
     && ! $SUDO docker compose version >/dev/null 2>&1; then
    warn "docker compose v2 no disponible; reintentando instalacion de Docker..."
    curl -fsSL https://get.docker.com | $SUDO sh
  fi

  $SUDO docker compose version >/dev/null 2>&1 \
    || fail "docker compose v2 no esta disponible. Instalalo manualmente y volve a correr."

  $SUDO systemctl enable --now docker >/dev/null 2>&1 || true

  if ! id -nG "$USER" | tr ' ' '\n' | grep -qx docker; then
    $SUDO usermod -aG docker "$USER" || true
    warn "Usuario agregado al grupo docker. En la PROXIMA sesion ya no haran falta sudo (re-logeate)."
  fi
}

# ---------- Paso 1 ----------
setup_watch_folder() {
  if [ ! -d "$WATCH_FOLDER" ]; then
    $SUDO mkdir -p "$WATCH_FOLDER"
    info "Creada la carpeta de ingesta $WATCH_FOLDER"
  fi
  $SUDO chown "$USER:$USER" "$WATCH_FOLDER"
  ok "Watch Folder listo: $WATCH_FOLDER"
}

# ---------- Paso 2 ----------
clone_repo() {
  if [ -d "$REPO_DIR/.git" ]; then
    info "Repo ya clonado en $REPO_DIR (se omite el clone)."
  else
    info "Clonando $REPO_URL en $REPO_DIR ..."
    mkdir -p "$REPO_DIR"
    git clone "$REPO_URL" "$REPO_DIR"
  fi
  cd "$REPO_DIR"
}

# ---------- Paso 3 ----------
# set_env KEY VALUE : rellena una linea "KEY=" vacia en .env
set_env() {
  local key="$1" val="$2"
  val="${val//&/\\&}"            # escapar & para sed (por las dudas)
  sed -i "s|^${key}=$|${key}=${val}|" .env
  grep -qE "^${key}=" .env || printf '%s=%s\n' "$key" "$val" >> .env
}

# set_env_uncomment KEY VALUE : reemplaza la linea comentada "# KEY=..." por la activa
set_env_uncomment() {
  local key="$1" val="$2"
  sed -i "s|^# ${key}=.*|${val}|" .env
  grep -qE "^${key}=" .env || printf '%s\n' "$val" >> .env
}

configure_env() {
  if [ ! -f .env ]; then
    cp .env.example .env
    info ".env creado desde .env.example"
  else
    info ".env ya existe; solo se rellenan valores vacios."
  fi

  if grep -qE '^MAYAN_SECRET_KEY=.+' .env; then
    ok "MAYAN_SECRET_KEY ya definida."
  else
    local secret
    secret="$(openssl rand -base64 64 | tr -d '\n')"
    set_env "MAYAN_SECRET_KEY" "$secret"
    ok "MAYAN_SECRET_KEY generada."
  fi

  if grep -qE '^MAYAN_AUTOADMIN_PASSWORD=.+' .env; then
    ok "MAYAN_AUTOADMIN_PASSWORD ya definida."
  else
    local password="${INSTALL_ADMIN_PASSWORD:-}"
    if [ -z "$password" ] && [ -t 0 ]; then
      read -rsp "Password del admin (deja vacio para generar una): " password
      echo
    fi
    if [ -z "$password" ]; then
      password="$(openssl rand -base64 18 | tr -d '\n')"
      warn "Password admin generada (guardala): $password"
    else
      case "$password" in
        *'|'*|*'&'*) fail "La password no puede contener '|' ni '&'. Volve a correr.";;
      esac
    fi
    set_env "MAYAN_AUTOADMIN_PASSWORD" "$password"
    ok "MAYAN_AUTOADMIN_PASSWORD definida."
  fi

  if grep -qE '^MAYAN_CSRF_TRUSTED_ORIGINS=' .env; then
    ok "MAYAN_CSRF_TRUSTED_ORIGINS ya definido."
  else
    local ip="${INSTALL_CSRF_ORIGINS:-}"
    if [ -z "$ip" ]; then
      local ip_dflt
      ip_dflt="$(hostname -I 2>/dev/null | awk '{print $1}')"
      if [ -t 0 ] && [ -n "$ip_dflt" ]; then
        read -r -p "IP local para CSRF (Enter para usar $ip_dflt): " ip_in
        [ -n "$ip_in" ] && ip="$ip_in"
      fi
      [ -z "$ip" ] && ip="$ip_dflt"
    fi
    if [ -n "$ip" ]; then
      set_env_uncomment "MAYAN_CSRF_TRUSTED_ORIGINS" "MAYAN_CSRF_TRUSTED_ORIGINS=['http://$ip']"
      ok "MAYAN_CSRF_TRUSTED_ORIGINS=['http://$ip']"
    else
      warn "No se pudo detectar la IP; dejala configurada en .env si el login falla por CSRF."
    fi
  fi
}

# ---------- Paso 4 ----------
http_port() { grep -E '^MAYAN_HTTP_PORT=' .env 2>/dev/null | cut -d= -f2- | tr -d ' '; }

start_stack() {
  info "Levantando el stack (primer arranque: varios minutos)..."
  $DOCK compose up -d
}

wait_http() {
  local port
  port="$(http_port)"; [ -n "$port" ] || port="$HTTP_PORT_DEFAULT"
  local url="http://127.0.0.1:${port}/"
  local tries=90 i=0
  printf "Esperando a que Mayan responda (%s) " "$url"
  while [ "$i" -lt "$tries" ]; do
    if curl -fs -o /dev/null "$url" 2>/dev/null; then
      printf "\n"; ok "Mayan responde en $url"
      return 0
    fi
    i=$((i + 1)); sleep 10; printf "."
  done
  printf "\n"
  fail "Mayan no respondio tras $((tries * 10))s. Revisa: $DOCK compose logs --tail=100 app"
}

seed_state() {
  local cid
  cid="$($DOCK compose ps -a -q seed 2>/dev/null | head -1)" || true
  [ -z "$cid" ] && { echo "pending"; return; }
  $DOCK inspect "$cid" --format '{{.State.Status}}|{{.State.ExitCode}}' 2>/dev/null || echo "pending"
}

wait_seed() {
  local tries=30 i=0 state logs
  printf "Esperando al servicio seed "
  while [ "$i" -lt "$tries" ]; do
    logs="$($DOCK compose logs seed --tail=200 2>/dev/null || true)"
    if echo "$logs" | grep -qE 'Seed completado|ya ejecutado'; then
      printf "\n"; ok "Seed completado."
      return 0
    fi
    state="$(seed_state)"
    case "$state" in
      exited\|[1-9]*)
        printf "\n"; fail "El seed fallo (estado $state). Revisa: $DOCK compose logs seed";;
      exited\|0)
        printf "\n"; ok "Seed terminado (exit 0)."
        return 0;;
    esac
    i=$((i + 1)); sleep 10; printf "."
  done
  printf "\n"
  warn "El seed no termino a tiempo. Revisa: $DOCK compose logs seed"
}

# ---------- resumen ----------
print_summary() {
  local port
  port="$(http_port)"; [ -n "$port" ] || port="$HTTP_PORT_DEFAULT"
  echo
  ok "=========================================================="
  ok "  Mayan EDMS desplegado"
  ok "=========================================================="
  info "URL:        http://<IP-de-este-servidor>:${port}"
  info "Admin:      admin"
  info "Password:   la de MAYAN_AUTOADMIN_PASSWORD en $REPO_DIR/.env"
  info "Watch:      $WATCH_FOLDER  (los PDFs que caigan se ingieren en <=30s)"
  info "Mailpit:    http://<IP>:8025  (correos de prueba, no salen a internet)"
  echo
  info "Comandos utiles (dentro de $REPO_DIR):"
  info "  make status   # estado de los contenedores"
  info "  make logs     # logs en vivo de la app"
  info "  make deploy   # git pull + bajar imagen + up -d"
  info "  make seed     # re-ejecutar el seed (idempotente)"
  info "  make clean    # BORRA TODO (documentos y BD)"
  echo
  info "Acceso externo (opcional):"
  info "  cloudflared tunnel --url http://127.0.0.1:${port} --logfile ~/cloudflared.log &"
  info "  Luego agregar la URL a MAYAN_CSRF_TRUSTED_ORIGINS en .env y: docker compose up -d"
}

usage() {
  sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'
  exit 0
}

main() {
  for arg in "$@"; do
    case "$arg" in
      --help|-h) usage;;
      --skip-prereqs) SKIP_PREREQS=1;;
      *) warn "Argumento ignorado: $arg";;
    esac
  done

  [ "$SKIP_PREREQS" -eq 0 ] && install_prereqs
  detect_docker_access
  [ -n "$DOCK" ] || fail "No se pudo acceder a docker (probá de nuevo tras re-logear al grupo docker)."

  setup_watch_folder
  clone_repo
  configure_env
  start_stack
  wait_http
  wait_seed
  print_summary
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  main "$@"
fi
