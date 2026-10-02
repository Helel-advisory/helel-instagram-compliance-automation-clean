import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse

app = FastAPI(title=os.getenv('APP_NAME','HELEL Instagram Compliance Automation'))
security = HTTPBasic()

def reviewer(c: HTTPBasicCredentials = Depends(security)):
    if not os.getenv('ADMIN_USERNAME') or not os.getenv('ADMIN_PASSWORD'):
        raise HTTPException(503, 'Reviewer credentials are not configured')
    if c.username != os.getenv('ADMIN_USERNAME') or c.password != os.getenv('ADMIN_PASSWORD'):
        raise HTTPException(401, 'Invalid reviewer credentials', headers={'WWW-Authenticate':'Basic'})
    return c.username

@app.get('/health')
def health():
    return {'status':'ok','service':app.title}

@app.get('/dashboard', response_class=HTMLResponse)
def dashboard(_: str = Depends(reviewer)):
    return '<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>HELEL Review</title></head><body><h1>HELEL Compliance Review</h1><p>Service is online. Content queue is ready for the next implementation stage.</p></body></html>'

@app.get('/content')
def content(_: str = Depends(reviewer)):
    return []
