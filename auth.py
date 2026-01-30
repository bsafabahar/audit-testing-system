"""
ماژول احراز هویت و مدیریت کاربران
Authentication and User Management Module

این ماژول شامل:
- توابع احراز هویت و مدیریت کاربران
- هش کردن و بررسی رمز عبور
- مدیریت توکن بازیابی رمز عبور
- ارسال ایمیل بازیابی رمز
"""

from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from models import User
from database import db
from datetime import datetime, timedelta
import secrets
from typing import Optional

# مقداردهی اولیه
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()


def init_auth(app):
    """مقداردهی اولیه سیستم احراز هویت"""
    # تنظیمات Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'لطفاً برای دسترسی به این صفحه وارد شوید.'
    login_manager.login_message_category = 'warning'
    
    # تنظیمات Bcrypt
    bcrypt.init_app(app)
    
    # تنظیمات Mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = app.config.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = app.config.get('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = app.config.get('MAIL_DEFAULT_SENDER', 'noreply@audit-system.com')
    mail.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """بارگذاری کاربر از دیتابیس"""
    if not db._initialized:
        db._initialize()
    session = db.SessionLocal()
    try:
        user = session.query(User).get(int(user_id))
        if user:
            # بارگذاری تمام attribute ها قبل از بستن session
            session.refresh(user)
            session.expunge(user)
        return user
    finally:
        session.close()


def hash_password(password: str) -> str:
    """هش کردن رمز عبور"""
    return bcrypt.generate_password_hash(password).decode('utf-8')


def check_password(password_hash: str, password: str) -> bool:
    """بررسی صحت رمز عبور"""
    return bcrypt.check_password_hash(password_hash, password)


def create_user(username: str, email: str, password: str, full_name: str = '', is_admin: bool = False) -> Optional[User]:
    """ایجاد کاربر جدید"""
    if not db._initialized:
        db._initialize()
    
    session = db.SessionLocal()
    try:
        # بررسی وجود کاربر با این نام کاربری یا ایمیل
        existing_user = session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            return None
        
        # ایجاد کاربر جدید
        new_user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            is_admin=is_admin,
            is_active=True,
            created_at=datetime.now()
        )
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user
    except Exception as e:
        session.rollback()
        print(f"Error creating user: {e}")
        return None
    finally:
        session.close()


def authenticate_user(username: str, password: str) -> Optional[User]:
    """احراز هویت کاربر"""
    if not db._initialized:
        db._initialize()
    
    session = db.SessionLocal()
    try:
        user = session.query(User).filter(User.username == username).first()
        
        if user and user.is_active and check_password(user.password_hash, password):
            # به‌روزرسانی زمان آخرین ورود
            user.last_login = datetime.now()
            session.commit()
            # بارگذاری تمام attribute ها و جدا کردن از session
            session.refresh(user)
            session.expunge(user)
            return user
        return None
    finally:
        session.close()


def generate_reset_token() -> str:
    """تولید توکن بازیابی رمز عبور"""
    return secrets.token_urlsafe(32)


def create_password_reset_token(email: str) -> Optional[str]:
    """ایجاد توکن بازیابی رمز عبور برای کاربر"""
    if not db._initialized:
        db._initialize()
    
    session = db.SessionLocal()
    try:
        user = session.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        # تولید توکن و تنظیم زمان انقضا
        token = generate_reset_token()
        user.reset_token = token
        user.reset_token_expiry = datetime.now() + timedelta(hours=1)
        
        session.commit()
        return token
    except Exception as e:
        session.rollback()
        print(f"Error creating reset token: {e}")
        return None
    finally:
        session.close()


def verify_reset_token(token: str) -> Optional[User]:
    """بررسی اعتبار توکن بازیابی رمز عبور"""
    if not db._initialized:
        db._initialize()
    
    session = db.SessionLocal()
    try:
        user = session.query(User).filter(User.reset_token == token).first()
        
        if not user or not user.reset_token_expiry:
            return None
        
        # بررسی انقضای توکن
        if datetime.now() > user.reset_token_expiry:
            return None
        
        return user
    finally:
        session.close()


