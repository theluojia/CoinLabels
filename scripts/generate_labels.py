"""Generate all 8252 front and 8240 back labels without changing template geometry."""
from pathlib import Path
import json, os, re, argparse
from copy import deepcopy
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from docx import Document
from docx.shared import Emu, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
LABEL=Path(__file__).resolve().parents[1]
BG=LABEL/'backgrounds'
DATA=LABEL/'data'
SOURCES=LABEL/'sources'
FONTS=Path(os.environ.get('LABEL_FONT_DIR','C:/Windows/Fonts' if os.name=='nt' else '/mnt/c/Windows/Fonts'))
CATALOG=json.loads((DATA/'catalog.json').read_text(encoding='utf-8'))
CATALOG.sort(key=lambda c:tuple(map(int,re.findall(r'\d+',c['id']))))
PDF_TEXT=json.loads((DATA/'pdf_text.json').read_text(encoding='utf-8'))
OVERRIDES=json.loads((DATA/'overrides.json').read_text(encoding='utf-8'))
for c in CATALOG:
    c.update(PDF_TEXT.get(c['id'],{}))
    c.update(OVERRIDES.get(c['id'],{}))
    c.setdefault('description','')
    c.setdefault('description2','')
    c.setdefault('front',{})
    c['display_id']=re.sub(r'^JB(\d+)',lambda m:'JB'+m[1].zfill(3),c['id'])
    c['serial']=c.get('pdf_serial') or c['serial']
IDS=[c['id'] for c in CATALOG]
COINS={c['id']:c for c in CATALOG}
DPI=600
SERIES_COLORS=json.loads((DATA/'series_colors.json').read_text(encoding='utf-8'))
SERIAL={c['id']:str(c['serial']).zfill(3) for c in CATALOG}
DATES={c['id']:c['release_date'] for c in CATALOG if c.get('release_date')}
REPORT=[]
def series_key(c):
    if c['theme']=='京剧艺术': return 'opera'
    if c['theme']=='国家公园': return 'park'
    return c['theme']
def series_color(c):
    return SERIES_COLORS.get(c['id'], SERIES_COLORS.get(c['theme'], '#305153'))
def font(px,bold=False):
    custom=os.environ.get('LABEL_FONT_BOLD' if bold else 'LABEL_FONT_REGULAR')
    path=Path(custom) if custom else FONTS/('msyhbd.ttc' if bold else 'msyh.ttc')
    if not path.exists():
        path=Path('/usr/share/fonts/opentype/noto/'+('NotoSansCJK-Bold.ttc' if bold else 'NotoSansCJK-Regular.ttc'))
    if not path.exists(): raise RuntimeError('Chinese font missing: set LABEL_FONT_REGULAR and LABEL_FONT_BOLD; see README.md')
    return ImageFont.truetype(str(path),round(px))
def wrapped(text,f,width):
    lines=[]
    for para in text.split('\n'):
        line=''
        for ch in re.findall(r'\d+(?:\.\d+)?(?:周年|年|毫米|mm|元|万)?|[A-Za-z]+|.',para):
            if line and f.getlength(line+ch)>width: lines.append(line); line=''
            line+=ch
        lines.append(line)
    return lines
