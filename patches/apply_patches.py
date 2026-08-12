import pathlib

PATCHES = [
    {
        'path': pathlib.Path('/opt/mayan-edms/lib/python3.13/site-packages/mayan/apps/authentication/views/authentication_views.py'),
        'marker': 'queryset = self.object_list',
        'old': '        queryset = self.get_queryset(\n            source_queryset=get_all_users_queryset()\n        )',
        'new': '        queryset = self.object_list',
    },
    {
        'path': pathlib.Path('/opt/mayan-edms/lib/python3.13/site-packages/mayan/apps/appearance/templates/appearance/app/head.html'),
        'marker': 'fix-layout',
        'old': '</style>',
        'new': '</style>\n\n<style>\n    /* fix-layout */\n    .table-responsive,\n    .well,\n    .list-group {\n        overflow-x: auto !important;\n    }\n</style>',
    },
]


def apply(patch):
    content = patch['path'].read_text()
    if patch['marker'] in content:
        print(f'SKIP (ya aplicado): {patch["path"]}')
        return
    if patch['old'] not in content:
        raise SystemExit(f'ERROR: el archivo {patch["path"]} no coincide con la version esperada de Mayan 4.11.5')
    patch['path'].write_text(content.replace(patch['old'], patch['new'], 1))
    print(f'PATCH OK: {patch["path"]}')


for patch in PATCHES:
    apply(patch)
