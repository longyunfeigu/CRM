from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
import json

from king_admin.forms import LoginForm
from utils.BaseObject.myResponse import BaseReponse
from utils.json_encode import JsonCustomEncode
from utils.captcha.mycaptcha import Captcha


# Create your views here.

def acc_login(request):
    if request.method == 'GET':
        obj_form = LoginForm()
        return render(request, 'login.html', {'obj_form': obj_form})
    else:
        response_obj = BaseReponse()
        obj_form = LoginForm(request.POST)
        if obj_form.is_valid():
            email = obj_form.cleaned_data.get('email', None)
            password = obj_form.cleaned_data.get('password', None)
            remember = obj_form.cleaned_data.get('remember', None)
            user = authenticate(username=email, password=password)
            if user:
                login(request, user)
                if remember:
                    request.session.set_expiry(None)
                else:
                    request.session.set_expiry(0)
                next_url = request.GET.get('next', '/')
                response_obj.data = next_url
                # if next_url:
                #     return redirect(next_url)
                # else:
                #     print('------- ok')
                #     return redirect(reverse('sales_index'))
            else:
                response_obj.status = False
                response_obj.errors = '用户名密码错误'
        else:
            response_obj.status = False
            response_obj.errors = obj_form.errors.as_data()
        try:
            response = json.dumps(response_obj.__dict__, cls=JsonCustomEncode)
        except TypeError as e:
            response_obj.errors = '请输入邮箱和密码'
            response = json.dumps(response_obj.__dict__, cls=JsonCustomEncode)
        return HttpResponse(response)

def acc_logout(request):
    logout(request)
    return redirect("/account/login/")


try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO


def captcha(request):
    text, image = Captcha.gene_code()
    # image.save('text.png','png') # I/0
    # 需要通过StringIO这个类来把图片当成流的形式返回给客户端
    out = StringIO()  # 获取"管道"
    image.save(out, 'png')  # 把图片保存到管道中
    out.seek(0)  # 移动文件指针到\第0个位置
    response = HttpResponse(content_type='image/png')
    response.write(out.read())
    # 把验证码数据写入到缓存中,过期时间是2分钟
    # key = text.lower()
    # value = key
    # cache.set(key,value,120)
    return response

def test(request):
    from utils.message import sendMessage
    sendMessage('ppp', '<a href="#">点击</a>','2514553187@qq.com')
    print('ooo')

def index(request):
    return render(request, 'index.html')