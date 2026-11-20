"""Refresh a portable label catalog and coin images from a myCoins checkout."""
import argparse,json,re,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
def order(c): return tuple(map(int,re.findall(r'\d+',c['id'])))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--source',type=Path,default=HERE.parent / "myCoins"); a=p.parse_args()
    source=json.loads((a.source/'coin_data.json').read_text(encoding='utf-8'))
    coins=sorted(({'id':c['id'],'theme':c['theme'],'diameter_mm':float(c['size'].lower().replace('mm',''))} for c in source if c['id'].startswith('JB')),key=order)
    (HERE/'coins').mkdir(exist_ok=True)
    for i,c in enumerate(coins,1):
        c['serial']=i
        for face in ('f','b'):
            name=f"{c['id']}_{face}.webp"
            shutil.copy2(a.source/'coins'/'img'/name,HERE/'coins'/name)
    (HERE/'data'/'catalog.json').write_text(json.dumps(coins,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Imported',len(coins),'coins, last',coins[-1]['id'])
