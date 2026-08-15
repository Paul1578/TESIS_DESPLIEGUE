import json

from mayan.apps.sources.models import Source
from mayan.apps.documents.models import DocumentType

BACKEND = 'mayan.apps.source_watch_folders.source_backends.SourceBackendWatchFolder'
LABEL = 'Escaner (Watch Folder)'

if Source.objects.filter(label=LABEL).exists():
    print('La fuente ya existe:', LABEL)
else:
    document_type = DocumentType.objects.filter(label='Facturas').first()
    if not document_type:
        document_type = DocumentType.objects.first()

    source = Source(label=LABEL, enabled=True)
    source.backend_path = BACKEND
    source.backend_data = json.dumps(
        {
            'folder_path': '/var/lib/mayan/watch_folder',
            'include_subdirectories': False,
            'document_type_id': str(document_type.pk),
            'language': 'spa',
            'interval': 30,
        }
    )
    source.save()
    print('Fuente creada:', source.label)
    print('Tipo asignado:', document_type.label)
    print('Intervalo: 30s | Idioma OCR: spa')
