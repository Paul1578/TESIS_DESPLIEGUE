from mayan.apps.documents.models import Document
from mayan.apps.document_indexing.models import IndexTemplate, IndexTemplateNode
from mayan.apps.cabinets.models import Cabinet
from mayan.apps.lock_manager.models import Lock

print('Documentos:', Document.objects.count())
for d in Document.objects.all():
    print('  -', d.label, '|', d.document_type.label)

print('Indices:')
for idx in IndexTemplate.objects.all():
    nodes = IndexTemplateNode.objects.filter(index=idx).order_by('pk')
    print('  *', idx.label, '| slug:', idx.slug, '| enabled:', idx.enabled, '| nodos:', nodes.count())
    for node in nodes:
        print('      node', node.pk, '| parent', node.parent_id, '| link:', node.link_documents, '|', node.expression[:70])

print('Cabinets:')
for c in Cabinet.objects.all():
    print('  -', c.pk, c.label)

print('Locks:', Lock.objects.count())
for l in Lock.objects.all():
    print('  -', l.name[:60], '| expira:', l.expiration_datetime)
