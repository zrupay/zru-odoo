# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import werkzeug


class ZRUController(http.Controller):
    @http.route(
        ['/payment/zru/notification'],
        type='json',
        auth='public',
        csrf=False,
        methods=['POST'],
    )
    def notification_payment(self, **post):
        notification_data = http.request.get_json_data()
        if notification_data:
            request.env['payment.transaction'].sudo()._handle_notification_data('zru', notification_data)
        return 'OK'
    
    @http.route(
        ['/payment/zru/return'],
        type='http',
        auth='public',
        csrf=False,
        methods=['GET'],
    )
    def return_payment(self, **post):
        return werkzeug.utils.redirect('/payment/status')
