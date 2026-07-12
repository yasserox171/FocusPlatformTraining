# CLAUDE.md — Focus Platform Training
# مرجع المشروع الكامل لـ Claude Code / Fable 5

---

## 1. نظرة عامة على المشروع

**الاسم:** Focus Platform Training (فوكس بلاتفورم ترينين)  
**الطبيعة:** منصة تكوينية داخلية حصرية لمركز Focus، سافي، المغرب  
**الهدف:** إدارة المحتوى التعليمي (دروس، دورات، تمارين، كويزات) مع نظام شهادات رسمية وخط إنتاج محتوى مدعوم بالذكاء الاصطناعي  
**اللغة:** ثنائية — عربي وفرنسي ممزوجان بشكل طبيعي في نفس الواجهة (مثال: "نشر / Publier")، بدون خيار تبديل لغة  
**الاتجاه:** RTL أساسي، مع dir="auto" على كتل المحتوى  
**الخط:** Cairo أو Tajawal (يدعم العربية واللاتينية معاً)

---

## 2. Stack التقني

```
Backend:    FastAPI (Python) + PostgreSQL + SQLAlchemy + Alembic
Frontend:   Next.js 14 (App Router) + TypeScript + Tailwind CSS + shadcn/ui
Auth:       JWT (access + refresh tokens) + FastAPI Security
AI:         Claude API (claude-fable-5) + Celery + Redis (task queue)
PDF:        WeasyPrint (شهادات)
QR:         qrcode (Python library)
Video:      YouTube IFrame API (embed) + دعم روابط مباشرة
Storage:    Local filesystem / S3-compatible (للملفات)
Cache:      Redis
```

---

## 3. هيكل المجلدات

```
focus-platform-training/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── content.py        # دروس، دورات، تمارين، كويز
│   │   │   ├── certificate.py
│   │   │   ├── progress.py
│   │   │   └── category.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── admin/
│   │   │   │   ├── content.py
│   │   │   │   ├── users.py
│   │   │   │   ├── analytics.py
│   │   │   │   └── pipeline.py
│   │   │   └── learner/
│   │   │       ├── content.py
│   │   │       ├── progress.py
│   │   │       └── certificates.py
│   │   ├── services/
│   │   │   ├── certificate_service.py   # توليد PDF + QR
│   │   │   ├── ai_pipeline/
│   │   │   │   ├── i1_prompt.py
│   │   │   │   ├── r1_validation.py
│   │   │   │   ├── i2_search.py
│   │   │   │   ├── i3_analysis.py
│   │   │   │   ├── duplicate_check.py
│   │   │   │   ├── i4_generation.py
│   │   │   │   └── r5_upload.py
│   │   │   └── linkedin_service.py
│   │   ├── tasks/               # Celery tasks
│   │   │   └── pipeline_tasks.py
│   │   └── utils/
│   │       ├── qr_generator.py
│   │       └── pdf_generator.py
│   ├── alembic/
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── app/
│   │   ├── layout.tsx           # RTL + Cairo font
│   │   ├── (learner)/           # واجهة المتعلم
│   │   │   ├── dashboard/
│   │   │   ├── course/[id]/
│   │   │   ├── lesson/[id]/
│   │   │   └── certificates/
│   │   └── (admin)/             # لوحة الأدمين (منفصلة تماماً)
│   │       ├── layout.tsx
│   │       ├── dashboard/
│   │       ├── content/
│   │       │   ├── new/
│   │       │   ├── drafts/      # محتوى AI في انتظار النشر
│   │       │   └── [id]/edit/
│   │       ├── users/
│   │       ├── analytics/
│   │       └── pipeline/        # واجهة AI Pipeline
│   ├── components/
│   │   ├── ui/                  # shadcn/ui components
│   │   ├── bilingual/           # مكونات ثنائية اللغة
│   │   │   └── BilingualButton.tsx   # مثال: "نشر / Publier"
│   │   ├── content-blocks/
│   │   │   ├── TextEditorBlock.tsx
│   │   │   ├── VideoBlock.tsx        # YouTube embed
│   │   │   ├── QuizBlock.tsx         # MCQ / Yes-No
│   │   │   └── ExerciseBlock.tsx
│   │   ├── certificate/
│   │   │   └── CertificateCard.tsx   # QR + PDF + LinkedIn buttons
│   │   └── progress/
│   │       └── ProgressBar.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   └── types.ts
│   ├── tailwind.config.ts        # RTL plugin + Cairo font
│   └── next.config.ts
├── pipeline/                     # AI Pipeline مستقل
│   └── ...
└── CLAUDE.md                     # هذا الملف
```

