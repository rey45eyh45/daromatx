# DAROMATX Academy Bot# DAROMATX Academy Bot



Telegram Mini App orqali kurs sotish platformasi.Telegram Mini App orqali kurs sotish platformasi.



## Tez boshlash (Development)## 📁 Loyiha strukturasi



### 1. Virtual environment yaratish```

```powershellDAROMATX_BOT/

python -m venv .venv├── bot/                    # Telegram Bot (Python/Aiogram 3)

.venv\Scripts\activate│   ├── main.py            # Bot entry point

```│   ├── config.py          # Konfiguratsiya

│   ├── handlers/          # Bot handlerlari

### 2. Dependencies ornatish│   ├── keyboards/         # Klaviaturalar

```powershell│   └── database/          # Database modellari va repository

pip install -r bot/requirements.txt│

pip install -r api/requirements.txt├── api/                    # Backend API (FastAPI)

cd mini-app && npm install│   ├── main.py            # API entry point

```│   └── routes/            # API endpointlari

│

### 3. .env sozlash├── mini-app/              # Frontend (React + Vite + TailwindCSS)

```powershell│   ├── src/

copy .env.example .env│   │   ├── components/    # React komponentlari

```│   │   ├── pages/         # Sahifalar

│   │   ├── context/       # React Context

### 4. Ishga tushirish│   │   └── api/           # API client

```powershell│   └── package.json

# Terminal 1 - Bot│

cd bot && python main.py└── .env                   # Environment variables

```

# Terminal 2 - API

cd api && python main.py## 🚀 O'rnatish



# Terminal 3 - Mini App### 1. Python environment yaratish

cd mini-app && npm run dev

``````bash

cd bot

## Docker bilan ishga tushirish (Production)python -m venv venv

.\venv\Scripts\activate  # Windows

### 1. Server tayyorlashpip install -r requirements.txt

```bash```

curl -fsSL https://get.docker.com | sh

sudo usermod -aG docker $USER### 2. API dependencies

```

```bash

### 2. Loyihani klonlashcd api

```bashpip install -r requirements.txt

git clone https://github.com/your-username/daromatx-bot.git```

cd daromatx-bot

```### 3. Mini App dependencies



### 3. .env sozlash```bash

```bashcd mini-app

cp .env.example .envnpm install

nano .env```

```

## ⚙️ Sozlash

### 4. Build va ishga tushirish

```bash`.env` faylini to'ldiring:

chmod +x deploy.sh

./deploy.sh build```env

./deploy.sh start# Telegram Bot

```BOT_TOKEN=your_bot_token_here

ADMIN_IDS=123456789,987654321

### 5. SSL sertifikat olish

```bash# Database

./deploy.sh sslDATABASE_URL=sqlite+aiosqlite:///./database.db

```

# API

## Deploy CommandsAPI_HOST=0.0.0.0

API_PORT=8000

| Command | Description |API_SECRET_KEY=your-secret-key

|---------|-------------|

| ./deploy.sh build | Docker images build |# Mini App URL (production)

| ./deploy.sh start | Barcha servislarni ishga tushirish |MINI_APP_URL=https://your-domain.com

| ./deploy.sh stop | Barcha servislarni toxtatish |

| ./deploy.sh restart | Servislarni qayta ishga tushirish |# Payment (Click)

| ./deploy.sh logs | Loglarni korish |CLICK_MERCHANT_ID=

| ./deploy.sh status | Servislar holatini korish |CLICK_SERVICE_ID=

| ./deploy.sh ssl | SSL sertifikat olish |CLICK_SECRET_KEY=

| ./deploy.sh backup | Database backup |

| ./deploy.sh update | Yangilash va restart |# Payment (Payme)

PAYME_MERCHANT_ID=

## Loyiha strukturasiPAYME_SECRET_KEY=

```

```

DAROMATX_BOT/## 🏃 Ishga tushirish

├── bot/                    # Telegram Bot (Aiogram 3)

├── api/                    # FastAPI Backend### Development mode

├── mini-app/              # React Mini App

├── nginx/                 # Nginx configs**1. Bot:**

├── docker-compose.yml     # Docker orchestration```bash

├── Dockerfile.bot         # Bot containercd bot

├── Dockerfile.api         # API containerpython main.py

├── Dockerfile.webapp      # Mini App container```

├── deploy.sh              # Deploy script

└── .env.example           # Environment template**2. API:**

``````bash

cd api

## Tolov tizimlariuvicorn main:app --reload --port 8000

```

- Telegram Stars - Tayyor

- Click - Sozlash kerak**3. Mini App:**

- Payme - Sozlash kerak```bash

- TON - Sozlash kerakcd mini-app

npm run dev

## Support```



Telegram: @daromatx_support### Production mode



## LicenseMini App'ni build qiling:

```bash

MIT Licensecd mini-app

npm run build
```

Build fayllarini serverga deploy qiling (Vercel, Netlify, yoki boshqa).

## 📱 Telegram Bot sozlash

1. @BotFather dan bot yarating
2. Bot token'ni `.env` ga qo'shing
3. Mini App URL'ni @BotFather da sozlang:
   - `/mybots` → Bot tanlang → `Bot Settings` → `Menu Button`
   - URL: Mini App URL'ingiz

## 💰 To'lov tizimlari

### Telegram Stars
Telegram ichida to'lov. Hech qanday qo'shimcha sozlash kerak emas.

### Click
1. Click.uz dan merchant account oching
2. Service yarating
3. Credentials'ni `.env` ga qo'shing

### Payme
1. Payme.uz dan merchant account oching
2. Credentials'ni `.env` ga qo'shing

### TON Crypto
1. TON wallet manzilini `.env` ga qo'shing

## 📚 API Endpoints

### Courses
- `GET /api/courses` - Barcha kurslar
- `GET /api/courses/{id}` - Bitta kurs
- `GET /api/courses/categories` - Kategoriyalar

### Users
- `GET /api/users/me` - Joriy foydalanuvchi
- `GET /api/users/me/courses` - Sotib olingan kurslar

### Payments
- `POST /api/payments/create` - To'lov yaratish
- `GET /api/payments/{id}/status` - To'lov statusi

### Admin
- `GET /api/admin/stats` - Statistika
- `POST /api/admin/courses` - Kurs qo'shish
- `GET /api/admin/users` - Foydalanuvchilar

## 🔧 Texnologiyalar

- **Bot:** Python 3.11+, Aiogram 3, SQLAlchemy 2
- **API:** FastAPI, Uvicorn
- **Frontend:** React 18, Vite, TailwindCSS, TypeScript
- **Database:** SQLite (development), PostgreSQL (production)
- **Telegram SDK:** @telegram-apps/sdk-react

## 📄 Litsenziya

MIT License
