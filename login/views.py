from django.contrib.auth import get_user_model, authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import random

from .models import CodeOTP

User = get_user_model()


# تسجيل الدخول
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'مرحباً {user.first_name} 👋 تم تسجيل الدخول بنجاح.')
                return redirect('home')
            else:
                messages.error(request, 'كلمة المرور غير صحيحة.')
        except User.DoesNotExist:
            messages.error(request, 'البريد الإلكتروني غير موجود.')
    return render(request, 'login/login.html')


# تسجيل الخروج
def logout_view(request):
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح.')
    return redirect('home')


# إنشاء حساب جديد
def signup(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        terms = request.POST.get('terms')

        if not terms:
            messages.error(request, 'يجب الموافقة على الشروط والأحكام.')
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'البريد الإلكتروني موجود بالفعل.')
            return redirect('signup')

        if len(password1) < 8:
            messages.error(request, 'كلمة المرور يجب أن تكون 8 أحرف على الأقل.')
            return redirect('signup')

        if password1 != password2:
            messages.error(request, 'كلمتا المرور غير متطابقتين.')
            return redirect('signup')

        User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=email,
            password=password1,
            is_student=True
        )
        messages.success(request, 'تم إنشاء الحساب بنجاح. يمكنك الآن تسجيل الدخول.')
        return redirect('login')

    return render(request, 'login/signup.html')


# طلب إرسال كود استعادة كلمة المرور
def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not User.objects.filter(email=email).exists():
            messages.error(request, 'البريد الإلكتروني غير موجود.')
            return redirect('reset_password')

        user = User.objects.get(email=email)
        random_code = str(random.randint(1000, 9999))

        # حذف الأكواد القديمة
        CodeOTP.objects.filter(user=user).delete()
        CodeOTP.objects.create(user=user, code=random_code)

        send_mail(
            subject='🔐 كود استعادة كلمة المرور',
            message=f'استخدم الكود التالي لتغيير كلمة المرور الخاصة بك:\n\n{random_code}\n\nفريق Code++',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        request.session['reset_email'] = email
        messages.success(request, '✅ تم إرسال الكود إلى بريدك الإلكتروني.')
        return redirect('verify_otp')

    return render(request, 'login/password_reset.html')


# التحقق من الكود
def verify_otp(request):
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        email = request.session.get('reset_email')

        if not email:
            messages.error(request, 'انتهت صلاحية الجلسة. الرجاء إعادة المحاولة.')
            return redirect('reset_password')

        try:
            user = User.objects.get(email=email)
            code_obj = CodeOTP.objects.get(user=user, code=otp_code)
            code_obj.delete()  # حذف الكود بعد الاستخدام
            messages.success(request, '✅ تم التحقق من الكود بنجاح.')
            return redirect('reset_password_form')
        except CodeOTP.DoesNotExist:
            messages.error(request, 'كود التحقق غير صحيح أو منتهي الصلاحية.')

    return render(request, 'login/otp_verify.html')


# إعادة تعيين كلمة المرور بعد التحقق
def reset_password_form(request):
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, 'انتهت صلاحية الجلسة. الرجاء إعادة المحاولة.')
        return redirect('reset_password')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, 'كلمتا المرور غير متطابقتين.')
            return redirect('reset_password_form')

        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        del request.session['reset_email']

        messages.success(request, '🔒 تم تغيير كلمة المرور بنجاح. يمكنك الآن تسجيل الدخول.')
        return redirect('login')

    return render(request, 'login/reset_password_form.html')
