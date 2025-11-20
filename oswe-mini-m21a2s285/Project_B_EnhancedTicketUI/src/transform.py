"""
Enhanced transformation - reorganize layout, add collapsible sections, highlight core info, secure HTML, non-blocking previews, and mis-operation prevention.
"""
import copy
import re


SAFE_SIMPLE_TAGS = ['b','i','u','em','strong','p','br']


def strip_unsafe_html(text):
    if not isinstance(text, str):
        return text
    # remove script/style tags and attributes
    text = re.sub(r'<\s*script[^>]*>.*?<\s*/\s*script\s*>', '', text, flags=re.S|re.I)
    text = re.sub(r'<\s*style[^>]*>.*?<\s*/\s*style\s*>', '', text, flags=re.S|re.I)
    # escape angle brackets for remaining tags
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    return text


def is_deeply_nested(node, depth=0):
    if depth > 5:
        return True
    if isinstance(node, dict):
        return any(is_deeply_nested(v, depth+1) for v in node.values())
    if isinstance(node, list):
        return any(is_deeply_nested(v, depth+1) for v in node)
    return False


def enhance_transform(layout):
    out = copy.deepcopy(layout) if isinstance(layout, dict) else {}
    metrics = {}
    ui_warnings = []

    # safe fallback on malformed input
    if not isinstance(layout, dict):
        ui_warnings.append('malformed_layout')
        out = {'core': {'description': 'Invalid layout', 'priority': 'Normal', 'status': 'Open'}}

    # Ensure core exists and highlight
    core = out.get('core', {})
    if not isinstance(core, dict):
        ui_warnings.append('core_type_error')
        core = {'description': str(core) if core else 'Missing description'}
    core.setdefault('description', 'No description provided')
    core.setdefault('priority', 'Normal')
    core.setdefault('status', 'Open')
    core['highlight'] = True
    out['core'] = core

    # Reorder: put core first
    new_layout = {'core': core}

    # Move other known sections next (attachments, fields, notes)
    for key in ['attachments', 'fields', 'notes', 'history', 'logs', 'related']:
        if key in out:
            new_layout[key] = out[key]

    # add a fallback for any remaining keys
    for key, val in out.items():
        if key not in new_layout:
            new_layout[key] = val

    # Collapsible behavior: default collapsed for history/logs/related
    for sec in ['history', 'logs', 'related']:
        if sec in new_layout:
            secval = new_layout[sec]
            if isinstance(secval, dict):
                secval.setdefault('collapsed', True)
                # reduce scrolling: limit visible entries
                if 'entries' in secval and isinstance(secval['entries'], list):
                    secval['visible_preview_count'] = min(3, len(secval['entries']))
                    # Store a short preview for UI
                    secval['preview'] = secval['entries'][:secval['visible_preview_count']]
            new_layout[sec] = secval

    # Attachment preview optimization
    if 'attachments' in new_layout and isinstance(new_layout['attachments'], dict):
        new_layout['attachments'].setdefault('preview_mode', 'side-panel')
        new_layout['attachments'].setdefault('non_blocking', True)

    # distinct internal vs external notes
    if 'notes' in new_layout and isinstance(new_layout['notes'], dict):
        n = new_layout['notes']
        if 'items' in n and isinstance(n['items'], list):
            for item in n['items']:
                if item.get('internal'):
                    item.setdefault('style', 'muted')
                    item.setdefault('confirm_on_edit', True)
                else:
                    item.setdefault('style', 'normal')

    # sanitize unsafe HTML and deep nesting detection
    if 'core' in new_layout and isinstance(new_layout['core'], dict):
        new_layout['core']['description'] = strip_unsafe_html(new_layout['core'].get('description', ''))

    # metrics and scores
    metrics['core_on_top'] = True
    metrics['clarity_score'] = 0.0
    # basic heuristic clarity: higher if core highlight and side-panel attachments
    clarity = 0
    if new_layout['core'].get('highlight'):
        clarity += 40
    if 'attachments' in new_layout and new_layout['attachments'].get('non_blocking'):
        clarity += 20
    # collapsed sections add to clarity
    collapsed = [sec for sec in ['history','logs','related'] if sec in new_layout and new_layout[sec].get('collapsed')]
    clarity += len(collapsed) * 10

    if is_deeply_nested(layout):
        ui_warnings.append('deeply_nested')
        # mark groups collapsed aggressively
        for sec in ['history','logs']:
            if sec in new_layout and isinstance(new_layout[sec], dict):
                new_layout[sec]['collapsed'] = True
    metrics['clarity_score'] = clarity

    # mis-operation prevention: set confirmation for critical actions
    new_layout.setdefault('actions', {})
    new_layout['actions'].setdefault('close_ticket', {'confirm': True, 'severity': 'critical'})
    new_layout['actions'].setdefault('delete_attachment', {'confirm': True, 'severity': 'high'})

    out = new_layout
    status = 'ok' if not ui_warnings else 'warning'
    return {'layout': out, 'metrics': metrics, 'ui_warnings': ui_warnings, 'status': status}


if __name__ == '__main__':
    import json, sys
    data = {}
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            data = json.load(f)
    print(json.dumps(enhance_transform(data), indent=2))
