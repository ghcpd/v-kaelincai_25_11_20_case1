"""
Enhanced transformer implementing UI/UX improvements for Ticket Detail Page.
- Reorders core info to top
- Collapses heavy sections (history, logs, related_tickets)
- Differentiates internal notes vs customer-visible replies
- Converts attachment handling to non-blocking previews
- Adds confirmation flags for critical interactions
- Safely deactivates unsafe HTML
- Handles malformed and deeply nested structures

Output format includes 'ui', 'metrics', 'warnings', 'errors'
"""
from typing import Any, Dict, List
import copy

CORE_KEYS = ['problem_description','description','priority','status','title','core']


class TransformError(Exception):
    pass


def is_string(x):
    return isinstance(x, str)


def safe_strip_html(text: str) -> str:
    # very lightweight sanitizer: remove <script> tags
    import re
    if not is_string(text):
        return text
    sanitized = re.sub(r'<script.*?>.*?</script>', '[removed script]', text, flags=re.I|re.S)
    # encode angle brackets to avoid HTML injection in outputs
    sanitized = sanitized.replace('<', '&lt;').replace('>', '&gt;')
    return sanitized


def promote_core(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Look for core blocks and move them to top (stable order)
    core_blocks = []
    others = []
    for b in blocks:
        name = b.get('name','').lower() if isinstance(b.get('name',''), str) else ''
        keys_in_block = [k.lower() for k in b.keys()]
        if any(k in name for k in CORE_KEYS) or any(any(c in k for c in CORE_KEYS) for k in keys_in_block):
            core_blocks.append(b)
        else:
            others.append(b)
    return core_blocks + others


def collapse_heavy_sections(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Collapse sections that are heavy by default
    heavy_names = ['history','logs','activity','timeline','related']
    out = []
    for b in blocks:
        name = b.get('name','').lower() if isinstance(b.get('name',''), str) else ''
        if any(h in name for h in heavy_names):
            b.setdefault('collapsed', True)
            # For very large lists, keep only a short preview
            items = b.get('items')
            if isinstance(items, list) and len(items) > 5:
                b['_preview'] = items[:3]
                b['_hidden_count'] = len(items) - 3
            out.append(b)
        else:
            out.append(b)
    return out


def differentiate_notes(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for b in blocks:
        if b.get('type') == 'note' or 'note' in b.get('name','').lower():
            # classify by visibility
            vis = b.get('visibility','')
            if vis == 'internal' or 'internal' in b.get('tags',[]):
                b['_display'] = 'internal'
                b['_style'] = {'background':'#fff7e6','label':'Internal note'}
            else:
                b['_display'] = 'customer'
                b['_style'] = {'background':'#f0f9ff','label':'Customer-visible reply'}
    return blocks


def convert_attachments(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for b in blocks:
        if b.get('type') == 'attachment' or 'attachment' in b.get('name','').lower():
            # convert to non-blocking preview metadata
            b['_attachment_mode'] = 'side-panel'
            b['_preview_inline'] = True
            # ensure attachment safe content
            items = b.get('items', [])
            safe_items = []
            for it in items:
                if isinstance(it, dict):
                    it_s = copy.deepcopy(it)
                    it_s['filename'] = str(it_s.get('filename',''))
                    it_s['preview'] = it_s.get('preview', '')  # could be url
                    safe_items.append(it_s)
            b['items'] = safe_items
    return blocks


def detect_malformed(blocks: List[Any]) -> List[str]:
    errors = []
    def check(obj, path='root'):
        if isinstance(obj, dict):
            # detect suspicious structures
            for k,v in obj.items():
                if k == '' or k is None:
                    errors.append(f"Empty key at {path}")
                if isinstance(v, dict) and len(v) == 0:
                    errors.append(f"Empty dict at {path}.{k}")
                if isinstance(v, list) and any(not isinstance(i, (dict,str,int,float,list)) for i in v):
                    errors.append(f"Mixed-type list at {path}.{k}")
                check(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check(item, f"{path}[{i}]")

    check(blocks)
    return errors


def transform_layout(layout: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(layout, dict):
        raise TransformError('Input must be a dict')

    out = {'ui': {}, 'metrics': {}, 'warnings': [], 'errors': []}
    src = copy.deepcopy(layout)

    # sanitize any top-level titles/fields
    for k,v in list(src.items()):
        if isinstance(v, str):
            src[k] = safe_strip_html(v)

    # extract layout blocks: support various formats
    blocks = []
    if 'sections' in src and isinstance(src['sections'], list):
        blocks = src['sections']
    elif 'layout' in src and isinstance(src['layout'], list):
        blocks = src['layout']
    else:
        # if a dict with keys, convert to list of blocks
        blocks = []
        for k,v in src.items():
            if k.startswith('_'): continue
            blocks.append({'name': k, 'content': v})

    # flatten and normalize blocks
    norm_blocks = []
    def normalize_block(b):
        if not isinstance(b, dict):
            return {'name': 'unknown', 'content': b}
        b2 = copy.deepcopy(b)
        # make sure name exists
        if 'name' not in b2:
            # try to extract from type
            b2['name'] = b2.get('type', 'section')
        # sanitize text fields
        for key, val in list(b2.items()):
            if isinstance(val, str):
                b2[key] = safe_strip_html(val)
        return b2

    for b in blocks:
        norm_blocks.append(normalize_block(b))

    # detect malformed
    out['errors'] += detect_malformed(norm_blocks)

    # apply improvements
    promoted = promote_core(norm_blocks)
    collapsed = collapse_heavy_sections(promoted)
    differentiated = differentiate_notes(collapsed)
    attachments = convert_attachments(differentiated)

    # ensure confirmation prompts for critical actions (status change, delete)
    for b in attachments:
        if b.get('name','').lower() in ('actions','controls') or b.get('type')=='actions':
            for action in b.get('items', []):
                if action.get('critical'):
                    action.setdefault('requires_confirmation', True)

    # construct ui view
    out['ui']['sections'] = attachments

    # compute metrics
    # hierarchy clarity: core blocks at top yield higher score
    out['metrics']['hierarchy_clarity'] = 0.0
    if len(attachments) > 0:
        names = [s.get('name','') for s in attachments]
        top = names[0].lower() if names[0] else ''
        if any(k in top for k in CORE_KEYS):
            out['metrics']['hierarchy_clarity'] = 1.0
        else:
            # if core anywhere earlier than position 3
            pos = next((i for i,n in enumerate(names) if any(k in (n or '').lower() for k in CORE_KEYS)), None)
            if pos is None:
                out['metrics']['hierarchy_clarity'] = 0.2
            else:
                out['metrics']['hierarchy_clarity'] = max(0.3, 1.0 - pos*0.2)

    # collapsibility coverage
    collapsed_count = sum(1 for s in attachments if s.get('collapsed'))
    out['metrics']['collapsed_sections'] = collapsed_count
    out['metrics']['total_sections'] = len(attachments)

    # mis-operation risk: if internal notes and customer replies not differentiated, risk high
    has_internal = any(s.get('_display') == 'internal' for s in attachments)
    has_customer = any(s.get('_display') == 'customer' for s in attachments)
    out['metrics']['misoperation_risk'] = 0.9 if not (has_internal and has_customer) else 0.2

    # attachment preview mode present?
    out['metrics']['has_non_blocking_attachments'] = any(s.get('_attachment_mode') is not None for s in attachments)

    # warnings for unsafe fields
    # any sanitized HTML found?
    # (The safe_strip_html replaced scripts with [removed script])
    import json
    def find_removed(obj, path='root'):
        if isinstance(obj, dict):
            for k,v in obj.items():
                if isinstance(v, str) and '[removed script]' in v:
                    out['warnings'].append(f'script removed at {path}.{k}')
                find_removed(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, it in enumerate(obj):
                find_removed(it, f"{path}[{i}]")

    find_removed(src)

    return out


# helper for tests

def compute_hierarchy_score(transformed: Dict[str, Any]) -> float:
    return transformed.get('metrics', {}).get('hierarchy_clarity', 0.0)