---

## 4. قاعدة البيانات — النماذج الأساسية

### Users
```python
class User(Base):
    id: UUID
    email: str
    password_hash: str
    role: Enum("admin", "learner")
    full_name_ar: str        # الاسم بالعربية
    full_name_fr: str        # الاسم بالفرنسية
    is_active: bool
    created_at: datetime
```

### Category
```python
class Category(Base):
    id: UUID
    name_ar: str
    name_fr: str
    created_by_ai: bool      # أُنشئت تلقائياً بواسطة I3
```

### ContentItem — الجدول الرئيسي للمحتويات
```python
class ContentItem(Base):
    id: UUID
    type: Enum("lesson", "course", "exercise", "quiz")
    title_ar: str
    title_fr: str
    category_id: UUID → Category
    status: Enum("draft", "published")  # draft = من AI أو بانتظار النشر
    created_by: UUID → User (admin)
    published_by: UUID → User (admin)
    published_at: datetime
    is_ai_generated: bool
    created_at: datetime
```

### Unit — وحدات الدورة التكوينية
```python
class Unit(Base):
    id: UUID
    course_id: UUID → ContentItem (type=course)
    title_ar: str
    title_fr: str
    order: int               # الترتيب داخل الدورة
    prerequisite_unit_id: UUID → Unit (nullable)  # Prerequisite
```

### Lesson — دروس داخل الوحدة أو مستقلة
```python
class Lesson(Base):
    id: UUID
    unit_id: UUID → Unit (nullable)    # داخل دورة
    content_item_id: UUID → ContentItem (nullable)  # درس مستقل
    title_ar: str
    title_fr: str
    order: int
```

### Paragraph — الفقرات (اللبنات الأساسية)
```python
class Paragraph(Base):
    id: UUID
    lesson_id: UUID → Lesson
    type: Enum("text", "video", "quiz", "exercise")
    order: int
    lang_hint: Enum("ar", "fr", "auto")   # dir="auto" افتراضياً
    # للنص:
    content_html: str (nullable)
    # للفيديو:
    video_url: str (nullable)             # YouTube URL أو رابط مباشر
    video_type: Enum("youtube", "direct") (nullable)
    # للكويز والتمارين: → QuizQuestion / Exercise
```

### QuizQuestion
```python
class QuizQuestion(Base):
    id: UUID
    paragraph_id: UUID → Paragraph
    question_text: str
    question_type: Enum("mcq", "yes_no")
    options: JSON                # [{id, text, is_correct}]
    hint: str (nullable)
    is_final_quiz: bool          # هل هو الكويز النهائي للدورة؟
```

### Exercise
```python
class Exercise(Base):
    id: UUID
    paragraph_id: UUID → Paragraph
    description: str             # نص التمرين
    solution: str                # الحل الكامل (يُخفى حتى يضغط المتعلم)
    hint: str (nullable)
    # لا يوجد تقييم — فقط عرض + حل + تلميح
```

### Certificate
```python
class Certificate(Base):
    id: UUID
    learner_id: UUID → User
    course_id: UUID → ContentItem (type=course)
    type: Enum("attendance", "competency")
    serial_number: str (unique)  # رقم تسلسلي فريد
    qr_code_url: str             # رابط صفحة التحقق العامة
    pdf_path: str                # مسار ملف PDF
    issued_at: datetime
    template_data: JSON          # بيانات القالب (سيوفره ياسر لاحقاً)
```

