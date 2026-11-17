"""Add published starts, prove selected extension negatives, and try SAT-guided repairs."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import subprocess

from campaign import OUT, PYTHON, launch, result
from search import as_rows, counts, edges, log, save


def check_candidate(path):
    root = Path.cwd().parents[2]
    completed = subprocess.run(
        ['bun','frontier','diagnose',str(path.resolve()),'--problem','witness.ramsey-4-6','--json'],
        cwd=root,capture_output=True,text=True,check=True,
    )
    print(completed.stdout,flush=True)


def extension_seed(input_path, prefix):
    core = as_rows(input_path)
    m = len(core)
    rows = [r+[0] for r in core]+[[0]*(m+1)]
    write_variables = [i if j==m else -1 for i,j in edges(m+1)]
    # This move table does not represent graph symmetry. The vertex list is unused by anneal.
    Path(prefix+'.orbits').write_text(
        f'{m} 1\n0 {m+1}\n'+' '.join(map(str,write_variables))+'\n')
    save(prefix+'.json',rows)


def graph_score(path):
    return sum(counts(as_rows(path),4,6))


def catalogue(deadline):
    launch(deadline,'catalogue-extension', ['env','PYTHONSAFEPATH=1',PYTHON,'-I','-c',
        'import runpy,sys; sys.path.insert(0,"."); sys.argv=["neighborhoods.py","catalogue","input-mckay/r46_35some.g6"]; runpy.run_path("neighborhoods.py",run_name="__main__")'], 180)
    for path in sorted(Path('.').glob('catalogue-input-*.json')):
        number = int(path.stem.split('-')[-1])
        label = f'catalogue-seed-{number:02}'
        prefix = str(OUT/label)
        extension_seed(path,prefix)
        if not launch(deadline,label,[
            './ramsey','anneal','36','4','6',str(4637000+number),
            '240000','20','1','0',prefix+'.json',prefix+'-best',prefix+'.orbits'
        ], 40):
            break
        if graph_score(Path(prefix+'-best.json'))==0:
            check_candidate(Path(prefix+'-best.json'))
            return


def refine(deadline):
    paths = [Path('best-single-extension.json')]
    paths += sorted(OUT.glob('catalogue-seed-*-best.json'))
    paths += sorted(OUT.glob('local-*.json'))
    paths += sorted(OUT.glob('n36-*-anneal.json'))
    paths += sorted(OUT.glob('n36-*-enum.json'))
    paths += sorted(OUT.glob('g36-*-enum.json'))
    paths += sorted(OUT.glob('aut-*.json'))
    ranked = sorted((graph_score(path),str(path)) for path in paths)
    tried = set()
    inputs = []
    for total, path in ranked:
        # Pick a small range of genuinely different labelled starts.
        data = tuple(tuple(row) for row in as_rows(path))
        if data in tried:
            continue
        tried.add(data)
        inputs.append((total,path))
        if len(inputs)==12:
            break
    for n,sizes in [(17,(4,4)),(24,(4,5))]:
        label = f'guided-control-{n}'
        launch(deadline,label,['./ramsey','anneal',str(n),*map(str,sizes),str(900+n),
            '380000','28','1','0','-',str(OUT/label),'-','2.9','0.12','0.50','0.35'],90)
        if result(OUT/(label+'.log'))!=0:
            raise RuntimeError('paired conflict search failed calibration')
    for i,(total,path) in enumerate(inputs):
        for j,(high,weight,bias,focus,pair) in enumerate([
            (0.45,1.0,0,0,0),(0.8,1.3,0,0.5,0.35),(1.15,1.0,0.04,0.5,0.4),
            (0.65,0.75,0.025,0.65,0.25)
        ]):
            label = f'refine-{i:02}-{j}'
            log(case=label,initial_cliques=total,path=path)
            steps = 400000 if bias else 2200000
            if not launch(deadline,label,[
                './ramsey','anneal','36','4','6',str(4638000+10*i+j),str(steps),'14',
                str(weight),str(bias),path,str(OUT/label),'-',str(high),'0.055',str(focus),str(pair)
            ], 150):
                return
            if result(OUT/(label+'.log'))==0:
                check_candidate(OUT/(label+'.json'))
                return


def exact_neighbors(deadline):
    launch(deadline,'raw-sat-negative-controls',[PYTHON,'-I','search.py','raw-negative-controls'],90)
    launch(deadline,'proof-controls',[PYTHON,'neighborhoods.py','proof-controls'],90)
    launch(deadline,'sat-repair-controls',[PYTHON,'neighborhoods.py','repair-controls'],90)
    if not (Path('repair-control-17.json').exists() and Path('repair-control-24.json').exists()
            and Path('repair-control-35.json').exists()):
        raise RuntimeError('repair was not calibrated')
    candidates = sorted((*OUT.glob('local-*.json'),*OUT.glob('refine-*.json'),*OUT.glob('catalogue-seed-*-best.json')))
    ranked = sorted((graph_score(path),str(path)) for path in candidates)
    chosen = []
    seen = set()
    for _,path in ranked:
        rows = tuple(tuple(row) for row in as_rows(path))
        if rows not in seen:
            chosen.append(path)
            seen.add(rows)
        if len(chosen)==6:
            break
    for i,path in enumerate(chosen):
        extra = (0,16,32)[i%3]
        label = f'near-{i}'
        if not launch(deadline,label,[PYTHON,'neighborhoods.py','repair',deadline.isoformat(),
                    path,label,'--seed',str(462000+i),'--limit','140','--conflicts','10000','--extra',str(extra)], 180):
            return
        candidates = sorted(Path('.').glob(label+'-repair-*.json'))
        if candidates:
            check_candidate(candidates[0])
            return
    launch(deadline,'delete-three',[PYTHON,'neighborhoods.py','delete',deadline.isoformat(),
        'baseline.json','base','--seed','466633','--limit','6545','--conflicts','30000','--remove','3'],1500)
    for path in sorted(Path('.').glob('base-ext4-*.json')):
        check_candidate(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('catalogue','refine','exact-neighbors'))
    parser.add_argument('deadline',type=datetime.fromisoformat)
    args = parser.parse_args()
    log(action=args.action,event='start',deadline=args.deadline.isoformat())
    actions = {'catalogue':catalogue, 'refine':refine, 'exact-neighbors':exact_neighbors}
    actions[args.action](args.deadline)
    log(action=args.action,event='end')
