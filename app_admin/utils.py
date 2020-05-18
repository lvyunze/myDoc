# utf-8
import smtplib
from django.conf import settings
from email.mime.text import MIMEText
from app_admin.models import SysSetting
import random


def generate_vcode(n=6):
    _num = ''.join(map(str, range(3, 10)))
    vcode_str = ''.join(random.sample(_num, n))
    return vcode_str


def send_email(to_email, vcode_str):
    email_enable = SysSetting.objects.get(types="basic", name='enable_email')
    if email_enable.value == 'on':
        smtp_host = SysSetting.objects.get(types='email', name='smtp_host').value
        send_emailer = SysSetting.objects.get(types='email', name='send_emailer').value
        smtp_port = SysSetting.objects.get(types='email', name='smtp_port').value
        username = SysSetting.objects.get(types='email', name='username').value
        pwd = SysSetting.objects.get(types='email', name='pwd').value
        ssl = SysSetting.objects.get(types='email', name='smtp_ssl').value
        print(smtp_host, smtp_port, send_emailer, username, pwd)

        msg_from = send_emailer
        passwd = dectry(pwd)
        msg_to = to_email
        if ssl:
            s = smtplib.SMTP_SSL(smtp_host, int(smtp_port))
        else:
            s = smtplib.SMTP(smtp_host, int(smtp_host))
        subject = "MrDoc - 重置密码验证码"
        content = "你的验证码为：{}，验证码30分钟内有效！".format(vcode_str)

        msg = MIMEText(content, _subtype='html', _charset='utf-8')
        msg['Subject'] = subject
        msg['From'] = 'MrDoc助手[{}]'.format(msg_from)
        msg['To'] = msg_to
        try:
            s.login(username, passwd)
            s.sendmail(msg_from, msg_to, msg.as_string())
            return True
        except smtplib.SMTPException as e:
            print(repr(e))
            return False
        finally:
            s.quit()
    else:
        return False


def enctry(s):
    k = settings.SECRET_KEY
    encry_str = ""
    for i, j in zip(s, k):
        temp = str(ord(i) + ord(j)) + '_'
        encry_str = encry_str + temp
    return encry_str


def dectry(p):
    k = settings.SECRET_KEY
    dec_str = ""
    for i, j in zip(p.split("_")[:-1], k):
        temp = chr(int(i) - ord(j))
        dec_str = dec_str + temp
    return dec_str
