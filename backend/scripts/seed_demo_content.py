"""إنشاء محتوى تجريبي (دورة + درس + كويز + تمرين) وحساب متعلم للاختبار

يستعمل نفس خدمات التطبيق (content_service) لضمان صحة البيانات المتداخلة،
وينشر كل محتوى مباشرة (status=published) ليظهر فوراً في واجهة المتعلم.

الاستخدام: python -m scripts.seed_demo_content
"""
from app.database import SessionLocal
from app.models import Category, ContentItem, User, UserRole
from app.schemas.content import (
    ContentItemCreate,
    ExerciseIn,
    LessonIn,
    ParagraphIn,
    QuizOptionIn,
    QuizQuestionIn,
    UnitIn,
)
from app.security import hash_password
from app.services.content_service import create_content_item, publish_content_item

LEARNER_EMAIL = "learner@focus.ma"
LEARNER_PASSWORD = "Learner123!"


def get_or_create_admin(db) -> User:
    admin = db.query(User).filter(User.role == UserRole.admin).first()
    if admin is not None:
        return admin
    admin = User(
        email="admin@focus.ma",
        password_hash=hash_password("ChangeMe123!"),
        role=UserRole.admin,
        full_name_ar="مدير المنصة",
        full_name_fr="Administrateur",
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def get_or_create_learner(db) -> None:
    if db.query(User).filter(User.email == LEARNER_EMAIL).first() is not None:
        return
    db.add(
        User(
            email=LEARNER_EMAIL,
            password_hash=hash_password(LEARNER_PASSWORD),
            role=UserRole.learner,
            full_name_ar="متعلم تجريبي",
            full_name_fr="Apprenant Démo",
        )
    )
    db.commit()
    print(f"حساب متعلم تجريبي: {LEARNER_EMAIL} / {LEARNER_PASSWORD}")


def get_or_create_category(db) -> Category:
    category = db.query(Category).filter(Category.name_ar == "السلامة والصحة المهنية").first()
    if category is not None:
        return category
    category = Category(name_ar="السلامة والصحة المهنية", name_fr="Hygiène Sécurité Environnement")
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def already_exists(db, title_ar: str) -> bool:
    return db.query(ContentItem).filter(ContentItem.title_ar == title_ar).first() is not None


def seed_course(db, admin: User, category: Category) -> None:
    title_ar = "دورة: السلامة والصحة المهنية (HSE)"
    if already_exists(db, title_ar):
        print(f"تخطّي — موجودة سلفاً: {title_ar}")
        return

    payload = ContentItemCreate(
        type="course",
        title_ar=title_ar,
        title_fr="Formation : Hygiène, Sécurité et Environnement (HSE)",
        category_id=category.id,
        pass_threshold=40.0,
        duration_hours=8,
        units=[
            UnitIn(
                title_ar="الوحدة 1: المفاهيم الأساسية",
                title_fr="Unité 1 : Concepts de base",
                order=0,
                lessons=[
                    LessonIn(
                        title_ar="تعريف الخطر والمخاطرة",
                        title_fr="Définition du danger et du risque",
                        order=0,
                        paragraphs=[
                            ParagraphIn(
                                type="text",
                                order=0,
                                lang_hint="auto",
                                content_html=(
                                    "<h2>الخطر مقابل المخاطرة</h2>"
                                    "<p><strong>الخطر (Danger)</strong> هو مصدر محتمل للضرر "
                                    "(آلة، مادة كيميائية، ارتفاع...). "
                                    "<strong>المخاطرة (Risque)</strong> هي احتمال حدوث ذلك الضرر "
                                    "مضروباً في شدته.</p>"
                                    "<p><em>Le danger est une source potentielle de dommage ; "
                                    "le risque est la probabilité que ce dommage survienne, "
                                    "combinée à sa gravité.</em></p>"
                                ),
                            ),
                            ParagraphIn(
                                type="video",
                                order=1,
                                lang_hint="fr",
                                video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                                video_type="youtube",
                            ),
                            ParagraphIn(
                                type="quiz",
                                order=2,
                                quiz_questions=[
                                    QuizQuestionIn(
                                        question_text=(
                                            "هل الخطر والمخاطرة لهما نفس المعنى؟ / "
                                            "Danger et risque ont-ils le même sens ?"
                                        ),
                                        question_type="yes_no",
                                        options=[
                                            QuizOptionIn(id="yes", text="نعم / Oui", is_correct=False),
                                            QuizOptionIn(id="no", text="لا / Non", is_correct=True),
                                        ],
                                        hint="فكّر في الفرق بين المصدر والاحتمال.",
                                        is_final_quiz=False,
                                    )
                                ],
                            ),
                        ],
                    )
                ],
            ),
            UnitIn(
                title_ar="الوحدة 2: تقييم المخاطر",
                title_fr="Unité 2 : Évaluation des risques",
                order=1,
                prerequisite_unit_order=0,
                lessons=[
                    LessonIn(
                        title_ar="خطوات تقييم المخاطر",
                        title_fr="Étapes d'évaluation des risques",
                        order=0,
                        paragraphs=[
                            ParagraphIn(
                                type="text",
                                order=0,
                                lang_hint="auto",
                                content_html=(
                                    "<h2>خطوات تقييم المخاطر حسب ISO 45001</h2>"
                                    "<ol><li>تحديد الأخطار</li><li>تحليل المخاطر</li>"
                                    "<li>تقييم المخاطر</li><li>إجراءات التحكم</li></ol>"
                                ),
                            ),
                            ParagraphIn(
                                type="exercise",
                                order=1,
                                exercises=[
                                    ExerciseIn(
                                        description=(
                                            "حدّد ثلاثة أخطار محتملة في ورشة تحتوي على آلات دوارة "
                                            "ومواد كيميائية، واقترح إجراء تحكم لكل خطر."
                                        ),
                                        solution=(
                                            "1. آلة دوارة بدون واقي → تركيب حاجز واقٍ.\n"
                                            "2. تسرّب مادة كيميائية → تخزين في مكان مهوّى مع لافتات تحذير.\n"
                                            "3. أرضية زلقة → علامات تحذيرية ومواد مانعة للانزلاق."
                                        ),
                                        hint="فكّر في السقوط، الآلات، والمواد الكيميائية.",
                                    )
                                ],
                            ),
                            ParagraphIn(
                                type="quiz",
                                order=2,
                                quiz_questions=[
                                    QuizQuestionIn(
                                        question_text=(
                                            "ما هي الخطوة الأولى في تقييم المخاطر؟ / "
                                            "Quelle est la première étape de l'évaluation des risques ?"
                                        ),
                                        question_type="mcq",
                                        options=[
                                            QuizOptionIn(id="a", text="تحديد الأخطار / Identifier les dangers", is_correct=True),
                                            QuizOptionIn(id="b", text="إجراءات التحكم / Mesures de contrôle", is_correct=False),
                                            QuizOptionIn(id="c", text="التوظيف / Recrutement", is_correct=False),
                                        ],
                                        hint="هي نقطة الانطلاق قبل أي تحليل.",
                                        is_final_quiz=True,
                                    ),
                                    QuizQuestionIn(
                                        question_text=(
                                            "هل تحليل المخاطر يأتي قبل تحديد الأخطار؟ / "
                                            "L'analyse des risques précède-t-elle l'identification des dangers ?"
                                        ),
                                        question_type="yes_no",
                                        options=[
                                            QuizOptionIn(id="yes", text="نعم / Oui", is_correct=False),
                                            QuizOptionIn(id="no", text="لا / Non", is_correct=True),
                                        ],
                                        hint=None,
                                        is_final_quiz=True,
                                    ),
                                ],
                            ),
                        ],
                    )
                ],
            ),
        ],
    )
    content = create_content_item(db, payload, admin)
    publish_content_item(db, content, admin)
    print(f"✓ دورة منشورة: {title_ar}")


def seed_lesson(db, admin: User, category: Category) -> None:
    title_ar = "درس: استعمال معدات الحماية الشخصية (EPI)"
    if already_exists(db, title_ar):
        print(f"تخطّي — موجود سلفاً: {title_ar}")
        return

    payload = ContentItemCreate(
        type="lesson",
        title_ar=title_ar,
        title_fr="Leçon : Utilisation des équipements de protection individuelle (EPI)",
        category_id=category.id,
        lessons=[
            LessonIn(
                title_ar=title_ar,
                title_fr="Utilisation des équipements de protection individuelle (EPI)",
                order=0,
                paragraphs=[
                    ParagraphIn(
                        type="text",
                        order=0,
                        lang_hint="auto",
                        content_html=(
                            "<h2>معدات الحماية الشخصية الأساسية</h2>"
                            "<ul><li>خوذة الأمان — تحمي الرأس من السقوط</li>"
                            "<li>حزام السلامة — للعمل في المرتفعات</li>"
                            "<li>الأحذية الواقية — تحمي القدم من السقوط والانزلاق</li>"
                            "<li>القفازات — حسب طبيعة العمل</li></ul>"
                        ),
                    ),
                    ParagraphIn(
                        type="quiz",
                        order=1,
                        quiz_questions=[
                            QuizQuestionIn(
                                question_text=(
                                    "متى يجب ارتداء حزام السلامة؟ / "
                                    "Quand faut-il porter le harnais de sécurité ?"
                                ),
                                question_type="mcq",
                                options=[
                                    QuizOptionIn(id="a", text="عند العمل في المرتفعات / En travail en hauteur", is_correct=True),
                                    QuizOptionIn(id="b", text="في المكتب / Au bureau", is_correct=False),
                                    QuizOptionIn(id="c", text="أبداً / Jamais", is_correct=False),
                                ],
                                hint="فكّر في خطر السقوط.",
                                is_final_quiz=False,
                            )
                        ],
                    ),
                ],
            )
        ],
    )
    content = create_content_item(db, payload, admin)
    publish_content_item(db, content, admin)
    print(f"✓ درس منشور: {title_ar}")


def seed_quiz(db, admin: User, category: Category) -> None:
    title_ar = "كويز: علامات السلامة"
    if already_exists(db, title_ar):
        print(f"تخطّي — موجود سلفاً: {title_ar}")
        return

    payload = ContentItemCreate(
        type="quiz",
        title_ar=title_ar,
        title_fr="Quiz : Panneaux de sécurité",
        category_id=category.id,
        lessons=[
            LessonIn(
                title_ar=title_ar,
                title_fr="Quiz : Panneaux de sécurité",
                order=0,
                paragraphs=[
                    ParagraphIn(
                        type="quiz",
                        order=0,
                        quiz_questions=[
                            QuizQuestionIn(
                                question_text=(
                                    "العلامة ذات اللون الأحمر والدائرية تعني عادةً؟ / "
                                    "Un panneau rouge et circulaire signifie généralement ?"
                                ),
                                question_type="mcq",
                                options=[
                                    QuizOptionIn(id="a", text="معلومات / Information", is_correct=False),
                                    QuizOptionIn(id="b", text="منع / Interdiction", is_correct=True),
                                    QuizOptionIn(id="c", text="إسعافات أولية / Premiers secours", is_correct=False),
                                ],
                                hint="اللون الأحمر يرتبط بالمنع والخطر.",
                                is_final_quiz=False,
                            ),
                            QuizQuestionIn(
                                question_text=(
                                    "هل اللون الأخضر يشير عادةً للإسعافات الأولية ومخارج الطوارئ؟ / "
                                    "Le vert indique-t-il généralement les premiers secours et sorties de secours ?"
                                ),
                                question_type="yes_no",
                                options=[
                                    QuizOptionIn(id="yes", text="نعم / Oui", is_correct=True),
                                    QuizOptionIn(id="no", text="لا / Non", is_correct=False),
                                ],
                                hint=None,
                                is_final_quiz=False,
                            ),
                        ],
                    )
                ],
            )
        ],
    )
    content = create_content_item(db, payload, admin)
    publish_content_item(db, content, admin)
    print(f"✓ كويز منشور: {title_ar}")


def seed_exercise(db, admin: User, category: Category) -> None:
    title_ar = "تمرين: تحديد الأخطار في ورشة"
    if already_exists(db, title_ar):
        print(f"تخطّي — موجود سلفاً: {title_ar}")
        return

    payload = ContentItemCreate(
        type="exercise",
        title_ar=title_ar,
        title_fr="Exercice : Identifier les dangers dans un atelier",
        category_id=category.id,
        lessons=[
            LessonIn(
                title_ar=title_ar,
                title_fr="Exercice : Identifier les dangers dans un atelier",
                order=0,
                paragraphs=[
                    ParagraphIn(
                        type="exercise",
                        order=0,
                        exercises=[
                            ExerciseIn(
                                description=(
                                    "أنت تزور ورشة نجارة. لاحظت: نشارة خشب متناثرة على الأرض، "
                                    "عامل يستعمل منشاراً كهربائياً بدون نظارات واقية، وسلكاً كهربائياً "
                                    "مكشوفاً قرب الماء. عدّد الأخطار الثلاثة وقدّم توصية لكل واحد."
                                ),
                                solution=(
                                    "1. نشارة خشب على الأرض → خطر انزلاق/حريق — يجب التنظيف الدوري.\n"
                                    "2. عدم استعمال نظارات واقية → خطر إصابة العين — إلزامية النظارات.\n"
                                    "3. سلك كهربائي مكشوف قرب الماء → خطر صعق كهربائي — عزل فوري وإصلاح."
                                ),
                                hint="فكّر في السقوط، الحريق، الإصابة الجسدية، والصعق الكهربائي.",
                            )
                        ],
                    )
                ],
            )
        ],
    )
    content = create_content_item(db, payload, admin)
    publish_content_item(db, content, admin)
    print(f"✓ تمرين منشور: {title_ar}")


def seed_demo_content():
    db = SessionLocal()
    try:
        admin = get_or_create_admin(db)
        get_or_create_learner(db)
        category = get_or_create_category(db)

        seed_course(db, admin, category)
        seed_lesson(db, admin, category)
        seed_quiz(db, admin, category)
        seed_exercise(db, admin, category)

        print("\nتم! سجّل الدخول كمتعلم بـ:")
        print(f"  {LEARNER_EMAIL} / {LEARNER_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_content()
