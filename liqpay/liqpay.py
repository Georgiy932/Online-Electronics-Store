"""
LiqPay Python SDK
~~~~~~~~~~~~~~~~~
supports python 2.7.x version
requires requests module
"""

__title__ = 'LiqPay Python SDK'
__version__ = '1.0'

import base64
from copy import deepcopy
import hashlib
import json
from urllib.parse import urljoin


import requests


def to_unicode(s):
    if isinstance(s, bytes):
        return s.decode('utf-8')
    return str(s)

smart_str = lambda x: to_unicode(x)




class ParamValidationError(Exception):
    pass


class LiqPay(object):
    FORM_TEMPLATE = u'''\
<form method="post" action="{action}" accept-charset="utf-8">
\t{param_inputs}
    <input type="image" src="//static.liqpay.ua/buttons/p1{language}.radius.png" name="btn_text" />
</form>'''
    INPUT_TEMPLATE = u'<input type="hidden" name="{name}" value="{value}"/>'

    SUPPORTED_PARAMS = [
        'public_key', 'amount', 'currency', 'description', 'order_id',
        'result_url', 'server_url', 'type', 'signature', 'language', 'sandbox'
    ]

    def __init__(self, public_key, private_key, host='https://www.liqpay.ua/api/'):
        self._public_key = public_key
        self._private_key = private_key
        self._host = host

    def _make_signature(self, *args):
        joined_fields = ''.join(str(x) for x in args)
        return base64.b64encode(hashlib.sha1(joined_fields.encode('utf-8')).digest()).decode('utf-8')

    def _prepare_params(self, params):
        params = {} if params is None else deepcopy(params)
        params.update(public_key=self._public_key)
        return params

    def api(self, url, params=None):
        params = self._prepare_params(params)

        json_encoded_params = json.dumps(params)
        private_key = self._private_key
        signature = self._make_signature(private_key, json_encoded_params, private_key)

        request_url = urljoin(self._host, url)
        request_data = {'data': json_encoded_params, 'signature': signature}
        response = requests.post(request_url, data=request_data, verify=False)
        return json.loads(response.content)

    def cnb_form(self, params):
        params = self._prepare_params(params)

        # валідація
        if not params.get('amount') or not params.get('description'):
            raise ParamValidationError('Missing required parameters.')

        # Обовʼязкові поля
        params.update({
            'language': params.get('language', 'uk'),
            'currency': 'UAH' if params.get('currency') == 'RUR' else params.get('currency', 'UAH'),
            'sandbox': 1 if params.get('sandbox') else 0
        })

        data = self.data_to_sign(params)  # вже повертає str
        signature = self._make_signature(self._private_key, data, self._private_key)

        inputs = [
            self.INPUT_TEMPLATE.format(name='data', value=data),
            self.INPUT_TEMPLATE.format(name='signature', value=signature)
        ]
        return self.FORM_TEMPLATE.format(
            action=urljoin(self._host, '3/checkout/'),
            language=params['language'],
            param_inputs='\n\t'.join(inputs)
        )

    def cnb_signature(self, params):
        params = self._prepare_params(params)

        data_to_sign = self.data_to_sign(params)
        return self._make_signature(self._private_key, data_to_sign, self._private_key)

    def cnb_data(self, params):
        params = self._prepare_params(params)
        return self.data_to_sign(params)

    def str_to_sign(self, str):
        return base64.b64encode(hashlib.sha1(str).digest())

    def data_to_sign(self, params):
        return base64.b64encode(json.dumps(params).encode('utf-8')).decode('utf-8')

    def decode_data_from_str(self, data):
        """Decoding data that were encoded by base64.b64encode(str)

        Note:
            Often case of using is decoding data from LiqPay Callback.
            Dict contains all information about payment.
            More info about callback params see in documentation
            https://www.liqpay.ua/documentation/api/callback.

        Args:
            data: json string with api params and encoded by base64.b64encode(str).

        Returns:
            Dict

        Example:
            liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
            data = request.POST.get('data')
            response = liqpay.decode_data_from_str(data)
            print(response)
            {'commission_credit': 0.0, 'order_id': 'order_id_1', 'liqpay_order_id': 'T8SRXWM71509085055293216', ...}

        """
        return json.loads(base64.b64decode(data).decode('utf-8'))
