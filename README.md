# Focus Platform Training

منصة تكوينية داخلية حصرية لمركز Focus — سافي، المغرب
Plateforme de formation interne — Centre Focus, Safi, Maroc

> المرجع الكامل للمشروع في [CLAUDE.md](./CLAUDE.md)

## Stack

- **Backend:** FastAPI + PostgreSQL + SQLAlchemy + Alembic + Celery + Redis
- **Frontend:** Next.js 14 (App Router) + TypeScript + Tailwind CSS — RTL + خط Cairo
- **AI:** Claude API (claude-fable-5)
- **PDF/QR:** WeasyPrint + qrcode

## التشغيل / Démarrage

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # عدّل القيم (DATABASE_URL, SECRET_KEY, ANTHROPIC_API_KEY...)

# قاعدة البيانات — توليد أول migration ثم تطبيقه
alembic revision --autogenerate -m "initial schema"
alembic upgrade head

# حساب الأدمين الأولي + الفئات
python -m scripts.seed   # admin@focus.ma / ChangeMe123!

# تشغيل الخادم
uvicorn app.main:app --reload --port 8000
```

### 2. Celery Worker (للـ AI Pipeline)

```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev   # http://localhost:3000
```

## نقاط أساسية

- لوحة الأدمين: `/admin/*` — واجهة المتعلم: `/dashboard`, `/course/[id]`, `/certificates`
- التحقق العام من الشهادات: `/verify/{serial_number}` (بدون login)
- الإدراج التلقائي: `POST /api/v1/content/import` مع Header `X-API-Key` — مثال في `backend/scripts/import_example.py`
- توثيق الـ API: `http://localhost:8000/docs`

## ملاحظات

- **قالب الشهادة:** placeholder حالياً في `backend/app/utils/pdf_generator.py` — سيُستبدل بقالب ياسر الرسمي
- **WeasyPrint** يتطلب مكتبات نظام: `apt install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0`
- كل محتوى AI يُنشأ كـ **Draft** — الأدمين يراجع ثم يضغط "نشر / Publier"
