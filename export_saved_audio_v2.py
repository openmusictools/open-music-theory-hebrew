#!/usr/bin/env python3
"""Export a detached v2 snapshot. Never synthesize, retag, or modify the state."""
import argparse, hashlib, json, shutil, sys
from pathlib import Path

def export(source, state, output):
    sys.path.insert(0, str(source/'scripts'))
    from export_audiobook_v2 import approved_plan, MODEL
    from mutagen.id3 import ID3
    chapters, selection = approved_plan()
    if selection['voice'] != 'Iapetus':
        raise RuntimeError('Unexpected approved voice')
    if output.exists():
        raise RuntimeError('Export destination must be new')
    output.mkdir(parents=True)
    (output/'chapters').mkdir()
    (output/'transcripts').mkdir()
    report = {'status':'saved_audio_exported','requests_this_run':0,
              'voice':selection['voice'],'model':MODEL,'edition':2,'chapters':[]}
    for chapter in chapters:
        number = chapter['chapter']
        filename = chapter['title']+'.mp3'
        receipt_path = state/'segments'/chapter['id']/'receipt.json'
        item = {'chapter':number,'title':chapter['title'],'filename':filename,'status':'not_completed'}
        if receipt_path.exists():
            receipt = json.loads(receipt_path.read_text())
            path = state/'chapters'/filename
            if receipt['chapter'] != number or receipt['source_sha256'] != chapter['source_sha256']:
                raise RuntimeError(f'Chapter {number}: source/receipt mismatch')
            if receipt['opening_sha256'] != selection['opening_mp3_sha256']:
                raise RuntimeError(f'Chapter {number}: approved opening mismatch')
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != receipt['sha256']:
                raise RuntimeError(f'Chapter {number}: audio checksum mismatch')
            tags = ID3(path)
            if str(tags.get('TXXX:Voice')) != selection['voice'] or str(tags.get('TXXX:Model')) != MODEL:
                raise RuntimeError(f'Chapter {number}: voice/model mismatch')
            shutil.copyfile(path,output/'chapters'/filename)
            item.update(status='generated',sha256=digest,voice=selection['voice'])
        (output/'transcripts'/f'{number:03d}.txt').write_text(chapter['transcript'])
        report['chapters'].append(item)
    if not any(c['status']=='generated' for c in report['chapters']):
        raise RuntimeError('No complete verified v2 chapters in snapshot')
    (output/'progress.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'complete':sum(c['status']=='generated' for c in report['chapters']),
                      'eligible':len(chapters),'voice':selection['voice'],'synthesis_requests':0}))
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--state',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    export(a.source.resolve(),a.state.resolve(),a.output.resolve())
