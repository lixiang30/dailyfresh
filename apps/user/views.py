from django.shortcuts import render,redirect

# Create your views here.
import re
from .models import User
from django.core.urlresolvers import reverse


def register(request):
    """用户注册"""
    if request.method =="GET":
        return render(request,'register.html')
    else:
        #注册通用处理流程
        # 1.接收数据
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")
        allow = request.POST.get("allow")
        # 2.数据校验
        if not all([username,password,email]):
            #数据不完整
            return render(request,'register.html',{"errmsg":"数据不完整"})
        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
            return render(request,'register.html',{"errmsg":"邮箱格式不正确"})
        # 校验是否同意了协议
        if allow != 'on':
            return render(request,"register.html",{"errmsg":"请同意协议"})
        #　校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            #用户名不存在
            user = None
        if user:
            #用户名已存在
            return render(request,'register.html',{"errmsg":"用户名已存在"})
        # 3.进行业务处理:进行数据校验
        user = User.objects.create_user(username,email,password)
        user.is_active = 0
        user.save()
        # 4.返回应答
        return redirect(reverse('goods:index'))