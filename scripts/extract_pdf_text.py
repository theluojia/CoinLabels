"""Extract label text by physical cell from the retained Label01.pdf, without website prose."""
import json, re
from pathlib import Path
import pdfplumber

HERE=Path(__file__).resolve().parents[1]
DATA=HERE/'data'
SOURCES=HERE/'sources'

def cells(page):
    boxes={tuple(round(c[k],2) for k in ('x0','top','x1','bottom'))
           for c in page.curves if 130<c['width']<145 and 50<c['height']<75}
    return sorted(boxes,key=lambda b:(round(b[1]),b[0]))

def region_text(page,box):
    x0,y0,x1,y1=box
    region=page.filter(lambda o:o['object_type']=='char' and x0<=(o['x0']+o['x1'])/2<x1 and y0<=(o['top']+o['bottom'])/2<y1)
    return region.extract_text(x_tolerance=1,y_tolerance=2) or ''

def write(name,value):
    (DATA/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
    catalog=json.loads((DATA/'catalog.json').read_text(encoding='utf-8'))
    catalog.sort(key=lambda c:tuple(map(int,re.findall(r'\d+',c['id']))))
    records={}; front_slots=[]
    with pdfplumber.open(SOURCES/'Label01.pdf') as pdf:
        for pi,page in enumerate(pdf.pages):
            page=page.dedupe_chars(tolerance=.5)
            for slot,b in enumerate(cells(page)):
                x,y,x1,y1=b
                full=region_text(page,b)
                if not full.strip(): continue
                source={'file':'Label01.pdf','page':pi+1,'row':slot//4+1,'col':slot%4+1}
                if pi<3:
                    lines=full.splitlines()
                    header=next((t for t in lines if '中华人民共和国普通纪念币' in t),None)
                    footer=next((t for t in lines if re.match(r'^\d{4}\s*[⦁•]',t)),None)
                    if not header or not footer: raise ValueError(('Unrecognized front',source,full))
                    title='\n'.join(t for t in lines if t not in (header,footer))
                    front_slots.append(dict(header=header,title=title,footer=footer,source=source))
                else:
                    badge=region_text(page,(x+98,y,x1,y1))
                    ident=re.search(r'JB0*(\d+)(-\d+)?',badge)
                    if not ident: raise ValueError(('Missing ID',source,badge))
                    ident='JB'+str(int(ident[1])).zfill(2)+(ident[2] or '')
                    seq=re.search(r'[（(](\d+)[）)]',badge)
                    date=re.search(r'\d{4}\.\d{1,2}\.\d{1,2}',badge)
                    upper=region_text(page,(x+29,y,x+99,y+(y1-y)/2))
                    lower=region_text(page,(x+29,y+(y1-y)/2,x+99,y1))
                    records[ident]={'description2':upper.replace('\n',''),'description':lower.replace('\n',''),
                                    'release_date':date[0] if date else '',
                                    'pdf_serial':int(seq[1]) if seq else None,'back_source':source}
    # The reference front pages use serial order; the back badges verify every slot.
    for i,front in enumerate(front_slots):
        ident=catalog[i]['id']
        assert records[ident]['pdf_serial']==i+1,(ident,'PDF serial mismatch')
        records[ident]['front']=front
    write('pdf_text.json',records)
    print('Extracted',len(front_slots),'front labels and',len(records),'back labels')
