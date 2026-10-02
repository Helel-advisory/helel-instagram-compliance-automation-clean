import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse

app = FastAPI(title=os.getenv('APP_NAME', 'HELEL Instagram Compliance Automation'))
security = HTTPBasic()


def reviewer(c: HTTPBasicCredentials = Depends(security)):
    if not os.getenv('ADMIN_USERNAME') or not os.getenv('ADMIN_PASSWORD'):
        raise HTTPException(503, 'Reviewer credentials are not configured')
    if c.username != os.getenv('ADMIN_USERNAME') or c.password != os.getenv('ADMIN_PASSWORD'):
        raise HTTPException(401, 'Invalid reviewer credentials', headers={'WWW-Authenticate': 'Basic'})
    return c.username


@app.get('/', response_class=HTMLResponse)
def home():
    return '''<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="HELEL Instagram compliance content review and publishing automation."><title>HELEL Instagram Compliance Automation</title><style>body{margin:0;background:#0d0b12;color:#f4f0f7;font-family:system-ui,-apple-system,sans-serif;display:grid;place-items:center;min-height:100vh}.card{max-width:620px;margin:24px;padding:34px;border:1px solid #4b3b61;border-radius:18px;background:linear-gradient(145deg,#17121f,#0b0a0e);box-shadow:0 18px 60px #0008}h1{letter-spacing:.02em}p{color:#c9bfd2;line-height:1.6}a{color:#caa8ff;text-decoration:none;margin-right:18px}</style></head><body><main class="card"><h1>HELEL Compliance Content Automation</h1><p>Secure review workflow for compliance-focused Instagram content. The service is online and ready for the next content-generation integration.</p><p><a href="/health">Health</a><a href="/docs">API docs</a><a href="/dashboard">Reviewer dashboard</a></p></main></body></html>'''


@app.get('/health')
def health():
    return {'status': 'ok', 'service': app.title}


@app.get('/dashboard', response_class=HTMLResponse)
def dashboard(_: str = Depends(reviewer)):
    return '<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>HELEL Review</title></head><body><h1>HELEL Compliance Review</h1><p>Service is online. Content queue is ready for the next implementation stage.</p></body></html>'


@app.get('/content')
def content(_: str = Depends(reviewer)):
    return []
