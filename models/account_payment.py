# coding: utf-8

import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


try:
    import conekta
except ImportError as err:
    print 'No se pudo installar el modulo, favor de instalar api de conekta ver README'
    _logger.debug(err)

CONEKTA_API_VERSION = "0.3.0"

# test

#
#CONEKTA_PUBLIC_KEY = "key_KgVK7FVH5xRfWyaH"
#CONEKTA_KEY="key_PqC9ZJasDD2YXzxo"
#
#conekta.api_key = CONEKTA_KEY
#conekta.api_version = CONEKTA_API_VERSION

class AccountPaymentConekta(models.Model):

    _inherit = 'account.payment'

    acquirer = fields.Many2one(comodel_name='payment.acquirer', string='Aquirer')
    # cards_test_49 = fields.Selection(selection='_get_credit_cards2')
    cards_test_50 = fields.Many2one(comodel_name='conekta.credit.card', domain= lambda self:self._get_domain(),string="Conekta Credit Card")
    hide = fields.Boolean(compute='_hide_cards')

    def _set_conketa_key(self):
        print 'seting up conekta key;;', self.acquirer
        enviroment = self.acquirer.environment
        print 'enviroment',enviroment
        if enviroment == 'prod':
             CONEKTA_KEY = self.acquirer.conekta_secret_key
             CONEKTA_PUBLIC_KEY = self.acquirer.conekta_publishable_key
        else:
             CONEKTA_KEY = self.acquirer.conekta_secret_key_test
             CONEKTA_PUBLIC_KEY = self.acquirer.conekta_publishable_key_test

        print 'CONEKTA_KEY',CONEKTA_KEY
        conekta.api_key = CONEKTA_KEY
        conekta.api_version = CONEKTA_API_VERSION
        
        return True

    @api.multi
    @api.onchange('partner_id')
    def _get_domain(self):
        res = {}
        # print '-----------------------aqui ----------------\n', self.partner_id.id
        res['domain'] = {'cards_test_50':[("partner_id", "=", self.partner_id.id)]}
        # print 'Doooooooooooooooooooooooooooooomain',res
        return res

    @api.depends('acquirer')
    def _hide_cards(self):
        if self.acquirer.name == 'Conekta':
            self.hide = True


    def action_validate_invoice_payment(self):
        if self.acquirer.name == 'Conekta':
            values = super(AccountPaymentConekta, self).action_validate_invoice_payment()
            print '\n \n \n si pucha esta madre jajajajaj\n \n \n'
            res = self.conekta_payment_validate()
        else:
           res = super(AccountPaymentConekta, self).action_validate_invoice_payment()

        return res

    @api.multi
    def conekta_payment_validate(self):
        card_token = self.cards_test_50.conekta_card_id
        amount = self.amount
        currency = self.currency_id.name
        partner_id = self.partner_id.id
        invoice = self.invoice_ids.number

        description="Linkaform Factura %s"%invoice

        conekta_object = {
                "currency":currency,
                "amount":amount,
                "description":description,
                "reference_id": invoice,
                "card":card_token,
                "pay_method": {'object': 'card_payment'}
        }

        # print 'payload :[{}]'.format(self.request.payload)
  #       print 'Charge Obj = %s'%(charge_obj)
  #       charge = 'Cobro conekta'
  #       res = {}
  #       e = False
        self._set_conketa_key()
        print 'conetkta', conekta
        print 'conekta api', dir(conekta)
        print 'elllllllllllllllllll eobjeto \n', conekta_object
        print '\n \n '

        try:
          charge  = conekta.Charge.create(conekta_object)
        except conekta.ConektaError as e:
            print 'excepte  = %s'%(e)
            print 'excepte  = %s'%(e.message)
            print 'excepte  = %s'%(e.error_json['message_to_purchaser'])
        if e:
            print e.error_json['message_to_purchaser']
            print 'NOT Charge'
        else:
            print 'udapte status', charge.status
