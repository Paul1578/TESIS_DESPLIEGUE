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
        'remove': True,
        'old': '\n\n<style>\n    /* appearance-dropdown-fix */\n    .table-responsive:has(.dropdown.open),\n    .well:has(.dropdown.open),\n    .list-group:has(.dropdown.open),\n    .modal:has(.dropdown.open) {\n        overflow: visible !important;\n    }\n\n    .dropdown-menu {\n        z-index: 1030;\n    }\n</style>',
    },
    {
        'path': pathlib.Path('/opt/mayan-edms/lib/python3.13/site-packages/mayan/apps/appearance/templates/appearance/app/foot.html'),
        'marker': 'const positionDropdownMenu',
        'remove': True,
        'old': '''\n\n<script>
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
    {
        'path': pathlib.Path('/opt/mayan-edms/lib/python3.13/site-packages/mayan/apps/appearance/templates/appearance/app/foot.html'),
        'marker': 'appearance-dropdown-overlay',
        'old': '''<script src="{% static 'appearance/js/partial_navigation.js' %}" type="text/javascript"></script>''',
        'new': '''<script src="{% static 'appearance/js/partial_navigation.js' %}" type="text/javascript"></script>

<script>
(function ($) {
    'use strict';

    const overlayId = 'appearance-dropdown-overlay';
    let overlay = null;
    let openMenu = null;

    function getOverlay() {
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = overlayId;
            overlay.setAttribute(
                'style',
                'position: fixed; top: 0; left: 0; width: 0; height: 0; z-index: 1060; pointer-events: none;'
            );
            document.body.appendChild(overlay);
        }
        return overlay;
    }

    function needsPortal($dropdown) {
        let clipped = false;

        $dropdown.parents().each(function () {
            if (this === document.body || this === document.documentElement) {
                return;
            }
            const style = window.getComputedStyle(this);
            if (style.overflowX !== 'visible' || style.overflowY !== 'visible') {
                clipped = true;
                return false;
            }
        });

        return clipped;
    }

    function portalZIndex($dropdown) {
        let zIndex = 1060;

        $dropdown.parents().each(function () {
            const style = window.getComputedStyle(this);
            const elementZIndex = parseInt(style.zIndex, 10);

            if (style.position !== 'static' && !Number.isNaN(elementZIndex) && elementZIndex > 0) {
                zIndex = elementZIndex + 10;
                return false;
            }
        });

        return zIndex;
    }

    function positionMenu() {
        const toggleRect = openMenu.toggle.getBoundingClientRect();
        const menuHeight = openMenu.menu.offsetHeight;
        const menuWidth = openMenu.menu.offsetWidth;
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        let top;
        let left;

        if (
            toggleRect.bottom + menuHeight > viewportHeight - 8 &&
            toggleRect.top - menuHeight > 8
        ) {
            top = toggleRect.top - menuHeight - 2;
        } else {
            top = toggleRect.bottom + 2;
        }

        if (
            toggleRect.right + menuWidth > viewportWidth - 8 &&
            toggleRect.left - menuWidth > 8
        ) {
            left = toggleRect.right - menuWidth;
        } else {
            left = toggleRect.left;
        }

        left = Math.max(8, Math.min(left, viewportWidth - menuWidth - 8));
        top = Math.max(8, top);

        openMenu.menu.style.left = `${left}px`;
        openMenu.menu.style.top = `${top}px`;
    }

    function closeMenu(remove) {
        if (!openMenu) {
            return;
        }

        const menu = openMenu.menu;

        if (!remove && openMenu.dropdown) {
            openMenu.dropdown.appendChild(menu);
        } else {
            $(menu).remove();
        }

        menu.style.display = '';
        menu.style.position = '';
        menu.style.margin = '';
        menu.style.left = '';
        menu.style.top = '';
        menu.style.maxWidth = '';
        menu.style.maxHeight = '';
        menu.style.overflow = '';
        menu.style.overflowY = '';
        menu.style.pointerEvents = '';

        openMenu = null;
    }

    function openMenuPortal($dropdown) {
        const $menu = $dropdown.children('.dropdown-menu');

        if (!$menu.length || !needsPortal($dropdown)) {
            return;
        }

        closeMenu(false);

        const menu = $menu[0];
        const overlayElement = getOverlay();

        overlayElement.style.zIndex = portalZIndex($dropdown);
        overlayElement.appendChild(menu);

        menu.style.display = 'block';
        menu.style.position = 'fixed';
        menu.style.margin = '0';
        menu.style.pointerEvents = 'auto';
        menu.style.maxWidth = `${window.innerWidth - 16}px`;
        menu.style.maxHeight = `${window.innerHeight - 16}px`;

        if (menu.scrollHeight > menu.clientHeight) {
            menu.style.overflowY = 'auto';
        }

        openMenu = {
            menu: menu,
            dropdown: $dropdown[0],
            toggle: $dropdown.find('.dropdown-toggle')[0] || $dropdown[0]
        };

        positionMenu();
    }

    $(document).on('shown.bs.dropdown', '.dropdown', function () {
        openMenuPortal($(this));
    });

    $(document).on('hidden.bs.dropdown', '.dropdown', function () {
        if (openMenu && openMenu.dropdown === this) {
            closeMenu(false);
        }
    });

    window.addEventListener('scroll', function () {
        if (openMenu) {
            positionMenu();
        }
    }, true);

    window.addEventListener('resize', function () {
        if (openMenu) {
            positionMenu();
        }
    });

    $(document).on('updated', '#ajax-content', function () {
        closeMenu(true);
    });
})(jQuery);
</script>''',
    },
]


def apply(patch):
    content = patch['path'].read_text()
    if patch.get('remove'):
        if patch['marker'] not in content:
            print(f'SKIP (ya eliminado): {patch["path"]}')
            return
        if patch['old'] not in content:
            raise SystemExit(f'ERROR (remove): el bloque {patch["marker"]} no coincide en {patch["path"]}')
        patch['path'].write_text(content.replace(patch['old'], '', 1))
        print(f'REMOVE OK: {patch["path"]}')
        return
    if patch['marker'] in content:
        print(f'SKIP (ya aplicado): {patch["path"]}')
        return
    if patch['old'] not in content:
        raise SystemExit(f'ERROR: el archivo {patch["path"]} no coincide con la version esperada de Mayan 4.11.5')
    patch['path'].write_text(content.replace(patch['old'], patch['new'], 1))
    print(f'PATCH OK: {patch["path"]}')


for patch in PATCHES:
    apply(patch)
