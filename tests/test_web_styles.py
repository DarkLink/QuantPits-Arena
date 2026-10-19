"""Guard shared presentation dependencies used by the browser views."""
import re

from arena.config import REPO_ROOT


def test_css_variables_resolve_or_provide_a_fallback():
    css_files = sorted((REPO_ROOT / 'web/css').glob('*.css'))
    sources = css_files + sorted((REPO_ROOT / 'web/js/views').glob('*.js'))
    sources += sorted((REPO_ROOT / 'web/js/components').glob('*.js'))
    definitions = set(re.findall(
        r'(--[\w-]+)\s*:', '\n'.join(path.read_text() for path in css_files)
    ))
    missing = []
    for path in sources:
        for variable, remainder in re.findall(r'var\((--[\w-]+)([^)]*)\)', path.read_text()):
            if variable not in definitions and ',' not in remainder:
                missing.append((str(path.relative_to(REPO_ROOT)), variable))
    assert not missing, missing


def test_shared_view_components_have_styles():
    css = '\n'.join(path.read_text() for path in (REPO_ROOT / 'web/css').glob('*.css'))
    sources = '\n'.join(path.read_text() for path in (REPO_ROOT / 'web/js/views').glob('*.js'))
    variants = set(re.findall(r'\b(?:badge-[a-z]+|btn-outline|btn-sm)\b', sources))
    variants.update({
        'chart-card', 'chart-card-header', 'chart-card-title', 'form-control',
        'table-responsive', 'table', 'text-up', 'text-down', 'kpi-title', 'prose',
    })
    for name in sorted(variants):
        assert re.search(r'\.' + re.escape(name) + r'(?![\w-])', css), name
