# 🚀 راهنمای آپلود پروژه به GitHub

## ✅ مرحله 1: ایجاد Repository در GitHub (انجام شده در سیستم شما)

Repository محلی شما آماده است! 

```
✅ Git initialized
✅ All files added (87 files, 11,229 lines)
✅ First commit created
```

---

## 📝 مرحله 2: ایجاد Repository در GitHub

### گزینه الف: از طریق وب‌سایت GitHub

1. به [GitHub.com](https://github.com) بروید و وارد حساب خود شوید
2. روی دکمه **"+"** در بالای صفحه کلیک کنید
3. **"New repository"** را انتخاب کنید
4. تنظیمات زیر را انجام دهید:
   - **Repository name**: `audit-testing-system` (یا هر نام دیگری)
   - **Description**: `Comprehensive Audit Testing System with 61 Professional Tests`
   - **Visibility**: Public یا Private (به انتخاب شما)
   - **⚠️ مهم**: چک‌باکس‌های زیر را **خالی** بگذارید:
     - ❌ Add a README file
     - ❌ Add .gitignore
     - ❌ Choose a license
5. روی **"Create repository"** کلیک کنید

### گزینه ب: از طریق GitHub CLI (اگر نصب دارید)

```powershell
gh repo create audit-testing-system --public --source=. --remote=origin --push
```

---

## 🔗 مرحله 3: اتصال به GitHub و Push

پس از ایجاد repository در GitHub، دستورات زیر را اجرا کنید:

### اگر از HTTPS استفاده می‌کنید (توصیه می‌شود):

```powershell
# جایگزین کردن YOUR_USERNAME با نام کاربری GitHub خود
git remote add origin https://github.com/YOUR_USERNAME/audit-testing-system.git

# تغییر نام branch به main (استاندارد جدید GitHub)
git branch -M main

# Push کردن کد
git push -u origin main
```

### اگر از SSH استفاده می‌کنید:

```powershell
# جایگزین کردن YOUR_USERNAME با نام کاربری GitHub خود
git remote add origin git@github.com:YOUR_USERNAME/audit-testing-system.git

# تغییر نام branch به main
git branch -M main

# Push کردن کد
git push -u origin main
```

---

## 🔐 احراز هویت GitHub

### اگر از HTTPS استفاده می‌کنید:

GitHub دیگر از رمز عبور معمولی پشتیبانی نمی‌کند. باید از **Personal Access Token** استفاده کنید:

1. به [GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)](https://github.com/settings/tokens) بروید
2. **"Generate new token (classic)"** را بزنید
3. دسترسی‌های زیر را انتخاب کنید:
   - ✅ `repo` (Full control of private repositories)
4. روی **"Generate token"** کلیک کنید
5. **توکن را کپی کنید** (فقط یک بار نمایش داده می‌شود!)
6. هنگام push، به جای رمز عبور از این توکن استفاده کنید

### اگر از SSH استفاده می‌کنید:

باید کلید SSH خود را به GitHub اضافه کنید:

1. ایجاد کلید SSH (اگر ندارید):
   ```powershell
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```
2. کپی کردن کلید عمومی:
   ```powershell
   Get-Content ~/.ssh/id_ed25519.pub | clip
   ```
3. افزودن به GitHub: [Settings > SSH and GPG keys > New SSH key](https://github.com/settings/ssh/new)

---

## 📋 دستورات کامل (کپی-پیست آماده)

پس از ایجاد repository در GitHub، این دستورات را اجرا کنید:

```powershell
# 1. اتصال به GitHub (جایگزین YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/audit-testing-system.git

# 2. بررسی اتصال
git remote -v

# 3. تغییر نام branch به main
git branch -M main

# 4. Push کردن
git push -u origin main
```

---

## ✨ پس از Push موفقیت‌آمیز

Repository شما در GitHub قابل مشاهده خواهد بود:
```
https://github.com/YOUR_USERNAME/audit-testing-system
```

### محتویات Repository:
- ✅ 87 فایل
- ✅ 11,229+ خط کد
- ✅ 61 آزمون حسابرسی
- ✅ Web UI کامل
- ✅ مستندات جامع فارسی و انگلیسی

---

## 🎨 توصیه: اضافه کردن Topics به Repository

در صفحه اصلی repository خود در GitHub:

1. روی ⚙️ **Settings** کلیک کنید
2. در بخش **About** روی **⚙️** کلیک کنید
3. Topics زیر را اضافه کنید:
   ```
   audit, fraud-detection, benford-law, python, flask, 
   accounting, financial-analysis, data-analysis, 
   sqlalchemy, audit-tests, persian, farsi
   ```

---

## 📱 اضافه کردن Badge به README

می‌توانید badge‌های زیر را به README.md اضافه کنید:

```markdown
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Tests](https://img.shields.io/badge/tests-61-brightgreen.svg)
```

---

## 🔄 دستورات مفید برای آینده

### برای commit‌های بعدی:
```powershell
git add .
git commit -m "توضیحات تغییرات"
git push
```

### برای مشاهده وضعیت:
```powershell
git status
```

### برای مشاهده تاریخچه:
```powershell
git log --oneline
```

### برای ایجاد branch جدید:
```powershell
git checkout -b feature/new-test
```

---

## ❓ رفع مشکلات رایج

### خطا: "remote origin already exists"
```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/audit-testing-system.git
```

### خطا: "Authentication failed"
- از Personal Access Token به جای رمز عبور استفاده کنید
- یا از SSH استفاده کنید

### خطا: "Updates were rejected"
```powershell
git pull origin main --rebase
git push
```

---

## 🎉 موفق باشید!

پروژه شما آماده است! فقط کافی است:
1. Repository در GitHub ایجاد کنید
2. دستورات بالا را اجرا کنید
3. کد شما در GitHub منتشر می‌شود!

---

**نکته امنیتی**: ⚠️ قبل از push، مطمئن شوید که:
- فایل `config.py` اطلاعات حساس ندارد
- فایل `.gitignore` درست کار می‌کند
- فایل `.env` در `.gitignore` است
