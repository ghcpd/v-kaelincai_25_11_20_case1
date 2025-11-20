import json
import time
from pathlib import Path

# Import both services
from Project_A_BaselineReportService.src.service import BaselineReportService
from Project_B_EnhancedReportService.src.service import EnhancedReportService
from Project_A_BaselineTicketUI.src.transform import baseline_transform
from Project_B_EnhancedTicketUI.src.transform import enhance_transform

OUTDIR = Path('results')
OUTDIR.mkdir(exist_ok=True)

with open('shared/test_scenarios.json') as f:
    scenarios = json.load(f)

baseline = BaselineReportService()
enhanced = EnhancedReportService()

report_results_pre = []
report_results_post = []

for s in scenarios['report_scenarios']:
    r = {"id": s['id']}
    st = time.time()
    try:
        if s['id']=='malformed_input':
            res = baseline.get_report(None)
            r['error'] = True
            r['status'] = 'fail'
        else:
            res = baseline.get_report('2025-11-19')
            r['status'] = 'ok'
            r['metrics'] = res.get('metrics')
            r['latency'] = time.time()-st
    except Exception as e:
        r['status'] = 'error'
        r['error'] = str(e)
    report_results_pre.append(r)

# enhanced
for s in scenarios['report_scenarios']:
    r = {"id": s['id']}
    st = time.time()
    try:
        if s['id']=='malformed_input':
            res = enhanced.get_report(None)
            r['status'] = 'error'
        else:
            res = enhanced.get_report('2025-11-19', dimensions='region', peak=s['initial_state'].get('peak', False))
            r['status'] = 'ok'
            r['latency'] = time.time()-st
            r['pre_agg'] = res['core']['pre_agg']
            r['in_progress'] = res.get('in_progress')
    except Exception as e:
        r['status'] = 'circuit' if 'CircuitBreaker' in str(e) else 'error'
        r['error'] = str(e)
    report_results_post.append(r)

with open(OUTDIR/'results_pre.json','w') as f:
    json.dump(report_results_pre,f,indent=2)
with open(OUTDIR/'results_post.json','w') as f:
    json.dump(report_results_post,f,indent=2)

# Ticket UI
ui_results_pre=[]
ui_results_post=[]
for s in scenarios['ticket_scenarios']:
    r_pre={'id':s['id']}
    try:
        out = baseline_transform(s.get('input',{}))
        r_pre['ui_warnings'] = []
        r_pre['status']='ok'
    except Exception as e:
        r_pre['status']='error'
        r_pre['errors']=str(e)
    ui_results_pre.append(r_pre)

    r_post={'id':s['id']}
    try:
        out = enhance_transform(s.get('input',{}))
        r_post['status']='ok'
        # check expectations
        r_post['core_on_top'] = (out['sections'][0]['id']=='core') if out.get('sections') else False
        r_post['history_collapsed'] = any((ss.get('id')=='history' and ss.get('collapsed')) for ss in out.get('sections',[]))
    except Exception as e:
        r_post['status']='error'
        r_post['errors']=str(e)
    ui_results_post.append(r_post)

with open(OUTDIR/'ui_results_pre.json','w') as f:
    json.dump(ui_results_pre,f,indent=2)
with open(OUTDIR/'ui_results_post.json','w') as f:
    json.dump(ui_results_post,f,indent=2)

# aggregate stats
summary = {
    'report_total': len(report_results_pre),
    'report_passed_pre': sum(1 for r in report_results_pre if r.get('status')=='ok'),
    'report_passed_post': sum(1 for r in report_results_post if r.get('status')=='ok'),
    'ui_total': len(ui_results_pre),
    'ui_passed_pre': sum(1 for r in ui_results_pre if r.get('status')=='ok'),
    'ui_passed_post': sum(1 for r in ui_results_post if r.get('status')=='ok')
}
with open(OUTDIR/'summary.json','w') as f:
    json.dump(summary,f,indent=2)

print('Done. Results written to results folder')
