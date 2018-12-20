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
        subject = "天天生鲜,欢迎信息"
        message = ''
        sender = settings.EMAIL_FROM
        receiver = [email]
        html_message = "<h1>%s,欢迎您成为天天生鲜会员</h1>请点击下面的链接激活您的账户<br><a href='http://127.0.0.1:8000/user/active/%s'>http://127.0.0.1:8000/user/active/%s</a>"%(username,token,token)
        send_mail(subject,message,sender,receiver,html_message=html_message)

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
        return render(request,"login.html")