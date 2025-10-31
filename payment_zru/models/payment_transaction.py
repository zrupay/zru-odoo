from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ZRUPaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    zru_id = fields.Char(string='Transaction ID in ZRU')
    zru_sale_id = fields.Char(string='Sale ID in ZRU')

    def _get_specific_rendering_values(self, values):
        res = super()._get_specific_rendering_values(values)
        if self.provider_code != 'zru':
            return res

        self.ensure_one()

        zru_values = dict(values)
        name_splitted = self.partner_name.split(' ', 1)
        first_name = name_splitted[0]
        if len(name_splitted) > 1:
            last_name = name_splitted[1]
        else:
            last_name = ' '
        zru_values.update(
            {
                'currency': self.currency_id.name,
                'lang': 'au',
                'first_name': first_name,
                'last_name': last_name,
                'address': self.partner_address,
                'address2': self.partner_address,
                'zip_code': self.partner_zip,
                'city': self.partner_city,
                'country': self.partner_country_id and self.partner_country_id.code or "",
                'phone': self.partner_phone,
                'email': self.partner_email,
                'base_url': self.get_base_url(),
            }
        )
        self._update_data_with_products_vat_shipping(zru_values)

        body = self.provider_id.build_transaction_body(zru_values)
        zru = self.provider_id.get_zru()

        transaction = zru.Transaction(body)
        transaction.save()
        values['zru_pay_url'] = transaction.pay_url
        return values

    @api.model
    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ 
        Override of payment to find the transaction based on ZRU data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'zru':
            return tx

        order_id = notification_data.get('order_id')
        if not order_id:
            error_msg = _("ZRU: received data with missing reference (%s)") % (
                order_id
            )
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        txs = self.search([("reference", "=", order_id)])
        if not txs or len(txs) > 1:
            error_msg = "ZRU: received data for reference %s" % (order_id)
            if not txs:
                error_msg += "; no order found"
            else:
                error_msg += "; multiple order found"
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    def _process_notification_data(self, data):
        """
        Override of payment to process the transaction based on ZRU data.

        Note: self.ensure_one()

        :param dict data: The feedback data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        super()._process_notification_data(data)
        if self.provider_code != 'zru':
            return

        zru = self.provider_id.get_zru()
        notification_data = zru.NotificationData(data)

        if self.state == 'done':
            return True
        
        if notification_data.fail:
            error_message = notification_data.fail
            _logger.info(error_message)
            self.write({'state_message': error_message})
            self._set_error('ZRU: ' + _(error_message))
            return True
        
        self.write({
            'provider_reference': notification_data.id,
            'zru_id': notification_data.id,
            'zru_sale_id': notification_data.sale_id,
        })
        
        if notification_data.is_status_done:
            self._set_done()
            return True
        elif notification_data.is_status_pending:
            self._set_pending()
            return True
        elif notification_data.is_status_cancelled or notification_data.is_status_expired:
            self._set_canceled()
            return True

        self._set_error('ZRU: ' + notification_data.status)
        return True
    
    def _update_data_with_products_vat_shipping(self, data):
        """ 
        This method update the products, vat and shipping to send to ZRU API
        """
        if not len(self.sale_order_ids):
            data['products'] = [{
                'amount': 1,
                'product': {
                    'name': 'Order %s' % data['reference'],
                    'price': float('%.2f' % self.amount),
                }
            }]
            return
        order = self.sale_order_ids[0]
        products = []
        shipping_name = ''
        shipping_value = float(0)
        tax_name = _('Taxes')
        tax_value = float(0)
        for line in order.order_line.filtered(lambda l: not l.display_type):  # ignore notes and section lines
            if line.price_tax:
                tax_value += float('%.2f' % line.price_tax)

            if 'is_delivery' in line._fields and line.is_delivery:
                if line.price_total:
                    shipping_name = line.name[:100]
                    shipping_value += float('%.2f' % line.price_total - line.price_tax)
                continue

            product = {
                'amount': int(line.product_uom_qty),
                'product': {
                    'product_id': line.product_id.id,
                    'name': line.name[:100],
                    'price': float('%.2f' % (line.price_total - line.price_tax)),
                }
            }
            products.append(product)

        data['shipping_name'] = shipping_name
        data['shipping_value'] = float('%.2f' % shipping_value)
        data['tax_name'] = tax_name
        data['tax_value'] = float('%.2f' % tax_value)
        data['products'] = products