### LearnerProgress
```python
class LearnerProgress(Base):
    id: UUID
    learner_id: UUID → User
    content_item_id: UUID → ContentItem
    unit_id: UUID → Unit (nullable)
    lesson_id: UUID → Lesson (nullable)
    paragraph_id: UUID → Paragraph (nullable)
    status: Enum("not_started", "in_progress", "completed")
    quiz_score: float (nullable)    # للكويز النهائي فقط
    attempts: int                   # عدد محاولات الكويز
    completed_at: datetime (nullable)
```

### AIPipelineJob
```python
class AIPipelineJob(Base):
    id: UUID
    prompt: str
    status: Enum("pending", "validating", "searching", "analyzing",
                 "awaiting_user", "generating", "uploading", "done", "failed")
    initiated_by: UUID → User (admin)
    search_results: JSON (nullable)
    analysis_results: JSON (nullable)
    user_request: JSON (nullable)        # R3 request
    user_answer: JSON (nullable)         # R4 answer
    generated_content_ids: JSON (nullable)  # IDs of created drafts
    error_message: str (nullable)
    created_at: datetime
    updated_at: datetime
```

---

## 5. منطق الأعمال الأساسي (Business Logic)

### 5.1 نظام الشهادات

```
منح الشهادة:
  - دورة تكوينية فقط (type="course")
  
  شهادة حضور (attendance):
    • الشرط: إكمال جميع الوحدات (كل paragraphs في كل lessons في كل units)
    • لا يُشترط أي نقطة
    
  شهادة كفاءة (competency):
    • الشرط: يوجد كويز نهائي (QuizQuestion.is_final_quiz=True) في الدورة
    • نسبة النجاح: قابلة للتخصيص per دورة (افتراضي 35%)
    • المحاولات: غير محدودة — المتعلم يعيد حتى يجتاز
    
  التحقق من الشهادة:
    • صفحة عامة: /verify/[serial_number]
    • تعرض صورة الشهادة + بيانات المتعلم + نوع الشهادة
    • QR code يشير لهذا الرابط
    
  توليد الشهادة:
    1. إنشاء serial_number فريد
    2. توليد PDF بـ WeasyPrint من القالب (القالب سيوفره ياسر)
    3. توليد QR code يشير لـ /verify/[serial_number]
    4. دمج QR في PDF
    5. حفظ في قاعدة البيانات
```

### 5.2 Prerequisites بين الوحدات

```
منطق Prerequisites:
  - كل Unit يمكن أن يكون له prerequisite_unit_id
  - المتعلم لا يمكنه الوصول للوحدة B إلا بعد إكمال الوحدة A
  - الدورات نفسها مستقلة (لا prerequisites بين دورات مختلفة)
  
  تحقق الوصول:
    GET /api/learner/unit/{unit_id}/access
    → يتحقق إذا prerequisite_unit مكتمل في LearnerProgress
```

### 5.3 Progress Bar للمتعلم

```
حساب التقدم في الدورة:
  progress% = (paragraphs_completed / total_paragraphs) * 100
  
  يُحسب لكل دورة بشكل منفصل
  يُعرض في:
    - قائمة الدورات (learner dashboard)
    - صفحة الدورة (course page)
    - الـ Sidebar بجانب الوحدات
```

### 5.4 كشف المحتوى المكرر

```
قبل توليد المحتوى (I4):
  1. استخراج الموضوعات الرئيسية من نتائج التحليل (I3)
  2. مقارنتها مع ContentItem.title_ar و title_fr الموجودة
  3. إذا وُجد تشابه > 80%:
     - إشعار المستخدم
     - سؤال: إنشاء محتوى جديد أم تحديث الموجود؟
```

---

## 6. AI Pipeline — التفاصيل الكاملة

