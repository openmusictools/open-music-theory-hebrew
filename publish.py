#!/usr/bin/env python3
"""Build the Hebrew reader and six reproducible release downloads. No narration API."""
import base64, argparse, hashlib, html, json, re, shutil, subprocess, zipfile
from pathlib import Path
from urllib.parse import urlsplit, unquote, quote
import markdown, yaml
from bs4 import BeautifulSoup

REPO = 'openmusictools/open-music-theory-hebrew'
SOURCE_REPO = 'open-music-theory-he/open-music-theory-hebrew'
ASSETS = {'pdf':'open-music-theory-hebrew.pdf', 'pdf-annexes':'book-and-annexes.zip',
          'audio':'audiobook.zip', 'audio-annexes':'audiobook-and-annexes.zip',
          'everything':'all-outputs.zip', 'sources':'everything-with-sources.zip'}
LABELS = [('pdf','PDF הספר','לקריאה ולהדפסה'),('pdf-annexes','PDF עם נספחים','הספר והמדיה המצורפת'),
          ('audio','ספר שמע','פרקי MP3 שלמים ותמלילים'),('audio-annexes','ספר שמע עם נספחים','הקלטות וחומרי העזר'),
          ('everything','כל הקבצים (לא כולל קבצי מקור)','PDF, שמע ונספחים — ללא קבצי מקור'),('sources','הכול כולל קבצי מקור','גם תוכן המקור, תיעוד ומקטעי שמע')]
