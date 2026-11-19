"""Run one worker lane. Every child stays within its own timeout and the wall budget."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import subprocess
from time import monotonic

from search import log


HERE = Path.cwd()
OUT = Path('results')
PYTHON = 'venv/bin/python'
STRUCTURED = [
    'n36-circle','n37-circle','n37-b2','g36-c9-c4-invert','g36-c9-v4-trivial',
    'g36-v9-c4-trivial','g36-v9-c4-reflect','g36-v9-c4-invert',
    'g36-v9-c4-rotate','g36-v9-v4-trivial','g36-v9-v4-trivial-reflect',
    'g36-v4-c9','g36-v4-v9','g36-v9-v4-two-chars',
    'g36-c9-v4-invert','g36-v9-v4-trivial-invert',
]
BLOCKS = ['n36-b2','n36-b3','n36-b4','n36-b6','n37-b3','n37-b4','n37-b6']


def launch(deadline, name, argv, limit):
    seconds = min(limit, (deadline - datetime.now(timezone.utc)).total_seconds())
    if seconds < 1:
        return False
    start = monotonic()
    logfile = OUT / (name+'.log')
    with logfile.open('x') as output:
        child = subprocess.Popen(argv, stdout=output, stderr=subprocess.STDOUT)
        log(job=name, event='start', pid=child.pid, seconds_limit=round(seconds, 2), argv=argv)
        try:
            status = child.wait(timeout=seconds)
        except subprocess.TimeoutExpired:
            child.terminate()
            try:
                status = child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                status = child.wait()
        except BaseException:
            child.terminate()
            child.wait()
            raise
    log(job=name, event='end', status=status, seconds=round(monotonic()-start, 3))
    return True


def result(path):
    with path.open() as file:
        records = [line.split() for line in file if ' best ' in line]
    if not records:
        return float('inf')
    return min(sum(int(field.split('=')[1]) for field in rec if field.startswith(('zero=','one=')))
               for rec in records)


def structured(deadline):
    # Establish a candidate for each large family before expensive exhaustive enumerations.
    for i, family in enumerate(BLOCKS):
        n = int(family[1:3])
        launch(deadline,family+'-anneal', [
            './ramsey','anneal',str(n),'4','6',str(46000+i),'2400000','5','1','0','-',
            str(OUT/(family+'-anneal')),family+'.orbits'
        ], 150)
    launch(deadline,'orbit-sat', [PYTHON,'orbits.py','sat','--names',*STRUCTURED,*BLOCKS,
                                '--conflicts','500000'], 920)
    for family in STRUCTURED:
        n = 37 if family.startswith('n37') else 36
        launch(deadline,family+'-enum', ['./ramsey','enumerate',str(n),'4','6',family+'.orbits',
                                        str(OUT/(family+'-enum'))], 1200)
    # Prioritise structure deviations that still start fairly close to a strict block.
    for repeat, weight in enumerate((0.6,1.6,1.0)):
        for i, family in enumerate(BLOCKS):
            n = int(family[1:3])
            label = f'{family}-reheat-{repeat}'
            launch(deadline,label, [
                './ramsey','anneal',str(n),'4','6',str(46900+10*repeat+i),'2500000','6',str(weight),'0',
                str(OUT/(family+'-anneal.json')),str(OUT/label),family+'.orbits'
            ], 210)


def unrestricted(deadline):
    starts = [('exoo-extension','best-single-extension.json'),('random','-')]
    for round_no in range(25):
        symmetry = []
        for label in STRUCTURED+BLOCKS:
            if label.startswith('n37'):
                continue
            for suffix in ('enum','anneal'):
                path = OUT / f'{label}-{suffix}.json'
                if path.exists():
                    symmetry.append((result(path.with_suffix('.log')),label,str(path)))
        # Alternate the best current symmetric input with other families.
        symmetry.sort()
        if symmetry:
            _, name, path = symmetry[0 if round_no % 2 == 0 else (round_no//2)%len(symmetry)]
            current_starts = starts+[('structured-'+name,path)]
        else:
            current_starts = starts
        for i, (source,path) in enumerate(current_starts):
            modes = [('raw',1.0,0),('light-k6',0.55,0),('heavy-k6',1.7,0),('p4',1.0,0.035)]
            mode, weight, p4 = modes[round_no%len(modes)]
            steps, restarts = (1_500_000,6) if p4 else (3_000_000,8)
            label = f'local-{source}-{mode}-{round_no:02}'
            if not launch(deadline,label, [
                './ramsey','anneal','36','4','6',str(4636000+10*round_no+i),
                str(steps),str(restarts),str(weight),str(p4),path,str(OUT/label)
            ], 300):
                return
            output = OUT/(label+'.log')
            if result(output)==0:
                return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lane', choices=('structured','unrestricted'))
    parser.add_argument('deadline', type=datetime.fromisoformat)
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    log(lane=args.lane,event='start',deadline=args.deadline.isoformat(),cwd=HERE.name)
    action = structured if args.lane == 'structured' else unrestricted
    action(args.deadline)
    log(lane=args.lane,event='end')
