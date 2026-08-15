#!/bin/bash
set -e

if [ -f /var/lib/mayan/seed_done ]; then
    echo "Seed ya ejecutado (marcador presente). Para re-sembrar: make seed-force"
    exit 0
fi

/opt/mayan-edms/bin/mayan-edms.py shell < /scripts/seed_taxonomy.py
touch /var/lib/mayan/seed_done
echo "Seed completado"
