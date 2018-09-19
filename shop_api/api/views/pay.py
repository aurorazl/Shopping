from django.shortcuts import render,redirect,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from utils.pay import AliPay
import time
from django.conf import settings

def aliPay():
    # 沙箱测试地址：https://openhome.alipay.com/platform/appDaily.htm?tab=info
    # 支付相关配置
    APPID = "2016092200570009"
    NOTIFY_URL = "http://127.0.0.1:8001/update_order/"   # 需公网IP
    RETURN_URL = "http://127.0.0.1:8001/pay_result/"
    PRI_KEY_PATH = "api/keys/app_private_2048.txt"
    PUB_KEY_PATH = "api/keys/alipay_public_2048.txt"

    obj = AliPay(
        appid=settings.APPID,
        app_notify_url=settings.NOTIFY_URL,  # 如果支付成功，支付宝会向这个地址发送POST请求（校验是否支付已经完成）
        return_url=settings.RETURN_URL,  # 如果支付成功，重定向回到你的网站的地址。
        alipay_public_key_path=settings.PUB_KEY_PATH,  # 支付宝公钥
        app_private_key_path=settings.PRI_KEY_PATH,  # 应用私钥
        debug=True,  # 默认False,
    )
    return obj

def index(request):
    if request.method == 'GET':
        return render(request,'index.html')

    alipay = aliPay()
    # 对购买的数据进行加密
    money = float(request.POST.get('price'))        # 拿到浮点型小数
    out_trade_no = "x2" + str(time.time())          # 随机生成的订单号
    # 1. 在数据库创建一条数据：状态（待支付）
    # 2. 创建加密的数据，然后放到url发送给支付宝
    query_params = alipay.direct_pay(
        subject="充气式韩红",  # 商品简单描述
        out_trade_no= out_trade_no,  # 商户订单号，支付完成后支付宝会返回订单号
        total_amount=money,  # 交易金额(单位: 元 保留俩位小数)
    )
    pay_url = "https://openapi.alipaydev.com/gateway.do?{}".format(query_params)
    return redirect(pay_url)

def pay_result(request):
    """
    支付完成后，跳转回的地址
    :param request:
    :return:
    """
    params = request.GET.dict()
    sign = params.pop('sign', None) # 获取sign对应的签名，通过verify函数检验

    alipay = aliPay()

    status = alipay.verify(params, sign)    # true or false

    if status:
        return HttpResponse('支付成功')
    return HttpResponse('支付失败')

@csrf_exempt
def update_order(request):
    """
    支付成功后，支付宝向该地址发送的POST请求（用于修改订单状态）
    :param request:
    :return:
    """
    if request.method == 'POST':
        from urllib.parse import parse_qs

        body_str = request.body.decode('utf-8')
        post_data = parse_qs(body_str)

        post_dict = {}
        for k, v in post_data.items():
            post_dict[k] = v[0]         # 解析字典

        alipay = aliPay()

        sign = post_dict.pop('sign', None)
        status = alipay.verify(post_dict, sign)
        if status:
            # 这一步去数据库修改订单状态
            out_trade_no = post_dict.get('out_trade_no')
            print(out_trade_no)
            # 2. 根据订单号将数据库中的数据进行更新
            return HttpResponse('支付成功')
        else:
            return HttpResponse('支付失败')
    return HttpResponse('')