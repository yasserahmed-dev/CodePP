from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

import random
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from Login.models import CodeOTP

# Create your views here.

# صفحة الملف الشخصي
@login_required(login_url='login')
def profile(request):
    return render(request, 'Profile/profile.html')


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

        messages.success(request, ' تم تحديث الملف الشخصي بنجاح.')
        return redirect('profile')

    return render(request, 'Profile/edit_profile.html')


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

        # تسجيل الدخول بعد تغيير كلمة المرور
        user = User.objects.get(email=user.email)
        user_auth = authenticate(request, username=user.username, password=new_password)
        login(request, user_auth)
        messages.success(request, ' تم تغيير كلمة المرور بنجاح.')
        return redirect('profile')

    return render(request, 'Profile/change_password.html')


# طلب إرسال كود حذف الحساب
@login_required(login_url='login')
def delete_account_request(request):
    if request.method == 'POST':
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
        messages.success(request, ' تم إرسال كود التحقق إلى بريدك الإلكتروني.')
        return redirect('verify_delete')

    return render(request, 'Profile/delete_account.html')


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

    return render(request, 'Profile/delete_account_verify.html')
