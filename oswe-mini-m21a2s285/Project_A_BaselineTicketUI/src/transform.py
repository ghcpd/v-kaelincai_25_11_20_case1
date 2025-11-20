import copy

def baseline_transform(layout):
    # naive pass-through
    out = copy.deepcopy(layout)
    out.setdefault('meta', {})
    out['meta']['transformed'] = False
    return out

if __name__ == '__main__':
    print(baseline_transform({'title':'Ticket'}))
