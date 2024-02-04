import requests
import json
from django.shortcuts import render, get_object_or_404, redirect, reverse
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
        'callback_url': request.build_absolute_uri(reverse('payment_callback'))
    }
    res = requests.post(zarinpal_req_url, data=json.dumps(request_data), headers=request_headers)

    data = res.json()['data']
    authority = data['authority']
    order.authority = authority
    order.save()
    if len(res.json()['errors']) == 0:
        return redirect(f'https://www.zarinpal.com/pg/StartPay/{authority}')
    else:
        return HttpResponse(res.json()['errors'])

def payment_callback(request):
    payment_authority = request.GET.get('Authority')
    payment_status = request.GET.get('Status')

    order = get_object_or_404(Order, authority=payment_authority)
    toman_total_price = order.get_total_price()
    rial_total_price = toman_total_price * 10

    if payment_status == 'OK':
        request_headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
        }

        request_data = {
            "merchant_id": settings.ZARIN_PAL_MERCHANT_ID,
            'amount': rial_total_price,
            'authority': payment_authority
        }
        res = requests.post('https://api.zarinpal.com/pg/v4/payment/verify.json', data=json.dumps(request_data),
                            headers=request_headers)

        if 'data' in res.json() and len(res.json()['errors']) == 0:
            data = res.json()['data']
            payment_status_code = data['status']
            if payment_status_code == 100:
                order.paid = True
                order.ref_id = data['ref_id']
                order.zarinpal_data = data
                order.save()
                return HttpResponse("Payment successful")
            elif payment_status_code == 101:
                return HttpResponse("Payment was success but the order was duplicated. ")
            else:
                return HttpResponse("Payment was not successful", res.json()['errors']['code'],
                                    res.json()['errors']['message'])
    else:
        return HttpResponse("ناموفق")


# def payment_process_sandbox(request):
#     #  get order id to pay
#     order_id = request.session.get('order_id')
#     order = get_object_or_404(Order, id=order_id)
#
#     toman_total_price = order.get_total_price()
#     rial_total_price = toman_total_price * 10
#
#     zarinpal_req_url = "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
#
#     request_headers = {
#         'accept': 'application/json',
#         'content-type': 'application/json',
#     }
#     request_data = {
#         "MerchantID": 'abcdAbcabcdAbcabscdAbcabcdAbcabcdAbc',
#         'Amount': rial_total_price,
#         'Description': f'#{order.id}: {order.user.first_name} {order.user.last_name} ',
#         'CallbackURL': request.build_absolute_uri(reverse('payment_callback'))
#     }
#     res = requests.post(zarinpal_req_url, data=json.dumps(request_data), headers=request_headers)
#     data = res.json()
#
#     authority = data['Authority']
#     order.authority = authority
#     order.save()
#     return redirect(f'https://sandbox.zarinpal.com/pg/StartPay/{authority}')


# def payment_callback_sandbox(request):
#     payment_authority = request.GET.get('Authority')
#     payment_status = request.GET.get('Status')
#
#     order = get_object_or_404(Order, authority=payment_authority)
#     toman_total_price = order.get_total_price()
#     rial_total_price = toman_total_price * 10
#
#     if payment_status == 'OK':
#         request_headers = {
#             'accept': 'application/json',
#             'content-type': 'application/json',
#         }
#
#         request_data = {
#             "MerchantID": 'abcdAbcabcdAbcabscdAbcabcdAbcabcdAbc',
#             'Amount': rial_total_price,
#             'Authority': payment_authority
#         }
#         res = requests.post('https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json',
#                             data=json.dumps(request_data),
#                             headers=request_headers)
#
#         data = res.json()
#         payment_status_code = data['Status']
#         if payment_status_code == 100:
#             order.paid = True
#             order.ref_id = data['RefID']
#             order.zarinpal_data = data
#             order.save()
#             return HttpResponse("Payment successful")
#         elif payment_status_code == 101:
#             return HttpResponse("Payment was success but the order was duplicated. ")
#         else:
#             return HttpResponse("Payment was not successful", res.json()['errors']['code'],
#                                 res.json()['Errors']['message'])
#     else:
#         return HttpResponse("ناموفق")
