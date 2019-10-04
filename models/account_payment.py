# coding: utf-8
import requests, simplejson, json
import logging, datetime

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


try:
    import conekta
except ImportError as err:
    _logger.debug(err)

CONEKTA_API_VERSION = "2.4.0"

ambiente = 'conekta'

class AccountPaymentConekta(models.Model):

    _inherit = 'account.payment'

    acquirer = fields.Many2one(comodel_name='payment.acquirer', string='Aquirer')
    cards_conekta = fields.Many2one(comodel_name='conekta.credit.card', domain= lambda self:self._get_domain(),string="Conekta Credit Card")
    hide = fields.Boolean(compute='_hide_cards')
    error = fields.Text(store = False )


    def _set_conketa_key(self):
        enviroment = self.acquirer.environment
        if enviroment == 'prod':
             CONEKTA_KEY = self.acquirer.conekta_secret_key
             CONEKTA_PUBLIC_KEY = self.acquirer.conekta_publishable_key
        else:
             CONEKTA_KEY = self.acquirer.conekta_secret_key_test
             CONEKTA_PUBLIC_KEY = self.acquirer.conekta_publishable_key_test

        conekta.api_key = CONEKTA_KEY
        # conekta.api_version = CONEKTA_API_VERSION

        return CONEKTA_KEY

    @api.multi
    @api.onchange('partner_id')
    def _get_domain(self):
        res = {}
        res['domain'] = {'cards_conekta':[("partner_id", "=", self.partner_id.id)]}
        return res

    @api.depends('acquirer')
    def _hide_cards(self):
        if self.acquirer.name == 'Conekta':
            self.hide = True

    def _create_payment_transaction(self):
        self.payment_model = self.env['payment.transaction']
        transaction_model = {
                'reference': self.invoice_ids.number,
                'invoice_id': self.invoice_ids.id,
                'amount': self.amount,
                'currency_id': self.currency_id.id,
                'partner_id': self.partner_id.id,
                'acquirer_id': self.acquirer.id,
                'fees': (self.amount * 2.9)/100
            }
        transaction = self.payment_model.create(transaction_model)
        return transaction


    def action_validate_invoice_payment(self):
        if self.acquirer.name == 'Conekta':
            res = self.conekta_payment_validate()
            if res == True:
                trans = self._create_payment_transaction()
                self.payment_transaction_id = trans.id
                trans.state = 'done'
                values = super(AccountPaymentConekta, self).action_validate_invoice_payment()
            else:
                trans = self._create_payment_transaction()
                message = 'Message form your friends at Contekta \n' + str(self.error)
                raise ValidationError(message)
        else:
           res = super(AccountPaymentConekta, self).action_validate_invoice_payment()

        return False

    @api.multi
    def conekta_payment_validate(self):
        amount = int(self.amount)
        currency = self.currency_id.name
        invoice = self.invoice_ids.number
        line_items = []
        email = ""
        if self.partner_id.email:
            email = self.partner_id.email
        else:
            email = self.env['res.partner'].search([('parent_id','=', self.partner_id.id)])[0].email

        lines =  self.env['account.invoice.line'].search([('invoice_id', '=' , self.invoice_ids.id)])
        for item in lines:
            objeto = {
              "name": item.name ,
              "unit_price": int(item.price_unit) ,
              "quantity": int(item.quantity) ,
            }
            line_items.append(objeto)

        description="Linkaform Factura %s"%invoice

        conekta_object = {
                "line_items":line_items,
                "customer_info":{
                    "name": self.partner_id.name,
                    "phone": self.partner_id.phone,
                    "email": email
                },
                "charges": [{

                    "payment_method":{
                        "object": 'card_payment',
                        "type": 'card',
                        "name": self.cards_conekta.name,
                        "last4": self.cards_conekta.last_four_digits,
                        "brand": self.cards_conekta.type,
                        "token_id": self.cards_conekta.conekta_card_id
                  },
                "currency" : currency
                }],
                "currency" : currency,
                "amount": amount,
                "metadata" : {"description" : description}
              }
        self._set_conketa_key()
        try:
            charge  = conekta.Order.create(conekta_object)
        except conekta.ConektaError as e:
            self.error = e.error_json['details'][0]['message']
            self.communication ='Not Charge'
        else:
            return 'No se puede pagar'