```
المسار الكامل:

I1 → R1 → I2 → R2 → DuplicateCheck → I3 → R3 → (انتظار المستخدم) → R4 → I4 → R5

التفصيل:

I1 (Prompt Interface):
  - المستخدم (Admin) يكتب Prompt
  - مثال: "ابحث عن مواد تعليمية حول السلامة والصحة المهنية بالفرنسية"
  - يُنشئ AIPipelineJob بـ status="validating"

R1 (Claude API Validation) — claude-fable-5:
  - يُقيّم وضوح الـ Prompt
  - إذا غير واضح:
    status="failed", error="prompt_unclear"
    يُعيد رسالة للمستخدم لإعادة الكتابة
  - إذا فشل (انقطاع إنترنت):
    status="failed", error="connection_error"
    رسالة: "Failed - تعذّر الاتصال"
  - إذا نجح:
    status="searching"
    رسالة: "البحث جارٍ / Recherche en cours..."

I2 (Search Engine) — Celery Task:
  - يبحث عن مصادر تعليمية وفق الـ Prompt
  - يلتزم باللغة المطلوبة في الـ Prompt
  - يخزّن النتائج في AIPipelineJob.search_results

R2 (Sources Transfer):
  - status="analyzing"
  - ينقل المصادر إلى I3

Duplicate Check:
  - يستخرج الموضوعات الرئيسية
  - يتحقق من ContentItem الموجودة
  - يُضيف تحذيراً إذا وُجد تشابه

I3 (Analysis Engine) — claude-fable-5:
  - يحلل المصادر
  - يصنّفها حسب Category الموجودة في قاعدة البيانات
  - إذا لم توجد category مناسبة → ينشئ Category جديدة (created_by_ai=True)
  - يُحدد أنواع المحتوى الممكن إنشاؤها
  - يخزّن في AIPipelineJob.analysis_results

R3 (Request to User):
  - status="awaiting_user"
  - يرسل للمستخدم قائمة بالمحتويات الممكنة إنشاؤها:
    مثال: [درس "Définition HSE", كويز "Fiche de risque", تمرين "تمرين تحديد الأخطار"]
  - المستخدم يختار ما يريد إنشاؤه (R4)

R4 (User Answer):
  - المستخدم يحدد المحتويات المطلوبة
  - يخزّن في AIPipelineJob.user_answer
  - status="generating"

I4 (Content Generation) — claude-fable-5:
  ⚠️ مهم: لا تُولَّد فيديوهات هنا أبداً
  - يولّد بناءً على المصادر واختيار المستخدم:
    * نصوص Text Editor (HTML)
    * أسئلة Quiz (MCQ / Yes-No) مع خيارات وإجابات صحيحة
    * تمارين مع حلول وتلميحات
  - يُنشئ ContentItem بـ status="draft", is_ai_generated=True

R5 (Upload as Draft):
  - status="done"
  - يُضيف المحتوى للمنصة كـ Draft
  - Admin يرى الـ Drafts في لوحته
  - Admin يراجع → يضغط "نشر / Publier" لنشره
```

---

## 7. API Key للإدراج التلقائي

```python
# يُصدر API Key لكل Admin
# يُستخدم في Python Script لإضافة المحتوى تلقائياً

# Header: X-API-Key: {key}
# Endpoint: POST /api/v1/content/import
# Body: JSON يحتوي على ContentItem كامل (بدون فيديو)

# الـ API يتحقق من:
# 1. صحة المفتاح
# 2. صلاحيات الـ Admin
# 3. البيانات المطلوبة
# ثم يُنشئ Content كـ Draft للمراجعة
```

---

## 8. واجهات المستخدم — المتطلبات التفصيلية

### 8.1 واجهة المتعلم (Learner Interface)