MEDIA = {'.png','.jpg','.jpeg','.svg','.gif','.webp','.pdf','.mp3','.wav','.ogg','.m4a','.mp4','.webm'}
CSS = '''
:root{--paper:#f8f6ef;--ink:#202c2a;--muted:#64726b;--line:#d9dfd4;--accent:#21684f;--card:#fffefa;--gold:#e9bb66;--serif:Georgia,"Times New Roman",serif;font-family:Arial,"Noto Sans Hebrew",sans-serif;color-scheme:light}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:90px}body{margin:0;background:var(--paper);color:var(--ink);font-size:17px;line-height:1.7}a{color:var(--accent);text-underline-offset:4px}button,input{font:inherit}button{cursor:pointer}button:focus-visible,a:focus-visible,input:focus-visible{outline:3px solid #cd862b;outline-offset:4px}.skip{position:absolute;top:-100px}.skip:focus{top:10px;z-index:20;background:white;padding:10px}.wrap{max-width:1260px;margin:auto;padding:0 36px}header{position:sticky;top:0;background:var(--paper);border-bottom:1px solid var(--line);z-index:8}.header-inner{display:flex;align-items:center;justify-content:space-between;gap:22px;min-height:82px}.brand{text-decoration:none;color:var(--ink);font-weight:800;line-height:1.3;font-size:19px}.brand small{display:block;font-size:11px;letter-spacing:.12em;color:var(--muted);margin-top:5px}.nav{display:flex;gap:25px;align-items:center}.nav a{text-decoration:none;font-size:15px}.beta{background:#efe2bf;border:1px solid #d8bd80;color:#694b19;border-radius:50px;padding:3px 12px;font-size:12px;font-weight:bold}.eyebrow{font-size:12px;letter-spacing:.1em;color:var(--accent);font-weight:bold}.hero{display:grid;grid-template-columns:1.12fr 1fr;gap:70px;align-items:center;padding:65px 0 55px}.hero h1{font-size:clamp(42px,5vw,74px);line-height:1.13;letter-spacing:-.05em;margin:17px 0 24px}.hero h1 span{font-weight:400;display:block}.hero p{color:var(--muted);max-width:540px;font-size:19px}.hero-art{position:relative}.hero-art img{width:100%;display:block;border-radius:190px 190px 8px 8px}.art-caption{font-size:12px;color:var(--muted);display:flex;justify-content:space-between;margin-top:12px}.actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:28px}.button{display:inline-flex;justify-content:center;align-items:center;padding:12px 24px;border-radius:5px;background:var(--accent);color:#fff;text-decoration:none;border:1px solid var(--accent);font-size:15px;font-weight:bold}.button.secondary{background:transparent;color:var(--accent)}.intro-line{border-block:1px solid var(--line);padding:20px 0;display:flex;gap:26px;justify-content:space-between;color:var(--muted);font-size:14px}.section{padding:54px 0}.section-title{display:flex;justify-content:space-between;align-items:baseline;gap:20px;margin-bottom:24px}.section h2{font-size:32px;line-height:1.3;margin:0}.section-title p{color:var(--muted);font-size:15px;margin:0}.catalog{display:grid;grid-template-columns:repeat(3,1fr);gap:0 35px}.topic{padding:22px 0;border-top:1px solid var(--line)}.topic h3{font-size:19px;margin:0 0 9px}.topic a{display:block;text-decoration:none;color:var(--muted);padding:3px 0;font-size:15px}.topic a:hover{color:var(--accent);text-decoration:underline}.topic .more{color:var(--accent);margin-top:8px;font-weight:bold}.notice{border-inline-start:3px solid var(--gold);padding:12px 20px;background:#f3eddd;font-size:15px}.downloads{background:#eaf0e5;border-block:1px solid var(--line)}.download-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.download-card{display:flex;flex-direction:column;gap:8px;background:var(--card);border:1px solid var(--line);padding:23px;text-decoration:none;color:var(--ink);border-radius:6px;transition:transform .15s,border-color .15s}.download-card:hover{transform:translateY(-3px);border-color:var(--accent)}.download-card strong{font-size:19px}.download-card small{color:var(--muted)}.download-card .format{font-size:11px;color:var(--accent);letter-spacing:.1em;font-weight:bold}.release-line{font-size:14px;color:var(--muted);margin-bottom:23px}.about-grid{display:grid;grid-template-columns:1fr 1fr;gap:65px}.about-grid p{color:var(--muted);font-size:16px}.about-grid h3{font-size:24px}.about-grid img{width:100%;border-radius:5px;max-height:190px;object-fit:cover}.search{border:1px solid var(--line);background:var(--card);border-radius:5px;padding:10px 14px;width:100%;color:var(--ink)}.search-block{max-width:630px;margin-bottom:30px}.search-results{display:none;background:var(--card);border:1px solid var(--line);padding:15px;margin-top:10px;max-height:370px;overflow:auto}.search-results.visible{display:block}.search-results a{display:block;padding:8px;border-bottom:1px solid var(--line);text-decoration:none}.search-results small{display:block;color:var(--muted);font-size:13px}.reader{display:grid;grid-template-columns:265px minmax(0,1fr);gap:65px;padding-top:32px}.sidebar{position:sticky;top:112px;align-self:start;max-height:calc(100vh - 140px);overflow:auto;padding-bottom:30px}.sidebar details{border-bottom:1px solid var(--line);padding:10px 0}.sidebar summary{cursor:pointer;font-weight:bold;font-size:14px}.sidebar a{display:block;text-decoration:none;color:var(--muted);font-size:13px;padding:6px 10px;border-inline-start:2px solid transparent}.sidebar a.current{border-color:var(--accent);color:var(--accent);font-weight:bold;background:#eaf0e5}.sidebar a:hover{color:var(--accent)}.chapter{min-width:0;max-width:850px;padding-bottom:60px}.chapter-head{border-bottom:1px solid var(--line);padding-bottom:23px;margin-bottom:30px}.chapter-head h1{font-size:clamp(30px,4vw,45px);line-height:1.25;margin:12px 0}.chapter-tools{display:flex;gap:10px;align-items:center;flex-wrap:wrap;font-size:12px;color:var(--muted)}.chapter-tools button{background:var(--card);border:1px solid var(--line);border-radius:4px;padding:5px 10px;color:var(--ink);font-size:13px}.prose{font-size:var(--reading-size,18px);line-height:1.9;overflow-wrap:anywhere}.prose h1,.prose h2,.prose h3{line-height:1.35;margin-top:2em;scroll-margin-top:110px}.prose h2{font-size:1.5em}.prose h3{font-size:1.2em}.prose img{max-width:100%;height:auto;background:white;border-radius:3px}.prose figure{margin:24px 0}.prose figcaption{font-size:13px;color:var(--muted)}.prose pre{direction:ltr;text-align:left;white-space:pre-wrap;background:#eaf0e5;padding:16px;border-radius:5px;overflow:auto}.prose code{direction:ltr;unicode-bidi:isolate}.prose blockquote{margin:20px 0;border-inline-start:3px solid var(--gold);padding:10px 20px;background:#f3eddd}.prose table{display:block;overflow-x:auto;border-collapse:collapse;font-size:15px;max-width:100%}.prose th,.prose td{border:1px solid var(--line);padding:8px 12px;vertical-align:top}.prose th{background:#eaf0e5}.prose audio{max-width:100%;width:100%;margin:12px 0}.media-link{padding:18px;border:1px solid var(--line);background:var(--card);border-radius:6px;margin:20px 0;font-size:15px}.chapter-nav{display:flex;justify-content:space-between;gap:20px;border-top:1px solid var(--line);padding-top:22px;margin-top:40px}.chapter-nav a{max-width:46%;text-decoration:none;font-size:15px}.chapter-nav small{display:block;color:var(--muted);font-size:12px}.footer{border-top:1px solid var(--line);padding:32px 0;color:var(--muted);font-size:12px}.footer-inner{display:flex;justify-content:space-between;gap:30px}.footer a{color:var(--muted)}.source-line{font-size:12px;color:var(--muted);margin-top:24px}.full-toc{columns:3;column-gap:40px}.full-toc h2,.full-toc h3{break-after:avoid}.full-toc h2{font-size:23px}.full-toc p{font-size:15px}.full-toc a{display:inline-block;padding:3px 0}body.dark{--paper:#18221e;--ink:#ecf0e8;--muted:#b0bdb3;--line:#3d5043;--accent:#9dd5b6;--card:#222f27;color-scheme:dark}body.dark .notice,body.dark .prose blockquote{background:#353226}body.dark .downloads,body.dark .prose pre,body.dark .prose th,body.dark .sidebar a.current{background:#24352b}body.dark .button{color:#18221e}body.dark .button.secondary{color:var(--accent)}
@media(max-width:1000px){.hero{gap:35px}.reader{gap:30px;grid-template-columns:220px minmax(0,1fr)}.catalog,.download-grid{grid-template-columns:repeat(2,1fr)}.full-toc{columns:2}}@media(max-width:700px){.wrap{padding:0 20px}.header-inner{min-height:72px;gap:12px}.brand{font-size:15px}.brand small{font-size:9px}.nav{gap:13px}.nav a{font-size:12px}.nav .source-nav{display:none}.beta{padding:2px 7px}.hero{display:flex;flex-direction:column;gap:35px;padding:35px 0}.hero h1{font-size:46px}.hero p{font-size:17px}.hero-art{width:85%;max-width:380px}.intro-line{flex-wrap:wrap;gap:8px 20px}.section{padding:35px 0}.section-title{display:block}.section-title p{margin-top:8px}.catalog,.download-grid,.about-grid{grid-template-columns:1fr;gap:15px}.download-card{padding:18px}.reader{display:block;padding-top:20px}.sidebar{position:static;max-height:280px;border:1px solid var(--line);padding:12px;margin-bottom:25px}.sidebar>details{display:none}.sidebar.open>details{display:block}.sidebar-toggle{display:block!important;width:100%;background:var(--card);border:1px solid var(--line);padding:8px;color:var(--ink)}.chapter-head h1{font-size:32px}.prose{font-size:var(--reading-size,17px)}.full-toc{columns:1}.footer-inner{display:block}.chapter-nav{font-size:14px}}.sidebar-toggle{display:none}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}@media print{header,.sidebar,.chapter-tools,.chapter-nav,.footer,.search-block{display:none}.reader{display:block}.wrap{padding:0}.prose{font-size:12pt}.chapter{max-width:none}}
'''
JS = r'''
const repo='openmusictools/open-music-theory-hebrew';
const prefix=document.body.dataset.prefix||'';
const slots={"pdf":"open-music-theory-hebrew.pdf","pdf-annexes":"book-and-annexes.zip","audio":"audiobook.zip","audio-annexes":"audiobook-and-annexes.zip","everything":"all-outputs.zip","sources":"everything-with-sources.zip"};
function useRelease(r){if(!r||!Array.isArray(r.assets))return;let found=0;for(const [key,name] of Object.entries(slots)){const a=r.assets.find(a=>a.name===name);if(a){document.querySelectorAll('[data-download="'+key+'"]').forEach(el=>{el.href=a.browser_download_url;el.querySelector('.size')?.replaceChildren(document.createTextNode((a.size/1048576).toFixed(1)+' MB'));});found++;}}if(found){document.querySelectorAll('[data-release]').forEach(el=>el.textContent=(r.name||r.tag_name)+' · '+new Date(r.published_at).toLocaleDateString('he-IL'));document.querySelectorAll('[data-release-link]').forEach(el=>el.href=r.html_url);}}
fetch(prefix+'release.json').then(r=>r.ok?r.json():null).then(useRelease).catch(()=>{});
// Include beta releases: /latest deliberately excludes prereleases.
fetch('https://api.github.com/repos/'+repo+'/releases?per_page=30').then(r=>r.ok?r.json():null).then(rs=>{if(Array.isArray(rs))useRelease(rs.find(r=>!r.draft&&Object.values(slots).every(n=>r.assets.some(a=>a.name===n))));}).catch(()=>{});
let indexPromise;function index(){return indexPromise||(indexPromise=fetch(prefix+'search.json').then(r=>r.json()));}
function normalize(s){return s.normalize('NFKD').replace(/[\u0591-\u05c7]/g,'').toLowerCase();}
document.querySelectorAll('[data-search]').forEach(input=>{let seq=0;input.addEventListener('input',async()=>{const token=++seq,q=normalize(input.value.trim()),box=input.parentElement.querySelector('.search-results');if(!q){box.replaceChildren();box.classList.remove('visible');return;}const data=await index().catch(()=>[]);if(token!==seq)return;const terms=q.split(/\s+/),items=data.filter(d=>terms.every(t=>normalize(d.title+' '+d.text).includes(t))).sort((a,b)=>Number(normalize(b.title).includes(q))-Number(normalize(a.title).includes(q))).slice(0,30);box.replaceChildren();box.classList.add('visible');if(!items.length){box.textContent='לא נמצאו פרקים מתאימים.';return;}for(const d of items){const a=document.createElement('a');a.href=prefix+d.path;a.textContent=d.title;const s=document.createElement('small');s.textContent=d.group;a.append(s);box.append(a);}});});
try{if(localStorage.getItem('omt-theme')==='dark')document.body.classList.add('dark');const size=localStorage.getItem('omt-size');if(size)document.documentElement.style.setProperty('--reading-size',size+'px');}catch{}
document.querySelector('[data-theme]')?.addEventListener('click',()=>{document.body.classList.toggle('dark');try{localStorage.setItem('omt-theme',document.body.classList.contains('dark')?'dark':'light');}catch{}});
document.querySelectorAll('[data-size]').forEach(b=>b.addEventListener('click',()=>{const now=parseFloat(getComputedStyle(document.querySelector('.prose')).fontSize),n=Math.min(26,Math.max(15,now+Number(b.dataset.size)));document.documentElement.style.setProperty('--reading-size',n+'px');try{localStorage.setItem('omt-size',n);}catch{}}));
document.querySelector('[data-sidebar]')?.addEventListener('click',e=>{const side=document.querySelector('.sidebar');side.classList.toggle('open');e.currentTarget.setAttribute('aria-expanded',String(side.classList.contains('open')));});
'''