def textblock(im,text,box,size,minsize=25,bold=False,center=False,color='#233f40',vcenter=False,maxlines=None,wash_opacity=0):
    d=ImageDraw.Draw(im); x,y,w,h=box
    for px in range(round(size),minsize-1,-1):
        f=font(px,bold); lines=wrapped(text,f,w); step=round(px*1.22)
        if len(lines)*step<=h and (maxlines is None or len(lines)<=maxlines): break
    else: raise ValueError('Text overflow: '+text)
    if vcenter:
        # Center the actual ink, not a nominal five-line block.
        ink=[d.textbbox((0,0),line,font=f,anchor='lt') for line in lines]
        actual=(len(lines)-1)*step+ink[-1][3]
        y+=(h-actual)/2
    if wash_opacity:
        wash_y=y
        for line in lines:
            xx=x+(w-f.getlength(line))/2 if center else x
            ink=d.textbbox((0,0),line,font=f,anchor='lt')
            pad_x=max(5,round(px*.25)); pad_y=max(3,round(px*.18))
            soft_wash(im,(xx-pad_x,wash_y-pad_y,f.getlength(line)+2*pad_x,ink[3]+2*pad_y),opacity=wash_opacity,blur=max(4,round(px*.25)))
            wash_y+=step
    for line in lines:
        xx=x+(w-f.getlength(line))/2 if center else x
        d.text((xx,y),line,font=f,fill=color,anchor='lt'); y+=step
def background(c,w,h,back=False):
    path=background_path(c,back)
    if path:
        image=Image.open(path)
        expected=(1738,905) if back else (1983,793)
        if image.size!=expected:
            raise ValueError(f'Background {path} is {image.size}, expected {expected}; see docs/DESIGN_RULES.md')
        return image.convert('RGB').resize((w,h),Image.Resampling.LANCZOS)
    return Image.new('RGB',(w,h),'#f7f4eb')
def background_path(c,back=False):
    folder=BG/('back' if back else 'front')
    return next((folder/(c['id']+ext) for ext in ('.png','.webp','.jpg') if (folder/(c['id']+ext)).exists()),None)
