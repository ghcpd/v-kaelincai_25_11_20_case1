from src.transform import baseline_transform

def test_baseline_pass_through():
    inp = {'sections':[{'id':'summary','fields':[{'name':'title','value':'x'}]}]}
    out = baseline_transform(inp)
    assert out['meta']['transformed'] is False
    assert 'sections' in out

def test_malformed_input():
    # missing sections
    inp = {'unknown': 1}
    out = baseline_transform(inp)
    assert out['meta']['transformed'] is False
