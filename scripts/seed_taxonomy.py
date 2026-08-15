# Sembrado de la estructura documental base (tipos, metadatos e indices).
# Corre automaticamente la primera vez que se levanta el stack (servicio `seed`),
# y manualmente con:  make seed   /   make seed-force
#
# Es idempotente: no duplica lo que ya existe en la base de datos.
#
# =====================================================================
#  EDITAR AQUI la taxonomia real de la institucion antes de desplegar.
# =====================================================================

# Tipos de documento (DocumentType)
DOCUMENT_TYPES = [
    {'label': 'Facturas'},
    {'label': 'Oficios Recibidos'},
    {'label': 'Contratos'},
    {'label': 'Memorandos'},
]

# Tipos de metadato (MetadataType). `name` debe ser un slug unico.
METADATA_TYPES = [
    {'name': 'numero_documento', 'label': 'Numero de Documento'},
    {'name': 'fecha_emision',    'label': 'Fecha de Emision'},
    {'name': 'ruc_cedula',       'label': 'RUC / Cedula'},
    {'name': 'remitente',        'label': 'Remitente'},
]

# Que metadatos se asocian a cada tipo de documento.
# La clave debe coincidir con un label de DOCUMENT_TYPES.
METADATA_PER_DOCUMENT_TYPE = {
    'Facturas':          ['numero_documento', 'fecha_emision', 'ruc_cedula', 'remitente'],
    'Oficios Recibidos': ['numero_documento', 'fecha_emision', 'remitente'],
    'Contratos':         ['numero_documento', 'fecha_emision', 'remitente'],
    'Memorandos':        ['numero_documento', 'fecha_emision'],
}

# Indice automatico: Anio / Mes / Tipo de documento.
# Cada nivel usa una expresion de plantilla Django sobre el documento.
INDEX_LABEL = 'Por Anio y Mes'
INDEX_NODES = [
    ('Anio',        '{{ document.datetime_created|date:"Y" }}',  False),
    ('Mes',         '{{ document.datetime_created|date:"F" }}',  False),
    ('Tipo',        '{{ document.document_type.label }}',        True),
]

# =====================================================================
#  No editar por debajo de esta linea.
# =====================================================================

from mayan.apps.documents.models import DocumentType
from mayan.apps.metadata.models import DocumentTypeMetadataType, MetadataType
from mayan.apps.document_indexing.models import IndexTemplate, IndexTemplateNode


def seed_document_types():
    created = 0
    for spec in DOCUMENT_TYPES:
        obj, was_created = DocumentType.objects.get_or_create(label=spec['label'])
        created += int(was_created)
    return created


def seed_metadata_types():
    created = 0
    for spec in METADATA_TYPES:
        obj, was_created = MetadataType.objects.get_or_create(
            name=spec['name'], defaults={'label': spec['label']}
        )
        created += int(was_created)
    return created


def seed_document_type_metadata():
    created = 0
    for label, meta_names in METADATA_PER_DOCUMENT_TYPE.items():
        document_type = DocumentType.objects.filter(label=label).first()
        if not document_type:
            print('  AVISO: tipo de documento no existe, se omite:', label)
            continue
        for meta_name in meta_names:
            metadata_type = MetadataType.objects.filter(name=meta_name).first()
            if not metadata_type:
                print('  AVISO: metadato no existe, se omite:', meta_name)
                continue
            _, was_created = DocumentTypeMetadataType.objects.get_or_create(
                document_type=document_type, metadata_type=metadata_type,
                defaults={'required': False}
            )
            created += int(was_created)
    return created


def seed_index():
    index, was_created = IndexTemplate.objects.get_or_create(
        label=INDEX_LABEL,
        defaults={'slug': 'seed-por-anio-y-mes', 'enabled': True}
    )

    # Mayan crea automaticamente el nodo raiz al guardar el indice.
    root = IndexTemplateNode.objects.filter(index=index, parent=None).first()

    created = 0
    parent = root
    for label, expression, link_documents in INDEX_NODES:
        if parent is None:
            print('  AVISO: no hay nodo raiz para el indice', INDEX_LABEL)
            break
        node = IndexTemplateNode.objects.filter(
            index=index, parent=parent, expression=expression
        ).first()
        if not node:
            node = IndexTemplateNode.objects.create(
                index=index,
                parent=parent,
                expression=expression,
                enabled=True,
                link_documents=link_documents,
            )
            created += 1
        parent = node
    return created


print('Sembrando estructura documental...')
total = 0
total += seed_document_types()
total += seed_metadata_types()
total += seed_document_type_metadata()
total += seed_index()
print('Seed terminado. Objetos creados:', total)