**الصفحة الرئيسية (Dashboard):**
- شريط "محتوياتي / Mes contenus": المحتويات التي بدأها المتعلم
- شريط "الأحدث / Récents": آخر المحتويات المنشورة
- شريط "حسب الفئة / Par catégorie": محتويات مصنفة
- جميع المحتويات المنشورة مرئية لجميع المتعلمين

**صفحة الدورة التكوينية:**
- عنوان الدورة + Progress Bar
- Sidebar يمين: قائمة الوحدات والدروس
  - الوحدة مقفلة (🔒) إذا prerequisite غير مكتمل
  - درس نشط / مكتمل / معلق
- منطقة المحتوى: عرض الفقرات بالترتيب
  - كل فقرة نوعها في badge (AR / FR)
  - زر "التالي / Suivant" و"السابق / Précédent"

**كتلة التمرين (Exercise Block):**
- عرض نص التمرين
- زر "💡 تلميح / Indice" (يظهر التلميح إن وُجد)
- زر "✓ الحل / Solution" (يكشف الحل الكامل)
- لا يوجد تقييم أو نقطة

**كتلة الكويز (Quiz Block):**
- سؤال MCQ أو نعم/لا
- خيارات قابلة للنقر
- زر "💡 تلميح / Indice"
- زر "✓ الجواب الصحيح / Bonne réponse"
- تلوين الإجابات (أخضر للصحيح، أحمر للخطأ) بعد الكشف

**الكويز النهائي للدورة:**
- نفس واجهة Quiz Block
- عند الإجابة: يُحسب النتيجة
- إذا ≥ نسبة النجاح (configurable): شهادة كفاءة
- إذا < النسبة: رسالة تشجيع + زر "إعادة المحاولة / Réessayer"
- لا حد للمحاولات

**صفحة الشهادات:**
- عرض شهادات المتعلم
- لكل شهادة:
  - صورة معاينة الشهادة
  - زر "📄 تنزيل PDF / Télécharger"
  - زر "💼 LinkedIn"
  - الرقم التسلسلي
  - نوع الشهادة (حضورية / كفاءة)

### 8.2 لوحة الأدمين (Admin Panel — منفصلة تماماً)

