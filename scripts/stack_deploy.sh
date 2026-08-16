#!/usr/bin/env bash
# Despliega el stack de Swarm para hosts con Traefik Swarm existente (swarm/).
#
# VALIDA antes de desplegar (para que los errores tipicos no lleguen a otro
# servidor):
#   - .env sin comentarios pegados ('#' dentro de un valor)
#   - variables obligatorias presentes (MAYAN_SECRET_KEY, MAYAN_DOMAIN, ...)
#   - MAYAN_DOCKER_WAIT con formato host:puerto
#   - memoria suficiente (RAM+swap) para el primer arranque de Mayan
#
# Uso:
#   bash scripts/stack_deploy.sh [nombre_del_stack]
set -euo pipefail

STACK_NAME="${1:-mayan}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STACK_FILE="$ROOT/swarm/mayan-stack.yml"
ENV_FILE="${ENV_FILE:-$ROOT/.env}"

fail() { echo "ERROR: $*" >&2; exit 1; }

[ -f "$ENV_FILE" ] || fail "no existe $ENV_FILE (copia .env.example a .env)"
[ -f "$STACK_FILE" ] || fail "no existe $STACK_FILE"

# ---------- 1. Cargar y validar .env ----------
errors=0
declare -A cfg=()
while IFS= read -r line || [ -n "$line" ]; do
    line="${line#"${line%%[![:space:]]*}"}"   # quita espacios iniciales
    line="${line%"${line##*[![:space:]]}"}"   # quita espacios finales
    case "$line" in
        '#'*|'') continue ;;
    esac
    if [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then
        key="${line%%=*}"
        val="${line#*=}"
        case "$val" in
            \"*\") val="${val#\"}"; val="${val%\"}" ;;
            \'*\') val="${val#\'}"; val="${val%\'}" ;;
        esac
        if [[ "$val" == *'#'* ]]; then
            echo "ERROR en .env: '$key' tiene un '#' dentro del valor (comentario pegado):" >&2
            echo "  $key=$val" >&2
            errors=1
            continue
        fi
        cfg["$key"]="$val"
    else
        echo "AVISO: linea ignorada (no es KEY=valor): $line" >&2
    fi
done < "$ENV_FILE"

for k in MAYAN_SECRET_KEY MAYAN_AUTOADMIN_PASSWORD MAYAN_DOMAIN MAYAN_CSRF_TRUSTED_ORIGINS; do
    if [ -z "${cfg[$k]:-}" ]; then
        echo "ERROR en .env: falta '$k' (obligatoria)" >&2
        errors=1
    fi
done

if [ -n "${cfg[MAYAN_SECRET_KEY]:-}" ] && [ "${#cfg[MAYAN_SECRET_KEY]}" -lt 32 ]; then
    echo "ERROR en .env: MAYAN_SECRET_KEY demasiado corta (usa: openssl rand -base64 64 | tr -d '\\n')" >&2
    errors=1
fi

if [ -n "${cfg[MAYAN_DOCKER_WAIT]:-}" ]; then
    for tok in ${cfg[MAYAN_DOCKER_WAIT]}; do
        [[ "$tok" =~ ^[^:]+:[0-9]+$ ]] || {
            echo "ERROR en .env: MAYAN_DOCKER_WAIT invalido ('$tok'); formato esperado host:puerto (ej. postgresql:5432 redis:6379)" >&2
            errors=1
        }
    done
fi

if [ -n "${cfg[MAYAN_DOMAIN]:-}" ] && [ -n "${cfg[MAYAN_CSRF_TRUSTED_ORIGINS]:-}" ]; then
    [[ "${cfg[MAYAN_CSRF_TRUSTED_ORIGINS]}" == *"${cfg[MAYAN_DOMAIN]}"* ]] || {
        echo "ADVERTENCIA: MAYAN_CSRF_TRUSTED_ORIGINS no incluye https://${cfg[MAYAN_DOMAIN]}; el login desde el dominio publico fallara" >&2
    }
fi

[ "$errors" -eq 0 ] || fail ".env tiene problemas; corregilos y volve a correr"

for k in "${!cfg[@]}"; do
    export "$k=${cfg[$k]}"
done

# ---------- 2. Chequear memoria (RAM + swap) ----------
mem_kb="$(awk '/MemTotal/{print $2}' /proc/meminfo)"
swap_kb="$(awk '/SwapTotal/{print $2}' /proc/meminfo)"
total_mb=$(( (mem_kb + swap_kb) / 1024 ))
if [ "$total_mb" -lt 3072 ]; then
    fail "poca memoria: ${total_mb}MB (RAM+swap). Mayan muere (OOM, exit 137) al migrar la primera vez. Activa swap: docker run --rm --privileged -v /:/host alpine sh -c \"fallocate -l 4G /host/swapfile && chmod 600 /host/swapfile && mkswap /host/swapfile && swapon /host/swapfile\""
elif [ "$total_mb" -lt 4096 ]; then
    echo "ADVERTENCIA: memoria justa (${total_mb}MB RAM+swap). Si un contenedor muere con exit 137, activa swap (ver README)." >&2
fi

echo "Desplegando stack '$STACK_NAME' desde $STACK_FILE"
docker stack deploy -c "$STACK_FILE" "$STACK_NAME"