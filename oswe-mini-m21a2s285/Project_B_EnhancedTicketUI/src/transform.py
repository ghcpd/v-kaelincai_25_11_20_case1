import copy

def enhance_transform(layout):
    out = copy.deepcopy(layout)
    # Ensure core information order
    core_keys = ['problem_description', 'priority', 'status']
    out['sections'] = out.get('sections', [])
    # Move or create core block at front
    core_block = {'id': 'core', 'title': 'Core Info', 'fields': []}
    others = []
    for s in out['sections']:
        if s.get('id') in ['core', 'summary']:
            core_block['fields'].extend(s.get('fields', []))
        else:
            others.append(s)
    # highlight priority
    for f in core_block['fields']:
        if f.get('name') == 'priority':
            f['highlight'] = True
    # Place core at top
    out['sections'] = [core_block] + others
    # Collapse long history sections
    for s in out['sections']:
        if s.get('id') == 'history':
            s['collapsed'] = True
            s['max_preview'] = 5
    # Attachment preview config
    out['attachment_preview'] = {'mode': 'side_panel'}
    out.setdefault('meta', {})
    out['meta']['transformed'] = True
    return out

if __name__ == '__main__':
    sample = {'sections':[{'id':'summary','fields':[{'name':'problem_description','value':'...'}]}, {'id':'history','fields':[{'name':'h1'}]}]}
    print(enhance_transform(sample))
