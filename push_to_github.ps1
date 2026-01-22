# راهنمای آماده Push به GitHub
# ====================================

Write-Host "🚀 آماده‌سازی برای Push به GitHub" -ForegroundColor Cyan
Write-Host ""

# درخواست نام کاربری GitHub
Write-Host "لطفاً نام کاربری GitHub خود را وارد کنید:" -ForegroundColor Yellow
$username = Read-Host "نام کاربری"

if ([string]::IsNullOrWhiteSpace($username)) {
    Write-Host "❌ نام کاربری خالی است!" -ForegroundColor Red
    exit 1
}

# درخواست نام repository
Write-Host ""
Write-Host "نام repository را وارد کنید (پیشنهاد: audit-testing-system):" -ForegroundColor Yellow
$repoName = Read-Host "نام repository"

if ([string]::IsNullOrWhiteSpace($repoName)) {
    $repoName = "audit-testing-system"
    Write-Host "از نام پیش‌فرض استفاده می‌شود: $repoName" -ForegroundColor Gray
}

# URL ایجاد repository
$createRepoUrl = "https://github.com/new"
$repoUrl = "https://github.com/$username/$repoName.git"

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "📋 مراحل لازم:" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""
Write-Host "1️⃣  ابتدا repository را در GitHub ایجاد کنید:" -ForegroundColor Yellow
Write-Host "   👉 $createRepoUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "2️⃣  تنظیمات repository:" -ForegroundColor Yellow
Write-Host "   - Repository name: $repoName" -ForegroundColor White
Write-Host "   - Description: Comprehensive Audit Testing System with 61 Tests" -ForegroundColor White
Write-Host "   - Public یا Private (به انتخاب شما)" -ForegroundColor White
Write-Host "   - ⚠️  هیچ فایلی را اضافه نکنید (README, .gitignore, license)" -ForegroundColor Red
Write-Host ""
Write-Host "3️⃣  بعد از ایجاد repository، به این اسکریپت برگردید" -ForegroundColor Yellow
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green

Write-Host ""
$continue = Read-Host "آیا repository را ایجاد کردید؟ (y/n)"

if ($continue -ne 'y' -and $continue -ne 'Y') {
    Write-Host "❌ لغو شد. لطفاً ابتدا repository را ایجاد کنید." -ForegroundColor Red
    Write-Host "🔗 $createRepoUrl" -ForegroundColor Cyan
    exit 0
}

Write-Host ""
Write-Host "🔧 در حال تنظیم remote..." -ForegroundColor Cyan

# حذف remote قبلی اگر وجود دارد
git remote remove origin 2>$null

# اضافه کردن remote جدید
try {
    git remote add origin $repoUrl
    Write-Host "✅ Remote اضافه شد: $repoUrl" -ForegroundColor Green
} catch {
    Write-Host "❌ خطا در اضافه کردن remote!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# تغییر نام branch به main
Write-Host ""
Write-Host "🔧 تغییر نام branch به main..." -ForegroundColor Cyan
git branch -M main
Write-Host "✅ Branch به main تغییر یافت" -ForegroundColor Green

# نمایش remote
Write-Host ""
Write-Host "📡 Remote URLs:" -ForegroundColor Cyan
git remote -v

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "🚀 آماده برای Push!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""

$push = Read-Host "آیا می‌خواهید الان push کنید؟ (y/n)"

if ($push -eq 'y' -or $push -eq 'Y') {
    Write-Host ""
    Write-Host "📤 در حال Push..." -ForegroundColor Cyan
    Write-Host ""
    
    try {
        git push -u origin main
        
        Write-Host ""
        Write-Host "=" * 60 -ForegroundColor Green
        Write-Host "🎉 موفقیت! پروژه به GitHub آپلود شد!" -ForegroundColor Green
        Write-Host "=" * 60 -ForegroundColor Green
        Write-Host ""
        Write-Host "🔗 لینک repository شما:" -ForegroundColor Cyan
        Write-Host "   https://github.com/$username/$repoName" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "📊 محتویات آپلود شده:" -ForegroundColor Cyan
        Write-Host "   ✅ 87 فایل" -ForegroundColor White
        Write-Host "   ✅ 11,229+ خط کد" -ForegroundColor White
        Write-Host "   ✅ 61 آزمون حسابرسی" -ForegroundColor White
        Write-Host "   ✅ Web UI کامل" -ForegroundColor White
        Write-Host "   ✅ مستندات فارسی و انگلیسی" -ForegroundColor White
        Write-Host ""
        
        # باز کردن repository در مرورگر
        $openBrowser = Read-Host "آیا می‌خواهید repository را در مرورگر باز کنید؟ (y/n)"
        if ($openBrowser -eq 'y' -or $openBrowser -eq 'Y') {
            Start-Process "https://github.com/$username/$repoName"
        }
        
    } catch {
        Write-Host ""
        Write-Host "❌ خطا در Push!" -ForegroundColor Red
        Write-Host ""
        Write-Host "احتمالاً نیاز به احراز هویت دارید:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "💡 راه‌حل 1: Personal Access Token" -ForegroundColor Cyan
        Write-Host "   1. به https://github.com/settings/tokens بروید" -ForegroundColor White
        Write-Host "   2. Generate new token (classic)" -ForegroundColor White
        Write-Host "   3. دسترسی 'repo' را انتخاب کنید" -ForegroundColor White
        Write-Host "   4. Token را کپی کنید" -ForegroundColor White
        Write-Host "   5. دوباره git push را اجرا کنید" -ForegroundColor White
        Write-Host "   6. به جای رمز عبور، token را وارد کنید" -ForegroundColor White
        Write-Host ""
        Write-Host "💡 راه‌حل 2: GitHub CLI" -ForegroundColor Cyan
        Write-Host "   gh auth login" -ForegroundColor White
        Write-Host ""
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
} else {
    Write-Host ""
    Write-Host "⏸️  Push لغو شد." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "برای Push دستی، دستور زیر را اجرا کنید:" -ForegroundColor Cyan
    Write-Host "   git push -u origin main" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Write-Host "📚 برای راهنمای کامل، فایل GITHUB_DEPLOY_GUIDE.md را مطالعه کنید" -ForegroundColor Gray
Write-Host ""