def meta(p):
    text=p.read_text(encoding='utf-8')
    if text.startswith('---\n'):
        _,head,text=text.split('---',2)
        return yaml.safe_load(head) or {},text
    return {},text

def write(p,text):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')

def relative(depth,path):return '../'*depth+path

FEEDBACK_HTML = '<dialog id="fb-dialog" aria-labelledby="fb-title">\n  <div class="card-hdr"><span class="dot"></span><h2 id="fb-title">משוב</h2></div>\n  <form id="fb-form" class="dlg-body" novalidate>\n    <div class="sec-lbl" id="fb-rate-lbl">מה דעתך הכללית?</div>\n    <div id="fb-stars" class="stars" role="radiogroup" aria-labelledby="fb-rate-lbl">\n      <button type="button" class="star" role="radio" aria-checked="false" aria-label="כוכב אחד">★</button>\n      <button type="button" class="star" role="radio" aria-checked="false" aria-label="2 כוכבים">★</button>\n      <button type="button" class="star" role="radio" aria-checked="false" aria-label="3 כוכבים">★</button>\n      <button type="button" class="star" role="radio" aria-checked="false" aria-label="4 כוכבים">★</button>\n      <button type="button" class="star" role="radio" aria-checked="false" aria-label="5 כוכבים">★</button>\n    </div>\n    <div id="fb-rating-label" class="rating-lbl" aria-hidden="true"></div>\n    <label class="sec-lbl" for="fb-text">מה אפשר לשפר?</label>\n    <textarea id="fb-text" class="txt-input" rows="4" maxlength="2000"></textarea>\n    <label class="sec-lbl" for="fb-email">כתובת מייל (לא חובה)</label>\n    <input id="fb-email" class="txt-input" type="email" dir="ltr" autocomplete="email">\n    <p class="fb-note">המשוב נשלח ל־Google Forms. כתובת העמוד מצורפת למשוב; מייל הוא לבחירתכם.</p><p id="fb-status" class="fb-status" role="status"></p>\n    <div class="dlg-actions">\n      <button id="fb-submit" class="go-btn" type="submit">שליחה</button>\n      <button class="ghost-btn" type="button" data-close>ביטול</button>\n    </div>\n  </form>\n  <div id="fb-thanks" class="dlg-body thanks" hidden>\n    <p>המשוב נשלח, תודה לך!</p>\n    <button id="fb-thanks-close" class="close-btn" type="button" data-close>סגירה</button>\n  </div>\n</dialog>'
FEEDBACK_JS = '/* Chord Lab — feedback dialog. Posts straight to a Google Form (formResponse endpoint). */\n(function (root) {\n  \'use strict\';\n  const FORM_ID = \'1FAIpQLSelwxmur-QrR6nQqPsKpWeEtYI1yJVHlRtfwWp9pMNWZRBzLA\';\n  const ENDPOINT = \'https://docs.google.com/forms/d/e/\' + FORM_ID + \'/formResponse\';\n  const ENTRY = { rating: \'entry.1002469539\', improve: \'entry.1816896131\', email: \'entry.2058120958\', tool: \'entry.572294768\' };\n  const LABELS = [\'\', \'גרוע\', \'חלש\', \'סביר\', \'טוב\', \'מצוין\'];\n  const COOLDOWN_MS = 30000;\n\n  /** Sends the answers as an application/x-www-form-urlencoded POST. The response is opaque (no-cors). */\n  async function send({ rating, improve, email, tool }) {\n    const body = new URLSearchParams();\n    body.set(ENTRY.tool, tool || document.body.dataset.feedbackTool || \'מילון האקורדים\');\n    body.set(ENTRY.rating, String(rating)); // sent as a plain number: "1".."5"\n    body.set(ENTRY.improve, improve || \'\');\n    body.set(ENTRY.email, email || \'\');\n    const controller = new AbortController();\n    const timeout = setTimeout(() => controller.abort(), 20000);\n    try { await fetch(ENDPOINT, { signal: controller.signal, method: \'POST\', mode: \'no-cors\', credentials: \'omit\', referrerPolicy: \'no-referrer\', body }); } finally { clearTimeout(timeout); }\n  }\n\n  function init(getContext = () => ({ url: location.href, page: document.title })) {\n    const $ = (id) => document.getElementById(id);\n    const dlg = $(\'fb-dialog\'), form = $(\'fb-form\'), stars = Array.from(document.querySelectorAll(\'#fb-stars .star\'));\n    const status = $(\'fb-status\'), submit = $(\'fb-submit\'), label = $(\'fb-rating-label\');\n    let rating = 0, sending = false;\n\n    function paint(hover) {\n      const n = hover || rating;\n      stars.forEach((s, i) => {\n        s.classList.toggle(\'on\', i < n);\n        s.setAttribute(\'aria-checked\', String(i + 1 === rating));\n        s.tabIndex = (rating ? i + 1 === rating : i === 0) ? 0 : -1;\n      });\n      label.textContent = n ? `${n} — ${LABELS[n]}` : \'\';\n    }\n    function setRating(n) { rating = n; paint(); status.textContent = \'\'; }\n\n    stars.forEach((s, i) => {\n      s.addEventListener(\'click\', () => setRating(i + 1));\n      s.addEventListener(\'mouseenter\', () => paint(i + 1));\n      s.addEventListener(\'mouseleave\', () => paint());\n      s.addEventListener(\'keydown\', (e) => {\n        const k = e.key;\n        let n = null;\n        // The page is RTL: star 1 is on the right, so ArrowLeft moves toward 5.\n        if (k === \'ArrowLeft\' || k === \'ArrowUp\') n = Math.min(5, (rating || 0) + 1);\n        if (k === \'ArrowRight\' || k === \'ArrowDown\') n = Math.max(1, (rating || 2) - 1);\n        if (k === \'Home\') n = 1;\n        if (k === \'End\') n = 5;\n        if (n) { e.preventDefault(); setRating(n); stars[n - 1].focus(); }\n      });\n    });\n\n    function reset() {\n      form.reset(); rating = 0; paint(); status.textContent = \'\'; status.className = \'fb-status\';\n      form.hidden = false; $(\'fb-thanks\').hidden = true; submit.disabled = false;\n    }\n    function open() { if (sending) return; reset(); dlg.showModal(); }\n    document.querySelectorAll(\'[data-open-feedback]\').forEach((b) => b.addEventListener(\'click\', open));\n    dlg.addEventListener(\'click\', (e) => { if (e.target === dlg) dlg.close(); });\n    dlg.querySelectorAll(\'[data-close]\').forEach((b) => b.addEventListener(\'click\', () => dlg.close()));\n\n    function fail(msg) { status.textContent = msg; status.className = \'fb-status err\'; }\n\n    form.addEventListener(\'submit\', async (e) => {\n      e.preventDefault();\n      if (sending) return;\n      if (!rating) return fail(\'נא לבחור דירוג בכוכבים (1–5).\');\n      const email = $(\'fb-email\').value.trim();\n      if (email && !/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)) return fail(\'כתובת המייל אינה תקינה.\');\n      let last = 0;\n      try { last = Number(localStorage.getItem(\'omt.feedback.\' + (document.body.dataset.feedbackTool || \'chord\')) || 0); } catch (_) { /* storage may be blocked */ }\n      if (Date.now() - last < COOLDOWN_MS) return fail(\'המשוב כבר נשלח. אפשר לשלוח שוב בעוד רגע.\');\n      const ctx = getContext();\n      const text = $(\'fb-text\').value.trim().slice(0, 2000);\n      const context = ctx.chord ? `אקורד: ${ctx.chord}` : `עמוד: ${ctx.page || document.title}`;\n      const improve = (text ? text + \'\\n\\n\' : \'\') + `[${context} | כתובת: ${ctx.url}]`;\n      sending = true; submit.disabled = true; status.className = \'fb-status\'; status.textContent = \'שולח…\';\n      try {\n        await send({ rating, improve, email });\n        try { localStorage.setItem(\'omt.feedback.\' + (document.body.dataset.feedbackTool || \'chord\'), String(Date.now())); } catch (_) { /* ignore */ }\n        form.hidden = true; $(\'fb-thanks\').hidden = false; $(\'fb-thanks-close\').focus();\n      } catch (_) {\n        fail(\'לא ניתן להשלים את השליחה. בדקו את החיבור. אם חלף זמן רב, ייתכן שהמשוב כבר התקבל.\');\n        submit.disabled = false;\n      } finally { sending = false; }\n    });\n    paint();\n  }\n\n  root.ChordFeedback = { init, send };\n})(self);\n\nChordFeedback.init();'
FEEDBACK_CSS = 'body{--fb-accent:#30634f;--fb-soft:#eaf0e5;--fb-radius:5px;--fb-paper:#f8f7ef;--fb-ink:#213c32}\n#fb-dialog{direction:rtl;box-sizing:border-box;width:min(520px,calc(100vw - 28px));max-height:calc(100dvh - 32px);overflow:auto;border:1px solid var(--fb-accent);border-radius:var(--fb-radius,18px);padding:0;background:var(--fb-paper,#fff);color:var(--fb-ink,#302947);font:16px/1.6 system-ui,sans-serif}#fb-dialog::backdrop{background:rgba(20,30,40,.55)}#fb-dialog [hidden]{display:none!important}#fb-dialog .card-hdr{padding:18px 22px;background:var(--fb-soft);border-bottom:1px solid var(--fb-accent)}#fb-dialog h2{font-size:24px;margin:0}#fb-dialog .dlg-body{padding:22px}#fb-dialog .sec-lbl{display:block;font-weight:600;margin:12px 0 6px}#fb-dialog .stars{display:flex;direction:rtl;gap:5px}#fb-dialog .star{border:0;background:transparent;color:#777;font-size:34px;min-width:44px;min-height:44px;cursor:pointer;padding:2px}#fb-dialog .star.on{color:var(--fb-accent)}#fb-dialog .rating-lbl{min-height:26px;color:var(--fb-accent)}#fb-dialog .txt-input{box-sizing:border-box;width:100%;padding:10px;border:1px solid #888;border-radius:8px;background:var(--fb-paper,#fff);color:inherit;font:inherit}#fb-dialog textarea{resize:vertical;min-height:100px}#fb-dialog .dlg-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}#fb-dialog .go-btn,#fb-dialog .close-btn,#fb-dialog .ghost-btn,.feedback-open{font-size:15px;font-weight:600;font-family:inherit;line-height:1.5;min-height:44px;padding:10px 18px;border:1px solid var(--fb-accent);border-radius:var(--fb-radius,18px);cursor:pointer;background:var(--fb-accent);color:white}#fb-dialog .ghost-btn,.feedback-open{background:var(--fb-soft);color:var(--fb-accent)}#fb-dialog :focus-visible,.feedback-open:focus-visible{outline:3px solid var(--fb-accent);outline-offset:3px}#fb-dialog .fb-status.err{color:#a32020}#fb-dialog .fb-status{min-height:24px}#fb-dialog button:disabled{opacity:.6;cursor:wait}#fb-dialog .fb-note{font-size:13px;color:inherit;opacity:.8}#fb-dialog .thanks{text-align:center}.feedback-area{padding:16px;text-align:center}.feedback-open{font-family:inherit}@media print{.feedback-area,#fb-dialog{display:none!important}}\n'