def soft_wash(im,box,opacity=145,blur=12):
    """Add a trim-safe translucent paper wash behind small unchanged text."""
    x,y,w,h=map(round,box)
    mask=Image.new('L',im.size,0)
    ImageDraw.Draw(mask).rounded_rectangle((x,y,x+w,y+h),radius=max(2,h//3),fill=opacity)
    mask=mask.filter(ImageFilter.GaussianBlur(blur))
    im.paste(Image.new('RGB',im.size,'#fffdf7'),(0,0),mask)
def front(c,w,h):
    im=background(c,w,h)
    color=series_color(c)
    textblock(im,c['front'].get('header','中华人民共和国普通纪念币'),(w*.045,h*.08,w*.72,h*.12),h*.09,bold=True,color=color,wash_opacity=55)
    title=c['front'].get('title',c['display_id']+'\n文字待补')
    textblock(im,title,(w*.045,h*.31,w*.57,h*.43),h*.18,bold=True,color=color)
    footer=re.sub(r'\s*[⦁•·]\s*',' · ',c['front'].get('footer',''))
    textblock(im,footer,(w*.045,h*.85,w*.91,h*.10),h*.060,minsize=20,color=color,wash_opacity=45)
    return im
def back(c,w,h):
    im=background(c,w,h,True)
    color=series_color(c)
    draw=ImageDraw.Draw(im)
    draw.line((round(w*.015),round(h*.50),round(w*.665),round(h*.50)),fill=color,width=max(2,round(DPI*.12/25.4)))
    diameter=c['diameter_mm']
    # A 32mm coin uses 46% of label height; every diameter uses the same scale.
    coin_side=round(h*.46*diameter/32)
    for side,desc,y in [('b',c['description2'] or '描述待补',h*.025),('f',c['description'] or '描述待补',h*.515)]:
        coin=Image.open(LABEL/'coins'/f"{c.get('image_id',c['id'])}_{side}.webp").convert('RGBA')
        coin=coin.crop(coin.getchannel('A').getbbox())
        coin.thumbnail((coin_side,coin_side),Image.Resampling.LANCZOS)
        x=round(w*.13-coin.width/2); cy=round(y+(h*.46-coin.height)/2)
        # A soft offset shadow in the label layout, leaving the coin pixels intact.
        mask=Image.new('L',(w,h),0)
        mask.paste(coin.getchannel('A'),(x+round(h*.008),cy+round(h*.012)))
        mask=mask.filter(ImageFilter.GaussianBlur(h*.009)).point(lambda a:round(a*.27))
        im.paste(Image.new('RGB',(w,h),'#322920'),(0,0),mask)
        im.paste(coin,(x,cy),coin)
        # Both descriptions use the same font size for this coin; at most 5 lines.
        size=round(h*.46/5/1.22)
        while any(len(wrapped(d,font(size,True),w*.41))>5 for d in (c['description2'],c['description'])):
            size-=1
        if size<18: raise ValueError('Description too dense for printed label: '+c['id'])
        if side=='b': REPORT.append({'id':c['id'],'description_font_pt':round(size*72/DPI,2),'needs_shorter_label_description':size<30})
        textblock(im,desc,(w*.255,y,w*.41,h*.46),size,minsize=size,bold=True,color=color,vcenter=True,maxlines=5)
    # Missing coin-specific QR images use the official catalog fallback.
    qrpath=LABEL/'qr'/(c['id']+'.png')
    if not qrpath.exists(): qrpath=LABEL/'qr'/'fallback.png'
    qr=Image.open(qrpath).convert('RGB').resize((round(w*.31),round(w*.31)),Image.Resampling.NEAREST)
    im.paste(qr,(round(w*.8325-qr.width/2),round(h*.025)))
    draw=ImageDraw.Draw(im)
    draw.rectangle((round(w*.68),round(h*.625),round(w*.985),round(h*.85)),fill=color)
    textblock(im,c['display_id'],(w*.685,h*.631,w*.295,h*.105),h*.078,bold=True,center=True,color='white',vcenter=True)
    seq='('+SERIAL[c['id']]+')' if c['id'] in SERIAL else '序号待补'
    textblock(im,seq,(w*.685,h*.740,w*.295,h*.10),h*.062,bold=True,center=True,color='white',vcenter=True)
    soft_wash(im,(w*.69,h*.852,w*.285,h*.115),opacity=135,blur=max(4,round(h*.018)))
    textblock(im,DATES.get(c['id'],''),(w*.69,h*.86,w*.285,h*.095),h*.062,minsize=24,center=True,color=color,vcenter=True)
    return im
def geometry(doc):
    t=doc.tables[0]
    return (doc.sections[0]._sectPr.xml,t._tbl.tblGrid.xml,[r._tr.trPr.xml for r in t.rows],[int(c.width) for r in t.rows for c in r.cells])
def populate(template,output,maker):
    doc=Document(str(template)); before=geometry(doc); t=doc.tables[0]
    original=deepcopy(t._tbl)
    capacity=((len(t.rows)+1)//2)*4
    # Suppress printed guide borders and inner padding; keep all grid widths,
    # row heights, table positioning and page dimensions from the template.
    t.autofit=False
    for b in t._tbl.xpath('.//w:tblBorders/* | .//w:tcBorders/*'):
        b.set(qn('w:val'),'nil')
    for m in t._tbl.xpath('./w:tblPr/w:tblCellMar/*'):
        m.set(qn('w:w'),'0')
    for i,ident in enumerate(IDS):
        slot=i%capacity
        if i and slot==0:
            doc.add_page_break()
            doc._body._body.insert_element_before(deepcopy(original),'w:sectPr')
            t=doc.tables[-1]
            t.autofit=False
            for b in t._tbl.xpath('.//w:tblBorders/* | .//w:tcBorders/*'): b.set(qn('w:val'),'nil')
            for m in t._tbl.xpath('./w:tblPr/w:tblCellMar/*'): m.set(qn('w:w'),'0')
        row=t.rows[(slot//4)*2]; cell=row.cells[slot%4]
        width=int(cell.width); height=int(row.height)
        w=round(width/914400*DPI); h=round(height/914400*DPI)
        picture=BytesIO()
        maker(COINS[ident],w,h).save(picture,format='PNG',dpi=(DPI,DPI)); picture.seek(0)
        cell.text=''; p=cell.paragraphs[0]
        cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.TOP
        margins=OxmlElement('w:tcMar')
        for edge in ('top','left','bottom','right'):
            e=OxmlElement('w:'+edge); e.set(qn('w:w'),'0'); e.set(qn('w:type'),'dxa'); margins.append(e)
        cell._tc.get_or_add_tcPr().append(margins)
        p.paragraph_format.space_before=Pt(0); p.paragraph_format.space_after=Pt(0)
        p.paragraph_format.left_indent=Pt(0); p.paragraph_format.right_indent=Pt(0)
        p.paragraph_format.first_line_indent=Pt(0)
        p.paragraph_format.line_spacing=Pt(1)
        snap=OxmlElement('w:snapToGrid'); snap.set(qn('w:val'),'0'); p._p.get_or_add_pPr().append(snap)
        run=p.add_run(); run.font.size=Pt(1)
        shape=run.add_picture(picture,width=Emu(width),height=Emu(height))
        # Anchor at the cell paragraph origin: no inline baseline/line-grid gap.
        inline=shape._inline; anchor=OxmlElement('wp:anchor')
        for key,val in {'distT':'0','distB':'0','distL':'0','distR':'0','simplePos':'0','relativeHeight':'0','behindDoc':'0','locked':'0','layoutInCell':'1','allowOverlap':'1'}.items(): anchor.set(key,val)
        simple=OxmlElement('wp:simplePos'); simple.set('x','0'); simple.set('y','0'); anchor.append(simple)
        for axis,relative in [('H','column'),('V','paragraph')]:
            pos=OxmlElement('wp:position'+axis); pos.set('relativeFrom',relative)
            offset=OxmlElement('wp:posOffset'); offset.text='0'; pos.append(offset); anchor.append(pos)
        for tag in ('wp:extent','wp:effectExtent'):
            el=inline.find(qn(tag))
            if el is not None: anchor.append(el)
        anchor.append(OxmlElement('wp:wrapNone'))
        for el in list(inline): anchor.append(el)
        inline.getparent().replace(inline,anchor)
    assert geometry(doc)==before,'Template geometry changed'
    for table in doc.tables:
        assert table._tbl.tblGrid.xml==doc.tables[0]._tbl.tblGrid.xml
        assert [r.height for r in table.rows]==[r.height for r in doc.tables[0].rows]
    doc.save(output)
    assert geometry(Document(output))==before
    print(output.name,'geometry identical',flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    scope=parser.add_mutually_exclusive_group()
    scope.add_argument('--back-only',action='store_true'); scope.add_argument('--front-only',action='store_true')
    args=parser.parse_args()
    assert len(IDS)==len(set(IDS)), 'Duplicate coin IDs'
    assert [c['serial'] for c in CATALOG]==list(range(1,len(CATALOG)+1)), 'Serial numbers must follow the catalog order'
    output=LABEL/'output'; output.mkdir(exist_ok=True)
    if not args.back_only: populate(SOURCES/'ZY8252.docx',output/'labels_8252_front.docx',front)
    if not args.front_only: populate(SOURCES/'ZY8240.docx',output/'labels_8240_back.docx',back)
    index=[{'serial':c['serial'],'id':c['id'],'name':c['front'].get('title','文字待补').replace('\n',''),'front_page':i//52+1,'front_row':(i%52)//4+1,'front_col':i%4+1,'back_page':i//40+1,'back_row':(i%40)//4+1,'back_col':i%4+1,'front_background':bool(background_path(c)),'back_background':bool(background_path(c,True)),'missing_text':[field for field in ('description2','description','front') if not c[field]],'missing_date':not c.get('release_date')} for i,c in enumerate(CATALOG)]
    (output/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
    if REPORT: (output/'layout_report.json').write_text(json.dumps(REPORT,ensure_ascii=False,indent=2),encoding='utf-8')
