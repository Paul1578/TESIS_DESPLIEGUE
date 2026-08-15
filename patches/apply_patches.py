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
        'path': pathlib.Path('/opt/mayan-edms/lib/python3.13/site-packages/mayan/apps/appearance/templates/appearance/app/foot.html'),
        'marker': 'appearance-dropdown-overlay',
        'old': '<script src="{% static \'appearance/js/partial_navigation.js\' %}" type="text/javascript"></script>',
        'new': '<script src="{% static \'appearance/js/partial_navigation.js\' %}" type="text/javascript"></script>\n\n<script>\n(function ($) {\n    \'use strict\';\n\n    var $overlay;\n\n    function ensureOverlay() {\n        if (!$overlay || !$.contains(document, $overlay[0])) {\n            $overlay = $(\'<div id="appearance-dropdown-overlay"></div>\').css({\n                \'position\': \'fixed\',\n                \'left\': \'0\',\n                \'top\': \'0\',\n                \'width\': \'0\',\n                \'height\': \'0\',\n                \'overflow\': \'visible\',\n                \'z-index\': \'2000\'\n            }).appendTo(document.body);\n        }\n        return $overlay;\n    }\n\n    function isPortaled($dropdown) {\n        if ($dropdown.is(\'#multi-item-actions\')) {\n            return true;\n        }\n        return $dropdown.children(\'.dropdown-menu\').hasClass(\'appearance-dropdown-menu-slim\');\n    }\n\n    function portalMenu($dropdown, $menu) {\n        var $overlayEl = ensureOverlay();\n        var menu = $menu[0];\n        var rect = $dropdown[0].getBoundingClientRect();\n        var menuWidth = menu.offsetWidth || 200;\n        var menuHeight = menu.offsetHeight || 100;\n        var winWidth = window.innerWidth || 1024;\n        var winHeight = window.innerHeight || 768;\n        var left = rect.left;\n        if (left + menuWidth > winWidth - 8) {\n            left = Math.max(8, rect.right - menuWidth);\n        }\n        var top = rect.bottom;\n        if (top + menuHeight > winHeight - 8) {\n            top = Math.max(8, rect.top - menuHeight);\n        }\n        $menu.data(\'appearance-dropdown-portal\', $dropdown);\n        $dropdown.data(\'appearance-dropdown-portaled\', true);\n        $menu.detach().appendTo($overlayEl).css({\n            \'position\': \'fixed\',\n            \'left\': left + \'px\',\n            \'top\': top + \'px\',\n            \'width\': menuWidth + \'px\',\n            \'margin\': \'0\',\n            \'z-index\': \'2000\'\n        });\n    }\n\n    function restoreMenu($dropdown) {\n        var $menu = $dropdown.children(\'.dropdown-menu\');\n        if (!$menu.length) {\n            $menu = ensureOverlay().find(\'.dropdown-menu\').filter(function () {\n                return $(this).data(\'appearance-dropdown-portal\') && $(this).data(\'appearance-dropdown-portal\')[0] === $dropdown[0];\n            }).first();\n        }\n        $dropdown.removeData(\'appearance-dropdown-portaled\');\n        if (!$menu.length) {\n            return;\n        }\n        var $parent = $menu.data(\'appearance-dropdown-portal\');\n        $menu.removeData(\'appearance-dropdown-portal\');\n        if ($parent && $parent.length && $.contains(document, $parent[0])) {\n            $menu.appendTo($parent).removeAttr(\'style\');\n        } else {\n            $menu.remove();\n        }\n    }\n\n    function afterShown(fn) {\n        if (typeof queueMicrotask === \'function\') {\n            queueMicrotask(fn);\n        } else {\n            window.setTimeout(fn, 0);\n        }\n    }\n\n    $(document).on(\'shown.bs.dropdown\', function (event) {\n        var $toggle = $(event.target);\n        var $dropdown = $toggle.parent(\'.dropdown, #multi-item-actions\').first();\n        if (!$dropdown.length) {\n            return;\n        }\n        if (!isPortaled($dropdown)) {\n            return;\n        }\n        afterShown(function () {\n            var $menu = $dropdown.children(\'.dropdown-menu\');\n            if (!$dropdown.hasClass(\'open\') || !$menu.length) {\n                return;\n            }\n            portalMenu($dropdown, $menu);\n        });\n    });\n\n    $(document).on(\'hidden.bs.dropdown\', function (event) {\n        var $toggle = $(event.target);\n        var $dropdown = $toggle.parent(\'.dropdown, #multi-item-actions\').first();\n        if (!$dropdown.length) {\n            return;\n        }\n        if (!$dropdown.data(\'appearance-dropdown-portaled\')) {\n            return;\n        }\n        restoreMenu($dropdown);\n    });\n\n    $(document).on(\'updated\', \'#ajax-content\', function () {\n        if ($overlay && $.contains(document, $overlay[0])) {\n            $overlay.children(\'.dropdown-menu\').remove();\n        }\n    });\n})(jQuery);\n</script>',
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