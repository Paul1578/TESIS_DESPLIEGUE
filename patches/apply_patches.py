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
        'remove': True,
        'path': pathlib.Path('/opt/mayan-edms/lib/python3.13/site-packages/mayan/apps/appearance/templates/appearance/app/head.html'),
        'marker': 'appearance-dropdown-fix',
        'old': '\n\n<style>\n    /* appearance-dropdown-fix */\n    .table-responsive:has(.dropdown.open),\n    .well:has(.dropdown.open),\n    .list-group:has(.dropdown.open),\n    .modal:has(.dropdown.open) {\n        overflow: visible !important;\n    }\n\n    .dropdown-menu {\n        z-index: 1030;\n    }\n</style>',
    },
    {
        'remove': True,
        'path': pathlib.Path('/opt/mayan-edms/lib/python3.13/site-packages/mayan/apps/appearance/templates/appearance/app/foot.html'),
        'marker': 'const positionDropdownMenu',
        'old': "\n\n<script>\n(function ($) {\n    'use strict';\n\n    const positionDropdownMenu = function ($dropdown) {\n        const $menu = $dropdown.children('.dropdown-menu');\n        if (!$menu.length) {\n            return;\n        }\n        $menu.removeClass('dropdown-menu-right');\n        const menuRight = $menu.offset().left + $menu.outerWidth();\n        if (menuRight > window.scrollX + window.innerWidth - 10) {\n            $menu.addClass('dropdown-menu-right');\n        }\n    };\n\n    $(document).on('shown.bs.dropdown', '.dropdown', function () {\n        positionDropdownMenu($(this));\n    });\n\n    $(document).on('hidden.bs.dropdown', '.dropdown', function () {\n        $(this).children('.dropdown-menu').removeClass('dropdown-menu-right');\n    });\n\n    $(window).on('resize', function () {\n        $('.dropdown.open').each(function () {\n            positionDropdownMenu($(this));\n        });\n    });\n})(jQuery);\n</script>",
    },
    {
        'remove': True,
        'path': pathlib.Path('/opt/mayan-edms/lib/python3.13/site-packages/mayan/apps/appearance/templates/appearance/app/foot.html'),
        'marker': 'appearance-dropdown-overlay',
        'old': "\n\n<script>\n(function ($) {\n    'use strict';\n\n    const overlayId = 'appearance-dropdown-overlay';\n    let overlay = null;\n    let openMenu = null;\n\n    function getOverlay() {\n        if (!overlay) {\n            overlay = document.createElement('div');\n            overlay.id = overlayId;\n            overlay.setAttribute(\n                'style',\n                'position: fixed; top: 0; left: 0; width: 0; height: 0; z-index: 1060; pointer-events: none;'\n            );\n            document.body.appendChild(overlay);\n        }\n        return overlay;\n    }\n\n    function needsPortal($dropdown) {\n        let clipped = false;\n\n        $dropdown.parents().each(function () {\n            if (this === document.body || this === document.documentElement) {\n                return;\n            }\n            const style = window.getComputedStyle(this);\n            if (style.overflowX !== 'visible' || style.overflowY !== 'visible') {\n                clipped = true;\n                return false;\n            }\n        });\n\n        return clipped;\n    }\n\n    function portalZIndex($dropdown) {\n        let zIndex = 1060;\n\n        $dropdown.parents().each(function () {\n            const style = window.getComputedStyle(this);\n            const elementZIndex = parseInt(style.zIndex, 10);\n\n            if (style.position !== 'static' && !Number.isNaN(elementZIndex) && elementZIndex > 0) {\n                zIndex = elementZIndex + 10;\n                return false;\n            }\n        });\n\n        return zIndex;\n    }\n\n    function positionMenu() {\n        const toggleRect = openMenu.toggle.getBoundingClientRect();\n        const menuHeight = openMenu.menu.offsetHeight;\n        const menuWidth = openMenu.menu.offsetWidth;\n        const viewportWidth = window.innerWidth;\n        const viewportHeight = window.innerHeight;\n        let top;\n        let left;\n\n        if (\n            toggleRect.bottom + menuHeight > viewportHeight - 8 &&\n            toggleRect.top - menuHeight > 8\n        ) {\n            top = toggleRect.top - menuHeight - 2;\n        } else {\n            top = toggleRect.bottom + 2;\n        }\n\n        if (\n            toggleRect.right + menuWidth > viewportWidth - 8 &&\n            toggleRect.left - menuWidth > 8\n        ) {\n            left = toggleRect.right - menuWidth;\n        } else {\n            left = toggleRect.left;\n        }\n\n        left = Math.max(8, Math.min(left, viewportWidth - menuWidth - 8));\n        top = Math.max(8, top);\n\n        openMenu.menu.style.left = `${left}px`;\n        openMenu.menu.style.top = `${top}px`;\n    }\n\n    function closeMenu(remove) {\n        if (!openMenu) {\n            return;\n        }\n\n        const menu = openMenu.menu;\n\n        if (!remove && openMenu.dropdown) {\n            openMenu.dropdown.appendChild(menu);\n        } else {\n            $(menu).remove();\n        }\n\n        menu.style.display = '';\n        menu.style.position = '';\n        menu.style.margin = '';\n        menu.style.left = '';\n        menu.style.top = '';\n        menu.style.maxWidth = '';\n        menu.style.maxHeight = '';\n        menu.style.overflow = '';\n        menu.style.overflowY = '';\n        menu.style.pointerEvents = '';\n\n        openMenu = null;\n    }\n\n    function openMenuPortal($dropdown) {\n        const $menu = $dropdown.children('.dropdown-menu');\n\n        if (!$menu.length || !needsPortal($dropdown)) {\n            return;\n        }\n\n        closeMenu(false);\n\n        const menu = $menu[0];\n        const overlayElement = getOverlay();\n\n        overlayElement.style.zIndex = portalZIndex($dropdown);\n        overlayElement.appendChild(menu);\n\n        menu.style.display = 'block';\n        menu.style.position = 'fixed';\n        menu.style.margin = '0';\n        menu.style.pointerEvents = 'auto';\n        menu.style.maxWidth = `${window.innerWidth - 16}px`;\n        menu.style.maxHeight = `${window.innerHeight - 16}px`;\n\n        if (menu.scrollHeight > menu.clientHeight) {\n            menu.style.overflowY = 'auto';\n        }\n\n        openMenu = {\n            menu: menu,\n            dropdown: $dropdown[0],\n            toggle: $dropdown.find('.dropdown-toggle')[0] || $dropdown[0]\n        };\n\n        positionMenu();\n    }\n\n    $(document).on('shown.bs.dropdown', '.dropdown', function () {\n        openMenuPortal($(this));\n    });\n\n    $(document).on('hidden.bs.dropdown', '.dropdown', function () {\n        if (openMenu && openMenu.dropdown === this) {\n            closeMenu(false);\n        }\n    });\n\n    window.addEventListener('scroll', function () {\n        if (openMenu) {\n            positionMenu();\n        }\n    }, true);\n\n    window.addEventListener('resize', function () {\n        if (openMenu) {\n            positionMenu();\n        }\n    });\n\n    $(document).on('updated', '#ajax-content', function () {\n        closeMenu(true);\n    });\n})(jQuery);\n</script>",
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
