import pathlib

PATCHES = [
    {
        'path': pathlib.Path('/opt/mayan-edms/lib/python3.13/site-packages/mayan/apps/authentication/views/authentication_views.py'),
        'marker': 'result = super().dispatch(request=request, *args, **kwargs)\n\n        queryset = self.object_list',
        'old': '        queryset = self.get_queryset(\n            source_queryset=get_all_users_queryset()\n        )',
        'new': '        queryset = self.object_list',
    },
    {
        'path': pathlib.Path('/opt/mayan-edms/lib/python3.13/site-packages/mayan/apps/appearance/templates/appearance/app/head.html'),
        'marker': 'fix-layout',
        'old': '</style>',
        'new': '</style>\n\n<style>\n    /* fix-layout */\n    .table-responsive,\n    .well,\n    .list-group {\n        overflow-x: auto !important;\n    }\n</style>',
    },
    {
        'path': pathlib.Path('/opt/mayan-edms/lib/python3.13/site-packages/mayan/apps/appearance/templates/appearance/app/head.html'),
        'marker': 'appearance-dropdown-fix',
        'old': '</style>',
        'new': '''</style>

<style>
    /* appearance-dropdown-fix */
    .table-responsive:has(.dropdown.open),
    .well:has(.dropdown.open),
    .list-group:has(.dropdown.open),
    .modal:has(.dropdown.open) {
        overflow: visible !important;
    }

    .dropdown-menu {
        z-index: 1030;
    }
</style>''',
    },
    {
        'path': pathlib.Path('/opt/mayan-edms/lib/python3.13/site-packages/mayan/apps/appearance/templates/appearance/app/foot.html'),
        'marker': 'appearance-dropdown-right-align',
        'old': '''<script src="{% static 'appearance/js/partial_navigation.js' %}" type="text/javascript"></script>''',
        'new': '''<script src="{% static 'appearance/js/partial_navigation.js' %}" type="text/javascript"></script>

<script>
(function ($) {
    'use strict';

    const positionDropdownMenu = function ($dropdown) {
        const $menu = $dropdown.children('.dropdown-menu');
        if (!$menu.length) {
            return;
        }
        $menu.removeClass('dropdown-menu-right');
        const menuRight = $menu.offset().left + $menu.outerWidth();
        if (menuRight > window.scrollX + window.innerWidth - 10) {
            $menu.addClass('dropdown-menu-right');
        }
    };

    $(document).on('shown.bs.dropdown', '.dropdown', function () {
        positionDropdownMenu($(this));
    });

    $(document).on('hidden.bs.dropdown', '.dropdown', function () {
        $(this).children('.dropdown-menu').removeClass('dropdown-menu-right');
    });

    $(window).on('resize', function () {
        $('.dropdown.open').each(function () {
            positionDropdownMenu($(this));
        });
    });
})(jQuery);
</script>''',
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
