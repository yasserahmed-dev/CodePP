import random
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from login.models import CodeOTP  # نفس النموذج المستخدم لكود OTP

User = get_user_model()


# صفحات الخطأ
def error_400(request, exception=None):
    return render(request, '400.html', status=400)

def error_403(request, exception=None):
    return render(request, '403.html', status=403)

def error_404(request, exception=None):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)


# الصفحة الرئيسية
def home(request):
    return render(request, 'CodePP/home.html')


# الملف الشخصي
@login_required(login_url='login')
def profile(request):
    return render(request, 'CodePP/profile/profile.html')


# تعديل الملف الشخصي
@login_required(login_url='login')
def edit_profile(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = email  # تحديث اسم المستخدم إذا كان email
        user.save()

        messages.success(request, '✅ تم تحديث الملف الشخصي بنجاح.')
        return redirect('profile')

    return render(request, 'CodePP/profile/edit_profile.html')


# تغيير كلمة المرور
@login_required(login_url='login')
def change_password(request):    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            messages.error(request, 'كلمة المرور الحالية غير صحيحة.')
            return redirect('change_password')

        if new_password != confirm_password:
            messages.error(request, 'كلمتا المرور غير متطابقتين.')
            return redirect('change_password')

        if len(new_password) < 8:
            messages.error(request, 'كلمة المرور يجب أن تكون 8 أحرف على الأقل.')
            return redirect('change_password')

        # تحديث كلمة المرور بشكل آمن
        user = request.user
        user.set_password(new_password)
        user.save()

        messages.success(request, '✅ تم تغيير كلمة المرور بنجاح.')
        return redirect('profile')

    return render(request, 'CodePP/profile/change_password.html')


# طلب إرسال كود حذف الحساب
@login_required(login_url='login')
def delete_account_request(request):
    if request.method == 'GET':
        user = request.user
        random_code = str(random.randint(1000, 9999))
        
        # حذف الأكواد القديمة
        CodeOTP.objects.filter(user=user).delete()
        CodeOTP.objects.create(user=user, code=random_code)

        send_mail(
            subject='🔐 كود حذف الحساب',
            message=f'استخدم الكود التالي لتأكيد حذف حسابك:\n\n{random_code}\n\nفريق Code++',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )

        request.session['delete_email'] = user.email
        messages.success(request, '✅ تم إرسال كود التحقق إلى بريدك الإلكتروني.')
        return redirect('delete_account_verify')

    return redirect('profile')


# التحقق من كود حذف الحساب
@login_required(login_url='login')
def delete_account_verify(request):
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        email = request.session.get('delete_email')

        if not email:
            messages.error(request, 'انتهت صلاحية الجلسة. الرجاء إعادة المحاولة.')
            return redirect('delete_account')

        try:
            user = User.objects.get(email=email)
            code_obj = CodeOTP.objects.get(user=user, code=otp_code)
            code_obj.delete()  # حذف الكود بعد الاستخدام
            user.delete()
            del request.session['delete_email']
            messages.success(request, 'تم حذف الحساب بنجاح.')
            return redirect('home')
        except CodeOTP.DoesNotExist:
            messages.error(request, 'الكود غير صحيح أو منتهي الصلاحية.')

    return render(request, 'CodePP/profile/delete_account_verify.html')