def page(title,body,depth=0):
    pre='../'*depth
    return f'''<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} | תאוריית המוזיקה הפתוחה</title><meta name="description" content="ספר תאוריית מוזיקה פתוח בעברית: קריאה בפרקים, מילון מונחים, PDF וספר שמע."><link rel="icon" href="{pre}art/icon.png" type="image/png" sizes="128x128"><link rel="stylesheet" href="{pre}style.css"><script defer src="{pre}app.js"></script></head><body data-prefix="{pre}" data-feedback-tool="תאוריית המוזיקה הפתוחה"><a class="skip" href="#main">דלג לתוכן</a><header><div class="wrap header-inner"><a class="brand" href="{pre}index.html">תאוריית המוזיקה הפתוחה<small>OPEN MUSIC THEORY · המהדורה העברית</small></a><nav class="nav" aria-label="ניווט ראשי"><a href="{pre}contents.html">הספר</a><a href="{pre}index.html#downloads">הורדות</a><a class="source-nav" href="{pre}docs/translation-policy-and-glossary.html">מילון ומדיניות</a><a class="top-nav-action" href="https://openmusictools.github.io/">דף הבית של כלי מוזיקה פתוחים</a><button class="top-nav-action" type="button" data-open-feedback>משוב</button><span class="beta">בטא</span></nav></div></header>{body}<footer class="footer"><div class="wrap footer-inner"><div>מהדורה עברית עצמאית בסיוע AI · ביקורת מקצועית אנושית טרם הושלמה.<br>מקור: Kris Shaffer, Bryn Hughes, Brian Moseley; עריכה: Kris Shaffer ו־Robin Wharton; Hybrid Pedagogy Publishing.<br>טקסט הספר: <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY–SA 4.0</a>; נכסי המקור לפי הרישיון המצוין בהם. איורי האתר המופשטים: CC0.</div><div><a href="https://openmusictheory.github.io/">המקור באנגלית</a> · <a href="https://github.com/{SOURCE_REPO}">מאגר התרגום</a><br><a href="https://github.com/{REPO}/issues/new">דיווח על טעות</a> · <a data-release-link href="https://github.com/{REPO}/releases">כל המהדורות</a></div></div></footer>{FEEDBACK_HTML}<style>{FEEDBACK_CSS}</style><script>{FEEDBACK_JS}</script></body></html>'''

