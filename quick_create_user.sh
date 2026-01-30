#!/bin/bash
# اسکریپت سریع برای ایجاد کاربر در سرور

# استفاده:
# ./quick_create_user.sh username email password "Full Name" [admin]

if [ $# -lt 3 ]; then
    echo "استفاده:"
    echo "./quick_create_user.sh <username> <email> <password> [full_name] [admin]"
    echo ""
    echo "مثال:"
    echo "./quick_create_user.sh babak babak@example.com pass123 'بابک صفاآب‌هار' admin"
    exit 1
fi

USERNAME=$1
EMAIL=$2
PASSWORD=$3
FULLNAME=${4:-""}
IS_ADMIN=${5:-""}

if [ "$IS_ADMIN" = "admin" ]; then
    IS_ADMIN_FLAG="True"
else
    IS_ADMIN_FLAG="False"
fi

# اجرا در سرور
ssh root@107.173.196.121 "cd /opt/audit-testing-system && source venv/bin/activate && python -c \"
from auth import create_user
user = create_user('$USERNAME', '$EMAIL', '$PASSWORD', '$FULLNAME', $IS_ADMIN_FLAG)
if user:
    print('✅ کاربر $USERNAME با موفقیت ایجاد شد!')
    print('نقش:', 'مدیر' if user.is_admin else 'کاربر عادی')
else:
    print('❌ خطا: نام کاربری یا ایمیل تکراری است!')
\""

echo ""
echo "🔗 آدرس لاگین: http://107.173.196.121:8000/login"
echo "👤 نام کاربری: $USERNAME"
echo "🔑 رمز عبور: $PASSWORD"
