# Railway Deployment Guide

## Railway.app ga joylash

### 1. Railway hisobini ochish
https://railway.app ga kiring va GitHub bilan ro'yxatdan o'ting.

### 2. Yangi loyiha yaratish

#### Bot uchun:
1. "New Project" → "Deploy from GitHub repo"
2. Repository ni tanlang
3. "Add Service" → "Database" → "PostgreSQL" qo'shing
4. Bot service sozlamalari:
   - Root Directory: `bot`
   - Start Command: `python main.py`

#### API uchun:
1. "Add Service" → "GitHub Repo" (yana shu repo)
2. API service sozlamalari:
   - Root Directory: `api`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### Mini App uchun:
1. "Add Service" → "GitHub Repo" (yana shu repo)
2. Mini App service sozlamalari:
   - Root Directory: `mini-app`
   - Build Command: `npm install && npm run build`
   - Start Command: `npx serve dist -s -l $PORT`

### 3. Environment Variables

Bot uchun:
```
BOT_TOKEN=your_bot_token
ADMIN_IDS=5425876649
DATABASE_URL=${{Postgres.DATABASE_URL}}
API_URL=https://your-api.railway.app
WEBAPP_URL=https://your-webapp.railway.app
```

API uchun:
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
BOT_TOKEN=your_bot_token
SECRET_KEY=your-secret-key-here
```

Mini App uchun:
```
VITE_API_URL=https://your-api.railway.app
VITE_BOT_USERNAME=daromatx_bot
```

### 4. Domain sozlash

Har bir service uchun:
1. Service → Settings → Networking
2. "Generate Domain" bosing
3. Yoki o'z domainni ulang

### 5. PostgreSQL ulanish

Railway avtomatik `DATABASE_URL` beradi.
Bot va API uchun `${{Postgres.DATABASE_URL}}` ishlating.

## Loyiha strukturasi Railway uchun

```
DAROMATX_BOT/
├── bot/
│   ├── Procfile          # worker: python main.py
│   ├── requirements.txt
│   └── ...
├── api/
│   ├── Procfile          # web: uvicorn main:app ...
│   ├── requirements.txt
│   └── ...
├── mini-app/
│   ├── package.json
│   └── ...
└── railway.json
```

## Muhim eslatmalar

1. **PostgreSQL**: Railway bepul PostgreSQL beradi (500MB)
2. **Hobby Plan**: $5/oy - 500 soat, 512MB RAM
3. **Pro Plan**: $20/oy - cheksiz
4. **Sleep**: Bepul planda 30 daqiqa harakatsizlikdan keyin uxlaydi

## Troubleshooting

### Bot ishlamayapti
- DATABASE_URL to'g'ri ekanligini tekshiring
- BOT_TOKEN to'g'ri ekanligini tekshiring
- Logs ni ko'ring: Service → Deployments → View Logs

### API ishlamayapti
- PORT environment variable Railway beradi
- `--port $PORT` ishlatganingizni tekshiring

### Mini App ishlamayapti
- `npm run build` muvaffaqiyatli bo'lganini tekshiring
- VITE_API_URL to'g'ri ekanligini tekshiring