def build_site(source,out,release_file):
    files=[source/p for p in subprocess.check_output(['git','ls-files','-z'],cwd=source).decode().split('\0') if p]
    docs=[p for p in files if p.suffix=='.md']
    docset={p.resolve() for p in docs}
    titles={}
    for p in docs:
        m,b=meta(p)
        heading=BeautifulSoup(markdown.markdown(b),'html.parser').find('h1')
        titles[p.resolve()]=str(m.get('title') or (heading.get_text() if heading else p.stem))
    toc_soup=BeautifulSoup(markdown.markdown(meta(source/'contents.md')[1],extensions=['tables']),'html.parser')
    groups={};order=[];group='המהדורה העברית'
    for node in toc_soup.find_all(['h2','a']):
        if node.name=='h2':group=node.get_text();continue
        path=unquote(urlsplit(node.get('href','')).path)
        if path.endswith('.html'):
            p=(source/(path[:-5]+'.md')).resolve()
            if p in docset and meta(p)[0].get('translation_status') in {'language-reviewed','completed'} and p not in order:
                groups.setdefault(group,[]).append(p);order.append(p)
    for p in docs:
        p=p.resolve()
        if p not in order and meta(p)[0].get('translation_status') in {'language-reviewed','completed'}:
            groups.setdefault('פרקים נוספים ודפי עזר',[]).append(p);order.append(p)
    paths={p.resolve():p.relative_to(source).with_suffix('.html').as_posix() for p in docs}
    missing=[];fallbacks=[];search=[];rendered={}
    for p in docs:
        p=p.resolve();m,body=meta(p)
        body=re.sub(r'\{\{\s*page\.title\s*\}\}\s*\n[=]+\s*\n','',body)
        body=re.sub(r'\{\{\s*site\.(?:url|baseurl)\s*\}\}','',body)
        soup=BeautifulSoup(markdown.markdown(body,extensions=['tables','fenced_code','footnotes','toc','attr_list']),'html.parser')
        for t in soup.find_all(['script','style']):t.decompose()
        for t in soup.find_all(True):
            for a in list(t.attrs):
                if a.lower().startswith('on') or a in {'style','srcdoc'}:del t[a]
        for t in list(soup.find_all(['iframe','object','embed','video'])):
            u=t.get('src') or t.get('data') or ''
            if not u and t.find('source'):u=t.find('source').get('src','')
            div=soup.new_tag('div',attrs={'class':'media-link'});div.append('דוגמה מקוונת / תרגיל אינטראקטיבי: ')
            if u.startswith('//'):u='https:'+u
            if u.startswith('http://'):u='https://'+u[7:]
            if u.startswith('https://'):
                a=soup.new_tag('a',href=u,target='_blank',rel='noopener noreferrer');a.string='פתיחת הדוגמה באתר המקור';div.append(a)
            else:div.append('הדוגמה זמינה דרך מאגר המקור.')
            t.replace_with(div)
        depth=len(Path(paths[p]).parts)-1
        for t in soup.find_all(True):
            attr='href' if t.name=='a' else 'src' if t.name in {'img','audio','source'} else None
            if not attr or not t.get(attr):continue
            u=html.unescape(t[attr]);parts=urlsplit(u)
            if u.rstrip('/') in {'https://openmusictheory.github.io','https://openmusictheory.com','http://openmusictheory.com'}:continue
            if u.startswith('#'):continue
            for base in ('https://openmusictheory.github.io/','http://openmusictheory.com/','https://openmusictheory.com/','https://open-music-theory-he.github.io/open-music-theory-hebrew/'):
                if u.startswith(base):u='/'+u[len(base):];parts=urlsplit(u);break
            if parts.scheme or parts.netloc:
                if parts.scheme not in {'http','https','mailto'}:t.attrs.pop(attr,None)
                elif t.name=='a':t['rel']='noopener noreferrer'
                continue
            target=((source/unquote(parts.path).lstrip('/')) if parts.path.startswith('/') else (p.parent/unquote(parts.path))).resolve()
            if target.suffix=='.html':target=target.with_suffix('.md')
            if target in docset:
                t[attr]=relative(depth,paths[target])+('#'+parts.fragment if parts.fragment else '')
            elif target.is_file() and target.is_relative_to(source):
                rel=target.relative_to(source).as_posix()
                if target.suffix.lower() in MEDIA:t[attr]=relative(depth,rel)
                else:t[attr]='https://github.com/'+SOURCE_REPO+'/blob/'+subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()+'/'+quote(rel)
            elif t.name=='img':
                note=soup.new_tag('p',attrs={'class':'notice'});note.string='איור חסר במאגר המקור: '+(t.get('alt') or Path(parts.path).name);t.replace_with(note);missing.append({'page':paths[p],'resource':u})
            else:
                t[attr]='https://openmusictheory.github.io/'+parts.path.lstrip('/')+('#'+parts.fragment if parts.fragment else '')
                missing.append({'page':paths[p],'resource':u})
        for t in soup.find_all(['strong','em','code']):
            if not re.search('[א-ת]',t.get_text()):t['dir']='ltr'
        if p.name=='schemataSummary.md':
            for t in soup.find_all('table'):t['dir']='ltr'
        if m.get('title') and soup.find('h1') and soup.find('h1').get_text()==titles[p]:soup.find('h1').decompose()
        rendered[p]=soup
    # Keep legacy fragment links within the correct chapter, documenting fallback.
    for p,soup in rendered.items():
        depth=len(Path(paths[p]).parts)-1
        for a in soup.find_all('a',href=True):
            u=a['href'];parts=urlsplit(u)
            if parts.scheme or parts.netloc or not parts.fragment:continue
            dest=p if not parts.path else (source/Path(paths[p]).parent/unquote(parts.path)).resolve().with_suffix('.md')
            if dest in rendered and not rendered[dest].find(id=parts.fragment):
                fallbacks.append({'page':paths[p],'original':u});a['href']=u.split('#')[0] or '#main'
    for p,soup in rendered.items():
        depth=len(Path(paths[p]).parts)-1;pre='../'*depth
        sidebar='<aside class="sidebar" aria-label="פרקי הספר"><button class="sidebar-toggle" data-sidebar aria-expanded="false">תוכן העניינים ▾</button>'
        for name,items in groups.items():
            sidebar+=f'<details {"open" if p in items else ""}><summary>{html.escape(name)}</summary>'
            for item in items:sidebar+=f'<a class="{"current" if item==p else ""}" href="{pre}{paths[item]}" {"aria-current=page" if item==p else ""}>{html.escape(titles[item])}</a>'
            sidebar+='</details>'
        sidebar+='</aside>'
        chapter_nav=''
        if p in order:
            n=order.index(p)
            for label,j in [('הפרק הקודם',n-1),('הפרק הבא',n+1)]:
                if 0<=j<len(order):chapter_nav+=f'<a href="{pre}{paths[order[j]]}"><small>{label}</small>{html.escape(titles[order[j]])}</a>'
        group=next((name for name,items in groups.items() if p in items),'תיעוד המהדורה')
        body=f'<main id="main" class="wrap reader">{sidebar}<article class="chapter"><div class="chapter-head"><span class="eyebrow">{html.escape(group)}</span><h1>{html.escape(titles[p])}</h1><div class="chapter-tools"><span>מהדורה עברית · בטא</span><button data-size="1" aria-label="הגדלת גודל הכתב">א+</button><button data-size="-1" aria-label="הקטנת גודל הכתב">א−</button><button data-theme>בהיר / כהה</button></div></div><div class="search-block"><label for="chapter-search">חיפוש בספר</label><input id="chapter-search" class="search" data-search placeholder="מושג, פרק או ביטוי…" autocomplete="off"><div class="search-results" aria-live="polite"></div></div><div class="prose">{soup}</div><div class="chapter-nav">{chapter_nav}</div><p class="source-line"><a href="https://github.com/{SOURCE_REPO}/blob/master/{quote(p.relative_to(source).as_posix())}">תוכן הפרק במאגר התרגום</a> · <a href="https://github.com/{REPO}/issues/new?title={quote(titles[p])}">דיווח על טעות בפרק</a></p></article></main>'
        if p.name=='contents.md':body=f'<main id="main" class="wrap section"><div class="section-title"><h1>תוכן העניינים</h1><p>126 עמודי תוכן · המהדורה העברית</p></div><div class="prose full-toc">{soup}</div></main>'
        write(out/paths[p],page(titles[p],body,depth))
        search.append({'title':titles[p],'text':soup.get_text(' ',strip=True),'path':paths[p],'group':group})
    for p in files:
        if p.suffix.lower() in MEDIA:
            dest=out/p.relative_to(source);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
    cards=''.join(f'<a class="download-card" data-download="{key}" href="https://github.com/{REPO}/releases"><span class="format">{"PDF" if key=="pdf" else "ZIP"} <span class="size"></span></span><strong>{label} ↙</strong><small>{desc}</small></a>' for key,label,desc in LABELS)
    topics=''
    for name,items in groups.items():
        topics+=f'<div class="topic"><h3>{html.escape(name)}</h3>'+''.join(f'<a href="{paths[p]}">{html.escape(titles[p])}</a>' for p in items[:4])+f'<a class="more" href="contents.html">לכל הפרקים · {len(items)} ←</a></div>'
    body=f'''<main id="main"><div class="wrap"><section class="hero"><div><span class="eyebrow">ללמוד · להקשיב · להבין</span><h1>תאוריית המוזיקה<span>בשפה שלכם.</span></h1><p>הספר הפתוח ללימוד מוזיקה, עכשיו בעברית. מהיסודות וההרמוניה ועד צורה, קונטרפונקט וניתוח מוזיקלי.</p><div class="actions"><a class="button" href="hebrew-introduction.html">מתחילים לקרוא ←</a><a class="button secondary" href="#downloads">מורידים ולומדים</a></div></div><div class="hero-art"><img src="art/resonance.svg" width="620" height="650" alt="איור מופשט של גלים וקשתות בצבעי ירוק וזהב, הממחיש תהודה וקצב"><div class="art-caption"><span>תהודה, קצב ותנועה</span><span>איור מקורי · CC0</span></div></div></section><div class="intro-line"><span>126 עמודי תוכן בעברית</span><span>קריאה חופשית · בלי הרשמה</span><span>מבוסס על Open Music Theory, גרסה 1</span></div><section class="section"><div class="section-title"><h2>מה תרצו ללמוד היום?</h2><p>לפי הסדר, או ישר אל הנושא שמעניין אתכם.</p></div><div class="search-block"><label for="book-search">חיפוש בספר</label><input id="book-search" class="search" data-search placeholder="למשל: סולמות, קדנצה, דו יחסי…" autocomplete="off"><div class="search-results" aria-live="polite"></div></div><div class="catalog">{topics}</div></section><p class="notice"><strong>זו מהדורת בטא.</strong> התרגום נוצר ונבדק בסיוע בינה מלאכותית, וטרם עבר הגהה מקצועית אנושית מלאה. כיתובים בתוך תמונות וחלק מהנספחים נשארו באנגלית. ספר השמע חלקי.</p></div><section id="downloads" class="section downloads"><div class="wrap"><div class="section-title"><h2>הספר, גם מחוץ לדפדפן</h2><p>בחרו את החבילה שמתאימה לכם.</p></div><p class="release-line"><span data-release>המהדורה הזמינה להורדה</span> · <a data-release-link href="https://github.com/{REPO}/releases">פרטי המהדורה וכל הגרסאות</a></p><div class="download-grid">{cards}</div><p class="release-line">ספר השמע כולל רק פרקים שכבר הוקלטו. מספרם המדויק מופיע בפרטי המהדורה. הדוגמאות והתרגילים המקוונים דורשים חיבור לאינטרנט.</p></div></section><section class="wrap section about-grid"><div><span class="eyebrow">המהדורה העברית</span><h3>אותו ידע, הקשר מקומי.</h3><p>לצד התרגום נוספו הקדמה ומדריך לדו קבוע ולדו נייד. שמות התווים נכתבים באותיות ABC, ומונחים מוזיקליים נשמרים בהתאם למדיניות התרגום.</p><a href="fixed-and-movable-do.html">להבנת דו קבוע ודו נייד ←</a></div><div><img src="art/rhythm.svg" width="680" height="220" loading="lazy" alt="רצף מופשט של עיגולים וגלי קול, ללא כלי נגינה"><h3>ספר פתוח, עבודה שקופה.</h3><p>המקור, מילון המונחים והערות התרגום זמינים לעיון. אפשר לדווח על טעות ולעזור לשפר את המהדורה.</p><a href="docs/translation-notes.html">הערות התרגום</a> · <a href="docs/translation-policy-and-glossary.html">מדיניות ומילון מונחים</a></div></section></main>'''
    write(out/'index.html',page('הספר הפתוח בעברית',body))
    write(out/'style.css',CSS + '.nav{flex-wrap:wrap;gap:16px}.nav .top-nav-action{border:0;background:transparent;color:var(--accent);font:inherit;font-size:15px;min-height:44px;padding:10px 0;text-decoration:none;cursor:pointer}.header-inner{flex-wrap:wrap;padding-block:12px}@media(max-width:900px){.nav{justify-content:center}.nav .top-nav-action{font-size:13px}}');write(out/'app.js',JS);write(out/'search.json',json.dumps(search,ensure_ascii=False))
    write(out/'.nojekyll','')
    if release_file and release_file.exists():shutil.copyfile(release_file,out/'release.json')
    else:write(out/'release.json','{}')
    wave=''.join(f'<path d="M {x} 600 C {x-90} 440 {x+155} 275 {x+10} 80"/>' for x in range(130,560,28))
    write(out/'art/resonance.svg',f'<svg xmlns="http://www.w3.org/2000/svg" width="620" height="650" viewBox="0 0 620 650"><title>תהודה — איור מקורי CC0</title><defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#d8e3cd"/><stop offset="1" stop-color="#eee3c3"/></linearGradient></defs><rect width="620" height="650" fill="url(#bg)"/><circle cx="155" cy="178" r="75" fill="#e3b25b"/><g fill="none" stroke="#276850" stroke-width="2" opacity=".8">{wave}</g><circle cx="437" cy="474" r="108" fill="#254f40"/><g fill="none" stroke="#f2d294" stroke-width="1.4">'+''.join(f'<circle cx="437" cy="474" r="{r}"/>' for r in range(20,101,11))+'</g><path d="M0 540 Q150 450 290 610" fill="none" stroke="#d09b47" stroke-width="34"/></svg>')
    write(out/'art/rhythm.svg','<svg xmlns="http://www.w3.org/2000/svg" width="680" height="220" viewBox="0 0 680 220"><title>קצב — איור מקורי CC0</title><rect width="680" height="220" fill="#dce6d3"/>'+''.join(f'<circle cx="{x}" cy="110" r="{r}" fill="{c}"/>' for x,r,c in [(80,45,'#25634a'),(190,28,'#e7b762'),(270,20,'#25634a'),(355,40,'#e7b762'),(475,55,'#25634a'),(595,32,'#e7b762')])+'<path d="M0 150 Q85 50 170 150 T340 150 T510 150 T680 150" stroke="#fff8e8" stroke-width="3" fill="none"/></svg>')
    write(out/'art/icon.svg','<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#21684f"/><path d="M8 32 Q20 7 32 32 T56 32" stroke="#efd09a" stroke-width="5" fill="none"/></svg>')
    (out/'art/icon.png').write_bytes(base64.b64decode('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'))
    write(out/'art/LICENSE.txt','Original abstract SVG artwork by contributors to the Hebrew edition. Dedicated to the public domain under CC0 1.0: https://creativecommons.org/publicdomain/zero/1.0/\n')
    write(out/'build-report.json',json.dumps({'chapters':len(order),'pages':len(docs),'known_missing_resources':missing,'legacy_fragment_fallbacks':fallbacks},ensure_ascii=False,indent=2))
    optimize_search(out)
    # Validate every local href/src and all retained internal fragments.
    problems=[]
    for p in out.rglob('*.html'):
        soup=BeautifulSoup(p.read_text(),'html.parser')
        for t in soup.find_all(True):
            u=t.get('href') or t.get('src')
            if not u:continue
            parts=urlsplit(u)
            if parts.scheme or parts.netloc:continue
            dest=(p.parent/unquote(parts.path)).resolve() if parts.path else p
            if not dest.is_file():problems.append(str(p)+': '+u)
            elif parts.fragment and dest.suffix=='.html' and not BeautifulSoup(dest.read_text(),'html.parser').find(id=parts.fragment):problems.append(str(p)+': missing fragment '+u)
    if problems:raise RuntimeError('\n'.join(problems))
    print('Site validated:',len(docs),'pages;',len(order),'content chapters')


