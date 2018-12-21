from django.conf import settings
from django.core.mail import send_mail
import time

#django环境的初始化
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")


#使用celery
from celery import Celery
#创建一个Celery类的实例对象
app = Celery('celery_tasks.tasks',broker='redis://:plmokn10241118@*:6379/8')
#定义任务函数
@app.task
def send_register_active_email(to_email,username,token):
    """发送激活邮件"""
    # 组织邮件信息
    subject = "天天生鲜,欢迎信息"
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = "<h1>%s,欢迎您成为天天生鲜会员</h1>请点击下面的链接激活您的账户<br><a href='http://127.0.0.1:8000/user/active/%s'>http://127.0.0.1:8000/user/active/%s</a>" % (
    username, token, token)
    send_mail(subject, message, sender, receiver, html_message=html_message)
    time.sleep(5)

