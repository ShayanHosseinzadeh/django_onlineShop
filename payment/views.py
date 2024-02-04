import requests
import json
from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse

from orders.models import Order
from django.conf import settings


def payment_process(request):
    #  get order id to pay
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    toman_total_price = order.get_total_price()
    rial_total_price = toman_total_price * 10

    zarinpal_req_url = "https://api.zarinpal.com/pg/v4/payment/request.json"

    request_headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
    }
    request_data = {
        "merchant_id": settings.ZARIN_PAL_MERCHANT_ID,
        'amount': rial_total_price,
        'description': f'#{order.id}: {order.user.first_name} {order.user.last_name} ',
        'callback_url': 'http://127.0.0.1:8000'
    }
    res = requests.post(zarinpal_req_url, data=json.dumps(request_data), headers=request_headers)

    data = res.json()['data']
    authority = data['authority']
    order.authority = authority
    order.save()
    if len(res.json()['errors']) ==0:
        return redirect(f'https://www.zarinpal.com/pg/StartPay/{authority}')
    else:
        return HttpResponse(res.json()['errors'])