def optimize_search(out):
    """Static per-page metadata and canonical sitemap; no content rewriting."""
    base = 'https://openmusictools.github.io/open-music-theory-hebrew/'
    urls = []
    for file in sorted(out.rglob('*.html')):
        soup = BeautifulSoup(file.read_text(), 'html.parser')
        if not soup.head:
            continue
        path = file.relative_to(out).as_posix()
        url = base + ('' if path == 'index.html' else quote(path, safe='/'))
        if path == '404.html':
            soup.head.append(soup.new_tag('meta', attrs={'name':'robots','content':'noindex'}))
        else:
            urls.append(url)
        title = soup.title.get_text()
        prose = soup.select_one('.prose')
        paragraphs = prose.find_all('p') if prose else []
        summary = next((node.get_text(' ', strip=True) for node in paragraphs if len(node.get_text()) > 45), '')
        if summary:
            description = title.split(' | ')[0] + ': ' + re.sub(r'\s+', ' ', summary)[:170]
        elif path == 'index.html':
            description = 'ספר תאוריית המוזיקה הפתוחה בעברית: יסודות, הרמוניה, קונטרפונקט וניתוח מוזיקלי. קריאה חופשית, PDF, נספחים וספר שמע חלקי. מהדורת בטא בסיוע AI.'
        else:
            description = title.split(' | ')[0] + ' — קריאה במהדורה העברית של תאוריית המוזיקה הפתוחה, עם דוגמאות ותיעוד התרגום.'
        soup.head.find('meta', attrs={'name':'description'})['content'] = description
        canon = soup.new_tag('link', rel='canonical', href=url); soup.head.append(canon)
        for key, value in [('og:title',title), ('og:description',description), ('og:url',url), ('og:type','website'), ('og:locale','he_IL')]:
            soup.head.append(soup.new_tag('meta', attrs={'property':key,'content':value}))
        # JSON-LD describes the actual page; no invented reviews or endorsements.
        schema = {'@context':'https://schema.org','@type':'WebPage','name':title,'url':url,'inLanguage':'he','description':description,
                  'isPartOf':{'@type':'WebSite','name':'תאוריית המוזיקה הפתוחה בעברית','url':base}}
        structured = soup.new_tag('script', type='application/ld+json')
        structured.string = json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c')
        soup.head.append(structured)
        # Keep the generated body exactly intact; only replace the head.
        original = file.read_text()
        a = original.index('<head>'); b = original.index('</head>') + len('</head>')
        write(file, original[:a]+str(soup.head)+original[b:])
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    xml += ''.join('<url><loc>'+html.escape(url)+'</loc></url>' for url in urls) + '</urlset>\n'
    write(out/'sitemap.xml', xml)

