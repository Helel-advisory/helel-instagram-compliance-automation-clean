import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title=os.getenv('APP_NAME', 'HELEL Instagram Compliance Automation'))
security = HTTPBasic()

class ContentUpdate(BaseModel):
    caption: str
    description: str
    cta: str = ''
    hashtags: str

contents = [{
    'id': 1,
    'topic': 'Compliance awareness',
    'caption': '',
    'description': '',
    'cta': '',
    'hashtags': '',
    'status': 'draft'
}]

def reviewer(c: HTTPBasicCredentials = Depends(security)):
    if not os.getenv('ADMIN_USERNAME') or not os.getenv('ADMIN_PASSWORD'):
        raise HTTPException(503, 'Reviewer credentials are not configured')
    if c.username != os.getenv('ADMIN_USERNAME') or c.password != os.getenv('ADMIN_PASSWORD'):
        raise HTTPException(401, 'Invalid reviewer credentials', headers={'WWW-Authenticate': 'Basic'})
    return c.username

def valid_tags(value: str):
    tags = [x for x in value.replace(',', ' ').split() if x]
    return len(tags) == 5 and all(x.startswith('#') and len(x) > 1 for x in tags)

@app.get('/', response_class=HTMLResponse)
def home():
    return '''<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="HELEL Instagram compliance content review and publishing automation."><title>HELEL Instagram Compliance Automation</title><style>body{margin:0;background:#0d0b12;color:#f4f0f7;font-family:system-ui;display:grid;place-items:center;min-height:100vh}.card{max-width:620px;margin:24px;padding:34px;border:1px solid #4b3b61;border-radius:18px;background:linear-gradient(145deg,#17121f,#0b0a0e)}p{color:#c9bfd2;line-height:1.6}a{color:#caa8ff;text-decoration:none;margin-right:18px}</style></head><body><main class="card"><h1>HELEL Compliance Content Automation</h1><p>Secure review workflow for compliance-focused Instagram content.</p><p><a href="/health">Health</a><a href="/docs">API docs</a><a href="/dashboard">Reviewer dashboard</a></p></main></body></html>'''

@app.get('/health')
def health():
    return {'status': 'ok', 'service': app.title}

@app.get('/dashboard', response_class=HTMLResponse)
def dashboard(_: str = Depends(reviewer)):
    return '''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>HELEL Review</title><style>body{margin:0;background:#0d0b12;color:#f4f0f7;font-family:system-ui}main{max-width:760px;margin:24px auto;padding:24px}label{display:block;margin-top:16px;color:#c9bfd2}textarea,input{box-sizing:border-box;width:100%;margin-top:6px;padding:12px;border:1px solid #4b3b61;border-radius:10px;background:#17121f;color:#fff;font:inherit}textarea{min-height:90px}button{margin:18px 8px 0 0;padding:11px 18px;border:0;border-radius:10px;background:#a978e8;color:#fff;font-weight:700}#msg{color:#caa8ff}</style></head><body><main><h1>HELEL Content Review</h1><p>Edit every field before approval. Hashtags must be exactly five.</p><label>Caption<textarea id="caption"></textarea></label><label>Description<textarea id="description"></textarea></label><label>Call to action<input id="cta"></label><label>Hashtags (exactly five, inline)<input id="hashtags" placeholder="#AML #CFT #KYC #Sanctions #Compliance"></label><button onclick="save()">Save draft</button><button onclick="approve()">Approve</button><button onclick="reject()">Reject</button><p id="msg"></p></main><script>const msg=document.getElementById('msg');async function load(){const r=await fetch('/content');const d=(await r.json())[0];for(const k of ['caption','description','cta','hashtags'])document.getElementById(k).value=d[k]||''}async function save(){const body={caption:caption.value,description:description.value,cta:cta.value,hashtags:hashtags.value};const r=await fetch('/content/1',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});msg.textContent=(await r.json()).detail||'Draft saved'}async function approve(){await save();const r=await fetch('/content/1/approve',{method:'POST'});msg.textContent=(await r.json()).message||'Approved'}async function reject(){const r=await fetch('/content/1/reject',{method:'POST'});msg.textContent=(await r.json()).message||'Rejected'}load()</script></body></html>'''

@app.get('/content')
def content(_: str = Depends(reviewer)):
    return contents

@app.put('/content/{content_id}')
def update_content(content_id: int, update: ContentUpdate, _: str = Depends(reviewer)):
    if not valid_tags(update.hashtags):
        raise HTTPException(422, 'Enter exactly five hashtags, each beginning with #')
    item = next((x for x in contents if x['id'] == content_id), None)
    if not item:
        raise HTTPException(404, 'Content not found')
    item.update(update.model_dump())
    item['status'] = 'draft'
    return {'message': 'Draft saved', 'content': item}

@app.post('/content/{content_id}/approve')
def approve(content_id: int, _: str = Depends(reviewer)):
    item = next((x for x in contents if x['id'] == content_id), None)
    if not item:
        raise HTTPException(404, 'Content not found')
    if not valid_tags(item['hashtags']):
        raise HTTPException(422, 'Exactly five hashtags are required before approval')
    item['status'] = 'approved'
    return {'message': 'Approved for publishing', 'content': item}

@app.post('/content/{content_id}/reject')
def reject(content_id: int, _: str = Depends(reviewer)):
    item = next((x for x in contents if x['id'] == content_id), None)
    if not item:
        raise HTTPException(404, 'Content not found')
    item['status'] = 'rejected'
    return {'message': 'Rejected and held from publishing', 'content': item}


@app.get('/media/{content_id}.png')
def branded_media(content_id: int, _: str = Depends(reviewer)):
    item = next((x for x in contents if x['id'] == content_id), None)
    if not item:
        raise HTTPException(404, 'Content not found')

    import io
    from PIL import Image, ImageDraw, ImageFont
    from fastapi.responses import Response

    image = Image.new('RGB', (1080, 1080), '#07080a')
    draw = ImageDraw.Draw(image)

    try:
        title_font = ImageFont.truetype('DejaVuSans-Bold.ttf', 58)
        body_font = ImageFont.truetype('DejaVuSans.ttf', 30)
    except OSError:
        title_font = body_font = ImageFont.load_default()

    draw.rounded_rectangle(
        (45, 45, 1035, 1035),
        radius=32,
        outline='#7c3aed',
        width=5,
    )
    draw.text((85, 95), 'HELEL ADVISORY', fill='#d1d5db', font=title_font)
    draw.text((85, 205), 'COMPLIANCE UPDATE', fill='#a78bfa', font=body_font)
    draw.multiline_text(
        (85, 350),
        item['topic'],
        fill='#ffffff',
        font=title_font,
        spacing=16,
        width=880,
    )
    draw.text(
        (85, 900),
        'Public-source education - Review required',
        fill='#d1d5db',
        font=body_font,
    )

    output = io.BytesIO()
    image.save(output, format='PNG', optimize=True)

    return Response(
        output.getvalue(),
        media_type='image/png',
        headers={'Cache-Control': 'no-store'},
    )
