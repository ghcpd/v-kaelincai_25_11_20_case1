from src.transform import enhance_transform

def test_core_prioritization_and_collapsing():
    inp = {'sections':[{'id':'summary','fields':[{'name':'problem_description','value':'p'},{'name':'priority','value':'high'}]}, {'id':'history','fields':[{'name':'h1'},{'name':'h2'}]}]}
    out = enhance_transform(inp)
    assert out['meta']['transformed'] is True
    assert out['sections'][0]['id'] == 'core'
    assert out['sections'][0]['fields'][0]['name'] == 'problem_description'
    assert out['sections'][0]['fields'][1].get('highlight', False) is True
    # history collapsed
    for s in out['sections']:
        if s['id']=='history':
            assert s['collapsed'] is True

def test_attachment_preview_mode():
    inp = {'sections':[]}
    out = enhance_transform(inp)
    assert out['attachment_preview']['mode'] == 'side_panel'