**URL:** /admin/* (مسار منفصل عن /learner/*)

**Dashboard الأدمين:**
- إحصاءات سريعة: عدد المتعلمين، المحتويات، الشهادات المُصدرة
- Drafts تنتظر المراجعة (قادمة من AI أو يدوية)
- آخر نشاط

**Analytics:**
- أكثر المحتويات مشاهدةً
- نسب إكمال الدورات
- عدد الشهادات الممنوحة (حضور vs كفاءة)
- توزيع المحتوى بالفئة

**إدارة المحتويات:**
- قائمة كل المحتويات (drafted / published)
- فلترة حسب النوع / الفئة / الحالة
- إنشاء محتوى يدوي
- تعديل محتوى موجود
- زر "نشر / Publier" للـ Drafts

**AI Pipeline:**
- واجهة I1: كتابة الـ Prompt
- تتبع حالة الـ Job بشكل real-time (WebSocket أو polling)
- صفحة R3: الرد على طلب AI (اختيار المحتويات المطلوبة)
- عرض الـ Drafts المُنشأة من AI

**إدارة المستخدمين:**
- إنشاء حسابات متعلمين وأدمين
- تعديل / تعطيل حسابات

---

## 9. تصميم الواجهة (UI/UX Guidelines)

```
النظام العام:
  direction: rtl (على مستوى الصفحة)
  font-family: 'Cairo', sans-serif
  
  الألوان الأساسية:
    primary:   #1B4FD8  (أزرق مهني)
    success:   #059669  (أخضر)
    warning:   #B45309  (برتقالي)
    danger:    #DC2626  (أحمر)
    bg:        #F1F5F9  (رمادي فاتح)
    dark:      #0F172A  (للـ navbar والـ admin sidebar)

قاعدة الثنائية اللغوية:
  - كل زر / تسمية: "عربي / Français"
  - النص مختصر: كلمة أو كلمتان لكل لغة
  - الفاصل: "/" أو " · "
  - أمثلة:
    "نشر / Publier"
    "حفظ / Enregistrer"
    "إضافة محتوى / Ajouter"
    "مكتمل / Complété"
    "الكويز النهائي / Quiz final"

كتل المحتوى:
  - badge يمين الكتلة: AR أو FR
  - dir="auto" على النص داخل الكتلة
  - نص عربي → يتجه RTL تلقائياً
  - نص فرنسي → يتجه LTR تلقائياً

عدم الاكتظاظ:
  - استخدام أيقونة + نص قصير بدل نص طويل
  - مسافات كافية بين العناصر (padding لا يقل عن 8px)
  - لا أكثر من 3 أزرار في نفس الصف
```

---

## 10. متطلبات الأمان

```
Auth:
  - JWT access token: 15 دقيقة
  - JWT refresh token: 7 أيام
  - تشفير كلمات المرور: bcrypt

Roles:
  - admin: وصول كامل للـ /admin/* + /api/admin/*
  - learner: وصول للـ /app/* + /api/learner/*
  
API Key:
  - يُصدر للـ admins فقط
  - يُرسل في Header: X-API-Key
  - قابل للإلغاء

Certificates:
  - صفحة التحقق /verify/{serial} عامة (بدون login)
  - لكن لا تعرض بيانات حساسة
```

---

## 11. متغيرات البيئة (.env)

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/focus_platform

# Redis
REDIS_URL=redis://localhost:6379

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Claude API (Fable 5)
ANTHROPIC_API_KEY=your-anthropic-api-key
CLAUDE_MODEL=claude-fable-5

# Storage
UPLOAD_DIR=./uploads
CERTIFICATES_DIR=./certificates

# App
APP_URL=http://localhost:3000
API_URL=http://localhost:8000

# Email (اختياري)
SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASS=
```

---

## 12. مراحل التطوير المقترحة

```
المرحلة 1 — الأساس:
  ✓ إعداد المشروع (FastAPI + Next.js + PostgreSQL)
  ✓ نظام المصادقة (JWT + roles)
  ✓ نماذج قاعدة البيانات الكاملة + Migrations
  ✓ CRUD الأساسي للمحتويات

المرحلة 2 — واجهة المتعلم:
  ✓ Dashboard مع الأشرطة الثلاثة
  ✓ صفحة الدورة التكوينية + Sidebar
  ✓ كتل الفقرات (Text, Video, Quiz, Exercise)
  ✓ منطق Prerequisites بين الوحدات
  ✓ Progress Bar

المرحلة 3 — نظام الشهادات:
  ✓ توليد شهادة حضور
  ✓ توليد شهادة كفاءة + الكويز النهائي
  ✓ PDF + QR + صفحة التحقق العامة
  ✓ أزرار LinkedIn + تنزيل

المرحلة 4 — لوحة الأدمين:
  ✓ Dashboard + Analytics
  ✓ إنشاء / تعديل المحتوى يدوياً
  ✓ إدارة المستخدمين
  ✓ نظام الـ Drafts + زر النشر

المرحلة 5 — AI Pipeline:
  ✓ I1 → R1 (Claude validation)
  ✓ I2 → R2 (Search)
  ✓ Duplicate Check
  ✓ I3 → R3 (Analysis + Request)
  ✓ R4 → I4 → R5 (Generate + Upload Draft)
  ✓ Real-time status tracking (WebSocket)

المرحلة 6 — API Key + Python Script:
  ✓ نظام API Key للأدمين
  ✓ Endpoint /api/v1/content/import
  ✓ Python script مثال

المرحلة 7 — الصقل النهائي:
  ✓ اختبارات شاملة
  ✓ تحسين الأداء
  ✓ Responsive design
  ✓ Error handling كامل
  ✓ قالب الشهادة (سيوفره ياسر)
```

---

## 13. ملاحظات خاصة لـ Claude Code

```
⚠️  النقاط الحرجة التي يجب مراعاتها دائماً:

1. اللغة والاتجاه:
   - html dir="rtl" على كل الصفحات
   - dir="auto" على كتل المحتوى النصي فقط
   - الأزرار دائماً: "عربي / Français" (وليس اختياراً بينهما)

2. الشهادات:
   - فقط الدورات التكوينية تمنح شهادات
   - نسبة النجاح قابلة للتخصيص per دورة (configurable field)
   - محاولات الكويز: غير محدودة أبداً
   - قالب الشهادة: placeholder حالياً — سيوفره ياسر لاحقاً

3. التمارين:
   - لا تقييم أبداً — عرض + حل + تلميح فقط
   - الحل مخفي حتى يضغط المتعلم عليه

4. AI Pipeline:
   - I4 لا يُولّد فيديوهات أبداً (نصوص وكويزات وتمارين فقط)
   - كل محتوى AI يُنشأ كـ Draft (is_ai_generated=True)
   - Admin يراجع ويضغط نشر يدوياً

5. Prerequisites:
   - بين الوحدات داخل نفس الدورة فقط
   - الدورات نفسها مستقلة تماماً عن بعضها

6. الفيديو:
   - YouTube embed أساساً
   - دعم روابط مباشرة أيضاً
   - لا رفع ملفات فيديو للخادم

7. Admin:
   - حسابات متعددة، كل Admin يملك نفس الصلاحيات
   - لوحة Admin على مسار /admin منفصل تماماً
   - لا يوجد دور Reviewer — كل Admin ينشر مباشرة

8. Cooldown للكويز:
   - غير مطبق حالياً
   - اتركه بدون cooldown حتى إشعار آخر

9. تخصيص وصول المتعلمين:
   - كل المحتويات المنشورة تظهر لكل المتعلمين
   - تخصيص per متعلم مؤجل لمرحلة لاحقة
```

---

## 14. نقاط الـ API الأساسية

```
Auth:
  POST /api/auth/login
  POST /api/auth/refresh
  POST /api/auth/logout

Learner:
  GET  /api/learner/dashboard              # الأشرطة الثلاثة
  GET  /api/learner/course/{id}            # تفاصيل الدورة
  GET  /api/learner/unit/{id}/access       # تحقق Prerequisites
  POST /api/learner/progress               # تحديث التقدم
  GET  /api/learner/certificates           # شهادات المتعلم
  GET  /api/learner/quiz/{id}/submit       # تقديم إجابة الكويز النهائي

Admin:
  GET  /api/admin/dashboard
  GET  /api/admin/analytics
  
  # Content
  GET  /api/admin/content                  # قائمة كل المحتويات
  POST /api/admin/content                  # إنشاء محتوى
  PUT  /api/admin/content/{id}             # تعديل
  POST /api/admin/content/{id}/publish     # نشر Draft
  DELETE /api/admin/content/{id}
  
  # Pipeline
  POST /api/admin/pipeline/start           # I1: إطلاق Pipeline
  GET  /api/admin/pipeline/{job_id}/status # متابعة الحالة
  POST /api/admin/pipeline/{job_id}/answer # R4: جواب المستخدم
  
  # Users
  GET  /api/admin/users
  POST /api/admin/users
  PUT  /api/admin/users/{id}
  
  # API Keys
  POST /api/admin/api-keys
  DELETE /api/admin/api-keys/{id}

Public:
  GET  /verify/{serial_number}             # صفحة التحقق من الشهادة (عامة)

Import (API Key):
  POST /api/v1/content/import              # X-API-Key header
```

---

*هذا الملف هو المرجع الأساسي للمشروع — أي قرار تقني يجب أن يكون متسقاً مع ما ورد هنا.*  
*قالب الشهادة سيُوفَّر لاحقاً من ياسر — اترك placeholder واضحاً في certificate_service.py*  
*النموذج المستخدم: claude-fable-5*
