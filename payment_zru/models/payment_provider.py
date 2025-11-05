from odoo import models, fields, api
from odoo.exceptions import UserError
from zru import ZRUClient


class ZRUPaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[("zru", "ZRU")], ondelete={"zru": "set default"}
    )
    zru_public_key = fields.Char('ZRU public key', size=32)
    zru_secret_key = fields.Char('ZRU secret key', size=32)

    @api.onchange('zru_public_key')
    def _onchange_zru_public_key(self):
        if self.zru_public_key and len(self.zru_public_key) != 32:
            raise UserError('A public key must be 32 characters long')

    @api.onchange('zru_secret_key')
    def _onchange_zru_secret_key(self):
        if self.zru_secret_key and len(self.zru_secret_key) != 32:
            raise UserError('A secret key must be 32 characters long')

    def build_transaction_body(self, data):
        body = {
            'order_id': data['reference'],
            'currency': data['currency'],
            'return_url': data['base_url'] + '/payment/zru/return',
            'cancel_url': data['base_url'] + '/payment/zru/return',
            'notify_url': data['base_url'] + '/payment/zru/notification',
            'language': data['lang'] or 'au',
            'products': data['products'],
            'extra': {
                'email': data['email'],
                'phone_number': data['phone'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'billing_street_name': data['address'],
                'billing_postal_code': data['zip_code'],
                'billing_city': data['city'],
                'billing_country': data['country'],
                'zru_lib': {
                    'name': 'odoo-17',
                    'version': '1.3'
                },
            },
        }
        if data.get('shipping_name', None):
            body['shipping_name'] = data['shipping_name']
            body['shipping_value'] = data['shipping_value']
        if data.get('tax_name', None):
            body['tax_name'] = data['tax_name']
            body['tax_value'] = data['tax_value']
        return body

    def get_zru(self):
        zru = ZRUClient(self.zru_public_key, self.zru_secret_key)
        return zru
