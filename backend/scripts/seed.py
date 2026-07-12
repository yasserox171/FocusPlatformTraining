"""إنشاء حساب أدمين أولي + فئات أساسية

الاستخدام: python -m scripts.seed
"""
from app.database import SessionLocal
from app.models import Category, User, UserRole
from app.security import hash_password

ADMIN_EMAIL = "admin@focus.ma"
ADMIN_PASSWORD = "ChangeMe123!"


def seed():
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == ADMIN_EMAIL).first() is None:
            db.add(
                User(
                    email=ADMIN_EMAIL,
                    password_hash=hash_password(ADMIN_PASSWORD),
                    role=UserRole.admin,
                    full_name_ar="مدير المنصة",
                    full_name_fr="Administrateur",
                )
            )
            print(f"Admin créé: {ADMIN_EMAIL} / {ADMIN_PASSWORD} — غيّر كلمة المرور فوراً!")
        if db.query(Category).count() == 0:
            db.add_all(
                [
                    Category(name_ar="السلامة والصحة المهنية", name_fr="Hygiène Sécurité Environnement"),
                    Category(name_ar="المعلوميات", name_fr="Informatique"),
                    Category(name_ar="اللغات", name_fr="Langues"),
                    Category(name_ar="التدبير", name_fr="Gestion"),
                ]
            )
            print("Catégories de base créées")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
