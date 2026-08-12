# Imagen de Mayan EDMS 4.11.5 con los parches locales.
# Si actualizas el tag base, revisa patches/apply_patches.py (los parches
# se pierden y el script falla a proposito si el archivo ya no coincide).
FROM mayanedms/mayanedms:v4.11.5

COPY patches/apply_patches.py /tmp/apply_patches.py
RUN python3 /tmp/apply_patches.py \
    && rm /tmp/apply_patches.py
