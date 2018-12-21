from django.shortcuts import render,redirect,HttpResponse

# Create your views here.
import re
from .models import User
from django.views.generic import View
from django.core.urlresolvers import reverse
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from django.core.mail import send_mail
import time
from celery_tasks.tasks import send_register_active_email
from django.contrib.auth import authenticate,login

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

        # 发送激活邮件,包含激活链接
        # 激活链接中需要包含用户的身份信息,并且把身份信息进行加密
        # 加密用户的身份信息，生成激活token
        serializer = Serializer(settings.SECRET_KEY,3600)
        info = {"confirm":user.id}
        serializer.dumps(info)

        # 4.返回应答
        return redirect(reverse('goods:index'))

class RegisterView(View):
    def get(self,request):
        return render(request,"register.html")
    def post(self,request):
        # 注册通用处理流程
        # 1.接收数据
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")
        allow = request.POST.get("allow")
        # 2.数据校验
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {"errmsg": "数据不完整"})
        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {"errmsg": "邮箱格式不正确"})
        # 校验是否同意了协议
        if allow != 'on':
            return render(request, "register.html", {"errmsg": "请同意协议"})
        # 　校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None
        if user:
            # 用户名已存在
            return render(request, 'register.html', {"errmsg": "用户名已存在"})
        # 3.进行业务处理:进行数据校验
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 发送激活邮件,包含激活链接
        # 激活链接中需要包含用户的身份信息,并且把身份信息进行加密
        # 加密用户的身份信息，生成激活token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {"confirm": user.id}
        token = serializer.dumps(info) # bytes类型数据
        token = token.decode("utf8")
        #　发送邮件
        send_register_active_email.delay(email,username,token)
        # 4.返回应答
        return redirect(reverse('goods:index'))



class ActiveView(View):
    """用户激活"""
    def get(self,request,token):
        """用户进行激活"""
        #进行解密，获取要激活的用户信息
        serializer = Serializer(settings.SECRET_KEY,3600)
        try:
            info = serializer.loads(token)
            #获取待激活用户的ID
            user_id = info["confirm"]
            # 根据id获取用户信息,将激活标记改为１.
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            #激活后，跳转到登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse("激活链接已过期")

class LoginView(View):
    def get(self,request):
        """显示登录页面"""
        #判断是否记住了用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = "checked"
        else:
            username = ''
            checked = ''
        #使用模板
        return render(request,"login.html",{"username":username,"checked":checked})
    def post(self,request):
        """登录校验"""
        #接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        #校验数据
        if not all([username,password]):
            return render(request,'login.html',{"errmsg":"数据不完整"})
        #业务处理:登录校验
        user = authenticate(username=username,password=password)
        if user is not None:
            # 用户名密码正确
            if user.is_active:
                #用户已激活
                #记录用户状态
                login(request,user)

                #跳转到首页
                response = redirect(reverse("goods:index")) # HttpResponseRedirect
                # 判断是否需要记住用户名
                remember = request.POST.get("remember")
                if remember == 'on':
                    response.set_cookie('username',username,max_age=7*24*3600)
                else:
                    response.delete_cookie('username')
                #返回response
                return response

                return
            else:
                #账户未激活
                return render(request,'login.html',{"errmsg":"账户未激活"})
        else:
            #用户名或密码错误
            return render(request,'login.html',{"errmsg":"用户名或密码错误"})
        #返回应答