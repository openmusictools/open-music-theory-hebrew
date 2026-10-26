#!/usr/bin/env python3
"""Create a phone-sized PDF, then PNG images. Never synthesize audio."""
import argparse, hashlib, html, importlib.util, json, shutil, subprocess, sys, zipfile
from pathlib import Path
from pypdf import PdfReader
from PIL import Image

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--work',type=Path,default=Path('dist/mobile-work'))
    ap.add_argument('--assets',type=Path,default=Path('release-assets'))
    ap.add_argument('--site',type=Path,default=Path('dist/mobile-site'))
    args=ap.parse_args(); source=args.source.resolve(); work=args.work.resolve()
    work.mkdir(parents=True,exist_ok=True);args.assets.mkdir(parents=True,exist_ok=True)
    args.site.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(source/'scripts'))
    spec=importlib.util.spec_from_file_location('mobile_export',source/'scripts/export_book.py')
    exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)
    exporter.CSS+='''
@page {size:100mm 178mm; margin:6mm 6mm 9mm; @bottom-center {font-size:8pt}}
body {font-size:11pt;line-height:1.5} h1 {font-size:19pt} h2 {font-size:16pt} h3 {font-size:13pt}
img {max-width:100%; max-height:145mm} table {font-size:8pt} table.wide {font-size:7pt}
th,td {padding:2pt} .cover {padding-top:6mm} .path {font-size:7pt}
'''
    sys.argv=['export_book.py','--output',str(work/'pdf')];exporter.main()
    pdf=work/'pdf/open-music-theory-static.pdf'; reader=PdfReader(pdf)
    pages=len(reader.pages); assert pages>0
    # Direct top-level PDF bookmarks partition the exact exported reading order.
    starts={0:'פתיחה ותוכן עניינים'}
    for item in reader.outline:
        if isinstance(item,list):continue
        n=reader.get_destination_page_number(item)
        if n is not None:starts[n]=str(item.title)
    boundaries=sorted(starts); segments=[]
    for i,start in enumerate(boundaries):
        end=boundaries[i+1] if i+1<len(boundaries) else pages
        if end>start:segments.append({'number':len(segments)+1,'title':starts[start],'start':start+1,'end':end})
    pngdir=work/'pages';pngdir.mkdir(exist_ok=True)
    subprocess.run(['pdftoppm','-png','-scale-to-x','1080','-scale-to-y','-1',str(pdf),str(pngdir/'page')],check=True)
    pngs=sorted(pngdir.glob('page-*.png')); assert len(pngs)==pages
    records=[]
    for i,p in enumerate(pngs,1):
        with Image.open(p) as im:
            im.verify()
        records.append({'page':i,'name':f'page-{i:05d}.png','bytes':p.stat().st_size,'sha256':digest(p)})
    chapters=args.site/'chapters';chapters.mkdir(exist_ok=True)
    for seg in segments:
        name=f'chapter-{seg["number"]:03d}.zip';seg['zip']=name
        with zipfile.ZipFile(chapters/name,'w',zipfile.ZIP_STORED) as z:
            for n in range(seg['start'],seg['end']+1):z.write(pngs[n-1],records[n-1]['name'])
        with zipfile.ZipFile(chapters/name) as z: assert z.testzip() is None
        seg['bytes']=(chapters/name).stat().st_size
    sample_numbers=sorted(set([1, min(pages,12), *[round(1+(pages-1)*i/7) for i in range(8)]]))
    # Exactly ten samples, including beginning, end, and representative chapter starts.
    for seg in segments:
        if len(sample_numbers)>=10:break
        if seg['start'] not in sample_numbers:sample_numbers.append(seg['start'])
    sample_numbers=sorted(sample_numbers[:10]);preview=args.site/'preview';preview.mkdir(exist_ok=True)
    for n in sample_numbers:shutil.copyfile(pngs[n-1],preview/records[n-1]['name'])
    manifest={'format':'PNG','width_pixels':1080,'mobile_pdf_page_mm':[100,178],
              'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip(),
              'pages':pages,'pdf_sha256':digest(pdf),'chapters':segments,'files':records,
              'preview_pages':sample_numbers,'visual_qa':'Ten sample images are reviewed separately; not every page is visually inspected.',
              'original_pdf_annexes':'Original appendix page sizes and source notation remain unchanged.'}
    (args.site/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    cards=''.join(f'<li><a href="chapters/{s["zip"]}">{s["number"]:03d} — {html.escape(s["title"])}</a> · עמודים {s["start"]}–{s["end"]} · {s["bytes"]/1048576:.1f} MB</li>' for s in segments)
    samples=''.join(f'<figure><img loading="lazy" src="preview/{records[n-1]["name"]}" alt="עמוד {n}"><figcaption>עמוד {n}</figcaption></figure>' for n in sample_numbers)
    full='https://github.com/openmusictools/open-music-theory-hebrew/releases/download/'
    index='''<!doctype html><html lang="he" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>הספר כתמונות PNG לסלולרי</title><style>body{font:18px/1.6 Arial,sans-serif;max-width:950px;margin:auto;padding:16px;background:#faf9f3;color:#202c2a}a{color:#21684f}li{margin:10px 0}img{max-width:100%;height:auto;border:1px solid #ccd1c8}figure{margin:24px 0}header{padding:12px 0;border-bottom:1px solid #ccc}</style><header><a href="../index.html#downloads">חזרה לאתר הספר ולהורדות</a></header><h1>הספר כתמונות PNG — לסלולרי</h1><p>פריסה צרה וכתב מוגדל, שנוצרו דרך PDF. תמונות ממוספרות לפי סדר הקריאה. דפי נספחים מקוריים שומרים על מידות המקור וניתן להגדילם. מהדורת בטא; אימות המדיה והתרגום עדיין בעבודה.</p>'''
    index+=f'<p>{pages} תמונות · <a href="../index.html#downloads">הורדת כל הספר ב־ZIP מאזור ההורדות</a></p><h2>הורדה לפי פרקים ונספחים</h2><ol>{cards}</ol><h2>עשר תמונות לדוגמה</h2>{samples}</html>'
    (args.site/'index.html').write_text(index)
    fullzip=args.assets/'book-mobile-png.zip'
    with zipfile.ZipFile(fullzip,'w',zipfile.ZIP_STORED,allowZip64=True) as z:
        for p,r in zip(pngs,records):z.write(p,'pages/'+r['name'])
        z.writestr('manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
        z.writestr('README.txt','תאוריית המוזיקה הפתוחה — תמונות PNG לסלולרי.\nקראו לפי המספור בתיקיית pages.\nפריסה צרה דרך PDF; נספחים מקוריים נשמרו בשלמותם.\nטקסט CC BY-SA 4.0; לכל נכס רישיונו וייחוסו במקור.\nhttps://openmusictools.github.io/open-music-theory-hebrew/\nבדיקת תצוגה מדגמית בלבד, לא של כל תמונה.\n')
    with zipfile.ZipFile(fullzip) as z:assert z.testzip() is None
    shutil.copyfile(pdf,args.assets/'book-mobile.pdf')
    print(json.dumps({'pages':pages,'chapter_packages':len(segments),'sample_pages':sample_numbers,'zip_bytes':fullzip.stat().st_size,'sha256':digest(fullzip)}),flush=True)

if __name__=='__main__':main()
