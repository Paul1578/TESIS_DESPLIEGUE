#!/usr/bin/env bash
# Despliega el stack de Swarm para hosts con Traefik Swarm existente (swarm/).
#
# Carga .env de forma robusta: `set -a; source .env` rompe con valores que
# contienen espacios (ej. MAYAN_DOCKER_WAIT o la CSRF) o claves partidas en
# varias lineas. Aqui cada linea se exporta como un solo valor.
#
# Uso:
#   bash scripts/stack_deploy.sh [nombre_del_stack]
set -euo pipefail

STACK_NAME="${1:-mayan}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STACK_FILE="$ROOT/swarm/mayan-stack.yml"
ENV_FILE="${ENV_FILE:-$ROOT/.env}"

[ -f "$ENV_FILE" ] || { echo "ERROR: no existe $ENV_FILE (copia .env.example)" >&2; exit 1; }
[ -f "$STACK_FILE" ] || { echo "ERROR: no existe $STACK_FILE" >&2; exit 1; }

while IFS= read -r line || [ -n "$line" ]; do
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
        export "$key=$val"
    else
        echo "AVISO: linea ignorada (no es KEY=valor): $line" >&2
    fi
done < "$ENV_FILE"

echo "Desplegando stack '$STACK_NAME' desde $STACK_FILE"
docker stack deploy -c "$STACK_FILE" "$STACK_NAME"