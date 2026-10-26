"""Restore the exact published mobile reader on ordinary website rebuilds."""
import argparse,hashlib,json,stat,urllib.request,zipfile
from pathlib import Path,PurePosixPath

def main():
    p=argparse.ArgumentParser();p.add_argument('--release',type=Path,required=True);p.add_argument('--output',type=Path,default=Path('dist/mobile-site'));a=p.parse_args()
    release=json.loads(a.release.read_text());asset=next((x for x in release.get('assets',[]) if x['name']=='book-mobile-site.zip'),None)
    if not asset:
        print('This release has no mobile reader archive; existing downloads remain available.');return
    url=asset['browser_download_url']
    expected='https://github.com/openmusictools/open-music-theory-hebrew/releases/download/'
    if not url.startswith(expected):raise ValueError('Unexpected mobile archive origin')
    archive=Path('dist/published-mobile-site.zip');archive.parent.mkdir(parents=True,exist_ok=True)
    h=hashlib.sha256();size=0
    with urllib.request.urlopen(url,timeout=180) as src,archive.open('wb') as dst:
        while b:=src.read(1024*1024):
            size+=len(b)
            if size>900*1024*1024:raise ValueError('Mobile archive too large')
            h.update(b);dst.write(b)
    if size!=asset['size'] or 'sha256:'+h.hexdigest()!=asset.get('digest'):raise ValueError('Published mobile archive checksum mismatch')
    with zipfile.ZipFile(archive) as z:
        if sum(x.file_size for x in z.infolist())>900*1024*1024:raise ValueError('Expanded archive too large')
        for x in z.infolist():
            name=PurePosixPath(x.filename)
            if name.is_absolute() or '..' in name.parts or '\\' in x.filename or stat.S_ISLNK(x.external_attr>>16):raise ValueError('Unsafe archive path')
        if z.testzip() is not None:raise ValueError('Archive CRC mismatch')
        z.extractall(a.output)
    m=json.loads((a.output/'manifest.json').read_text())
    records={x['page']:x for x in m['files']}
    for n in m['preview_pages']:
        f=a.output/'preview'/records[n]['name']
        if hashlib.sha256(f.read_bytes()).hexdigest()!=records[n]['sha256']:raise ValueError('Preview hash mismatch')
    for c in m['chapters']:
        with zipfile.ZipFile(a.output/'chapters'/c['zip']) as z:
            expected=[records[n]['name'] for n in range(c['start'],c['end']+1)]
            if z.namelist()!=expected or z.testzip() is not None:raise ValueError('Chapter package mismatch')
    print(f'Restored exact published mobile reader: {m["pages"]} PNG pages; {len(m["preview_pages"])} previews.')

if __name__=='__main__':main()