def reset_password(token: str, new_password: str) -> bool:
    """بازیابی رمز عبور با استفاده از توکن"""
    if not db._initialized:
        db._initialize()
    
    session = db.SessionLocal()
    try:
        user = session.query(User).filter(User.reset_token == token).first()
        
        if not user or not user.reset_token_expiry:
            return False
        
        # بررسی انقضای توکن
        if datetime.now() > user.reset_token_expiry:
            return False
        
        # تنظیم رمز عبور جدید
        user.password_hash = hash_password(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error resetting password: {e}")
        return False
    finally:
        session.close()


def send_password_reset_email(email: str, token: str, base_url: str):
    """ارسال ایمیل بازیابی رمز عبور"""
    try:
        reset_link = f"{base_url}/reset-password/{token}"
        
        msg = Message(
            'بازیابی رمز عبور - سیستم حسابرسی',
            recipients=[email]
        )
        
        msg.body = f"""
سلام،

برای بازیابی رمز عبور خود بر روی لینک زیر کلیک کنید:

{reset_link}

این لینک به مدت 1 ساعت معتبر است.

اگر شما این درخواست را ارسال نکرده‌اید، این ایمیل را نادیده بگیرید.

با تشکر،
تیم سیستم حسابرسی
"""
        
        msg.html = f"""
        <html dir="rtl">
        <body style="font-family: Tahoma, Arial, sans-serif; direction: rtl; text-align: right;">
            <h2>بازیابی رمز عبور</h2>
            <p>سلام،</p>
            <p>برای بازیابی رمز عبور خود بر روی دکمه زیر کلیک کنید:</p>
            <p style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" 
                   style="background-color: #007bff; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    بازیابی رمز عبور
                </a>
            </p>
            <p>یا این لینک را در مرورگر خود کپی کنید:</p>
            <p><a href="{reset_link}">{reset_link}</a></p>
            <p><strong>توجه:</strong> این لینک به مدت 1 ساعت معتبر است.</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                اگر شما این درخواست را ارسال نکرده‌اید، این ایمیل را نادیده بگیرید.
            </p>
        </body>
        </html>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def get_all_users():
    """دریافت لیست تمام کاربران"""
    if not db._initialized:
        db._initialize()
    
    session = db.SessionLocal()
    try:
        users = session.query(User).order_by(User.created_at.desc()).all()
        return users
    finally:
        session.close()


def update_user(user_id: int, **kwargs) -> bool:
    """به‌روزرسانی اطلاعات کاربر"""
    if not db._initialized:
        db._initialize()
    
    session = db.SessionLocal()
    try:
        user = session.query(User).get(user_id)
        if not user:
            return False
        
        # فیلدهای قابل به‌روزرسانی
        allowed_fields = ['full_name', 'email', 'is_active', 'is_admin']
        
        for key, value in kwargs.items():
            if key in allowed_fields and hasattr(user, key):
                setattr(user, key, value)
        
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error updating user: {e}")
        return False
    finally:
        session.close()


def delete_user(user_id: int) -> bool:
    """حذف کاربر"""
    if not db._initialized:
        db._initialize()
    
    session = db.SessionLocal()
    try:
        user = session.query(User).get(user_id)
        if not user:
            return False
        
        session.delete(user)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error deleting user: {e}")
        return False
    finally:
        session.close()


def change_password(user_id: int, old_password: str, new_password: str) -> bool:
    """تغییر رمز عبور کاربر"""
    if not db._initialized:
        db._initialize()
    
    session = db.SessionLocal()
    try:
        user = session.query(User).get(user_id)
        if not user:
            return False
        
        # بررسی صحت رمز عبور قدیمی
        if not check_password(user.password_hash, old_password):
            return False
        
        # تنظیم رمز عبور جدید
        user.password_hash = hash_password(new_password)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error changing password: {e}")
        return False
    finally:
        session.close()