def release_packages(source,out,tag):
    out.mkdir(parents=True,exist_ok=True)
    exp=source/'dist/export';audio=source/'dist/audiobook';state=source/'dist/audiobook-state'
    report=json.loads((audio/'progress.json').read_text())
    if report['requests_this_run']!=0 or report['status']!='tags_updated':raise RuntimeError('Export must reuse existing audio')
    completed=[c for c in report['chapters'] if c['status']=='generated']
    for c in completed:
        if hashlib.sha256((audio/'chapters'/c['filename']).read_bytes()).hexdigest()!=c['sha256']:raise RuntimeError('Audio checksum mismatch')
    m=json.loads((exp/'export-manifest.json').read_text())
    pdf=out/ASSETS['pdf'];shutil.copyfile(exp/'open-music-theory-static.pdf',pdf)
    companions={}
    for f in m['files']:
        p=source/f['path']
        if p.suffix.lower() in MEDIA:companions['נספחים/'+f['hebrew_filename']]=p
    companions['נספחים/external-media-links.txt']=None
    audiofiles={}
    for p in audio.rglob('*'):
        if p.is_file() and p.suffix!='.zip':audiofiles['ספר-שמע/'+p.relative_to(audio).as_posix()]=p
    common={'קראו-אותי.txt':f'תאוריית המוזיקה הפתוחה — מהדורה עברית {tag}\nמקור: Open Music Theory v1, CC BY-SA 4.0. קרדיטים ורישיונות פרטניים נשמרים בחומרי המקור.\nתרגום בסיוע AI, טרם הושלמה הגהה מקצועית עצמאית. תמונות ונספחים נשמרים גם בשפת המקור.\nספר השמע חלקי: {len(completed)}/{len(report["chapters"])} פרקים שלמים. אין הפקת שמע בריצת הפרסום.\nאתר הקריאה: https://openmusictools.github.io/open-music-theory-hebrew/\nמאגר התרגום: https://github.com/{SOURCE_REPO}\nחבילות הפלט מכילות PDF, מדיה, נספחים ותמלילי שמע; אינן כוללות קוד, Markdown, תווי מקור או גיבויי עבודה.\n'}
    external='\n'.join(m['external_references'])+'\n'
    def archive(key,mapping):
        with zipfile.ZipFile(out/ASSETS[key],'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for name,p in sorted(mapping.items()):
                if p is not None:z.write(p,name)
                else:z.writestr(name,external)
            for n,t in common.items():z.writestr(n,t)
        with zipfile.ZipFile(out/ASSETS[key]) as z:
            if z.testzip():raise RuntimeError('ZIP corruption')
    pdfmap={'תאוריית-המוזיקה-הפתוחה.pdf':pdf}
    archive('pdf-annexes',{**pdfmap,**companions})
    archive('audio',audiofiles)
    archive('audio-annexes',{**audiofiles,**companions})
    outputs={**pdfmap,**audiofiles,**companions}
    archive('everything',outputs)
    allfiles=dict(outputs)
    for p in subprocess.check_output(['git','ls-files','-z'],cwd=source).decode().split('\0'):
        if p:allfiles['קבצי-מקור/'+p]=source/p
    for p in state.rglob('*'):
        if p.is_file() and p.name not in {'.git','.gitignore','concat.txt','working.wav','working.mp3'} and not p.name.endswith('.tmp'):allfiles['תיעוד-ומקטעי-שמע/'+p.relative_to(state).as_posix()]=p
    for name in ('publish.py','README.md','.github/workflows/publish.yml'):
        p=Path(__file__).parent/name
        if p.is_file():allfiles['קוד-אתר/'+name]=p
    archive('sources',allfiles)
    manifest={'tag':tag,'source_commit':m['commit'],'audio_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=state,text=True).strip(),'complete_audio_chapters':len(completed),'eligible_audio_chapters':len(report['chapters']),'synthesis_requests':0,'assets':[]}
    for key,name in ASSETS.items():manifest['assets'].append({'kind':key,'name':name,'bytes':(out/name).stat().st_size,'sha256':hashlib.sha256((out/name).read_bytes()).hexdigest()})
    write(out/'release-manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    notes=f'''מהדורת בטא ראשונה של תאוריית המוזיקה הפתוחה בעברית, המבוססת על Open Music Theory גרסה 1.

כל 124 עמודי התוכן והעזר המקוריים תורגמו ונבדקו בסיוע AI; נוספו שני פרקי פתיחה בעברית. הגהה מקצועית אנושית טרם הושלמה. כיתובים בתמונות וחלק מהנספחים נותרו באנגלית; דוגמאות מקוונות נשמרות כקישורים. איור אחד חסר במאגר המקור ומתועד בדוחות.

ספר השמע: **{len(completed)} מתוך {len(report['chapters'])} פרקים שלמים**. בריצה זו נעשה שימוש בהקלטות קיימות בלבד, ללא יצירה מחדש וללא שימוש במכסת Google.

| קובץ | תוכן |
|---|---|
'''+''.join(f'| {ASSETS[k]} | {label} — {desc} |\n' for k,label,desc in LABELS)+f'''
ה־PDF הוא היצוא הסטטי המלא: כולל המסמכים המשולבים בעקבות הפרקים ותיעוד המהדורה. חבילות הנספחים מוסיפות את קובצי המדיה והמסמכים בנפרד. חבילת הפלטים אינה כוללת קבצי עריכה וקוד; חבילת המקור כוללת גם אותם ואת כל מצב השמע השמור.

מקור הטקסט: `{m['commit']}`. מקור השמע: `{manifest['audio_commit']}`. חתימות SHA256 וגודל כל הורדה: release-manifest.json.

טקסט הספר ברישיון CC BY-SA 4.0; רישיונות פרטניים נשמרים. זו מהדורה עצמאית ואינה מוצגת כתרגום רשמי המאושר בידי מחברי המקור.

[אתר הספר](https://openmusictools.github.io/open-music-theory-hebrew/) · [מאגר התרגום](https://github.com/{SOURCE_REPO}) · [דיווח על טעות](https://github.com/{REPO}/issues)
'''
    write(out/'release-notes.md',notes)
    print(json.dumps(manifest,ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['site','packages']);parser.add_argument('--source',type=Path,default=Path('source'));parser.add_argument('--output',type=Path);parser.add_argument('--release',type=Path);parser.add_argument('--tag',default='v0.1.0-beta.1');args=parser.parse_args()
    source=args.source.resolve()
    if args.mode=='site':build_site(source,(args.output or Path('_site')).resolve(),args.release)
    else:release_packages(source,(args.output or Path('release-assets')).resolve(),args.tag)
