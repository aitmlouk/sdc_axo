from odoo import models, fields, api,_
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.addons import decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
    
class ResCompany(models.Model):
    _inherit = 'res.company' 
    
    rc = fields.Char(string='N°RC')
    itp = fields.Char(string='Patente')
    ifs = fields.Char(string='Identifiant Fiscal')
    cnss = fields.Char(string='CNSS')
    ice = fields.Char(string='I.C.E')
    company_type_id = fields.Many2one('res.company.type',string='Type de société')
    capital = fields.Float(string='Capital')
    tele = fields.Char(string='Télécopie')
    date = fields.Date(string='Date inscription')
 

class ResCompanyType(models.Model):
    _name = 'res.company.type' 
    
    name = fields.Char(string='Nom')
    code = fields.Char(string='Code')
    
class Partner(models.Model):
    _inherit = 'res.partner' 
    
    rc = fields.Char(string='Registre du commerce')
    patente = fields.Char(string='Patente')
    ifs = fields.Char(string='Identifiant Fiscal')
    cnss = fields.Char(string='C.N.S.S.')
    ice = fields.Char(string='I.C.E')
    activite_id = fields.Many2one('partner.activity',string='Activités')
    supplier_account = fields.Char(string='Ancien compte fournisseur')

class PartnerActivity(models.Model):
    _name = 'partner.activity' 
    
    name = fields.Char(string='Nom')
    code = fields.Char(string='Code')
            
class ProductTemplate(models.Model):
    _inherit = 'product.template' 

    @api.onchange('largeur','hauteur')
    def _compute_area(self):
        if self.largeur and self.hauteur:
            self.area = self.largeur * self.hauteur or False
                
    internal_category_id = fields.Many2one('product.internal',string='Catégorie Emplac.')
    display_type_id = fields.Many2one('product.display',string='Type d\'affichage') 
    adress = fields.Char(string='Adresse') 
    city_id = fields.Many2one('res.city',string='Ville') 
    largeur = fields.Float(string='Largeur') 
    hauteur = fields.Float(string='Hauteur')
    area = fields.Float(string='Surface')  
    time = fields.Float(string='Temps de pose')
    visibility = fields.Char(string='Visibilité')
    proximity = fields.Char(string='Proximité')


class ProductInternal(models.Model):
    _name = 'product.internal' 
    
    name = fields.Char(string='Nom')
    code = fields.Char(string='Code')
    
class ProductDisplay(models.Model):
    _name = 'product.display' 
    
    name = fields.Char(string='Nom')
    code = fields.Char(string='Code')

class ResCity(models.Model):
    _name = 'res.city' 
    
    name = fields.Char(string='Nom')
    code = fields.Char(string='Code')

class SaleOrder(models.Model):
    _inherit = 'sale.order' 

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        if self.refrence_id =='print':
            for line in self.order_line:
                    print('reimpression----------------------')
                    price = line.price_unit
                    product_uom_qty =line.area * (1+(line.comm_agence/100))
                    taxes = line.tax_id.compute_all(price, line.order_id.currency_id, product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
                    line.update({
                        'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                        'price_total': taxes['total_included'],
                        'price_subtotal': taxes['total_excluded'],
                    })
        else:
            for line in self.order_line:     
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    product_uom_qty =(1+(line.comm_agence/100))
                    taxes = line.tax_id.compute_all(price, line.order_id.currency_id, product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
                    line.update({
                        'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                        'price_total': taxes['total_included'],
                        'price_subtotal': taxes['total_excluded'],
                    })
                      
    @api.depends('order_line')
    def _compute_display(self):
            display = []
            if self.order_line:
                for l in self.order_line: 
                    if l.product_id.display_type_id.name not in display:           
                        display.append(l.product_id.display_type_id.name) 
                display_name = ', '.join(str(v) for v in display)
                self.display = display_name or ''
            return True
                
                    
    compagne = fields.Char(string='Campagne')
    periode = fields.Char(string='Période demandée')
    annance = fields.Char(string='Annonceur')
    display = fields.Char(compute='_compute_display',string='Choix d\'affichage')
    refrence_id = fields.Selection([('contract', 'Contrat de prestation'), ('print', 'Réimpression')], string= 'Référence')
  
    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sales journal for this company.'))
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'compagne':self.compagne,
            'num_offer':self.name,
            'annance':self.annance,
            'refrence_id':self.refrence_id,
            'periode':self.periode,
            'type': 'out_invoice',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id
        }
        return invoice_vals


    @api.multi
    def _action_confirm(self):
        super(SaleOrder, self)._action_confirm()

        for fr in self.order_line:
            sup = fr.product_id.seller_ids
            if not sup:
                raise UserError(_('Veuillez choidir un fournisseur pour l\article > anglet achat!'))
            va = {
                'partner_id':sup.name.id,
                'date_order':self.date_order,
                'origin':self.name
                
                }
        ord = self.env['purchase.order'].create(va)
        for order in self.order_line:
            seller = order.product_id._select_seller(
            partner_id=sup.name,
            quantity=False,
            date=order.order_id.date_order and order.order_id.date_order[:10],
            uom_id=order.product_uom)      
            vals = {
                'product_id':order.product_id.id,
                'product_qty':order.area,
                'product_uom':order.product_uom.id,
                'name':order.product_id.name,
                'date_planned':self.date_order,
                'price_unit':seller.price,
                'largeur':order.largeur,
                'hauteur':order.hauteur,
                'adresse':order.adresse,
                'order_id':ord.id,
                'taxes_id':[(6, 0, order.tax_id.ids)]
                }
            self.env['purchase.order.line'].create(vals)

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"   
    plage_h = fields.Char(string='Plage horaire')
    user_id = fields.Many2one('res.users',string='Emetteur',default=lambda self: self._uid)
    
class Purshase(models.Model):
    _inherit = 'purchase.order.line'   
    
    largeur = fields.Float(string='Largeur')
    hauteur = fields.Float(string='Hauteur')
    adresse = fields.Char(string='Adresse')   
       
                  
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'   
            
    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.adresse = self.product_id.adress or False
            self.largeur = self.product_id.largeur or False
            self.hauteur = self.product_id.hauteur or False
            self.area = self.product_id.area or False

    @api.onchange('largeur','hauteur')
    def _compute_area(self):
        if self.largeur and self.hauteur:
            self.area = self.largeur * self.hauteur or False

                   
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            if line.order_id.refrence_id =='print':
                print('reimpression----------------------')
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                product_uom_qty =line.area * (1+(line.comm_agence/100))
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })
            else:
                
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                product_uom_qty =(1+(line.comm_agence/100))
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })
                                                                   
    adresse = fields.Char(string='Adresse')
    du = fields.Date(string='Du')
    au = fields.Date(string='Au')
    month_nbr = fields.Integer(string='Nbr mois') 
    largeur = fields.Float(string='Largeur') 
    hauteur = fields.Float(string='Hauteur')
    area = fields.Float(string='Surface')  
    dimension = fields.Char(string='Dimension')
    vailable = fields.Date(string='Disponibilité')
    comm_agence = fields.Integer(string='Comm.Agence')
    #product_uom_qty = fields.Integer(string='Comm. Agence %', digits=dp.get_precision('Product Unit of Measure'), required=True, default=0)
    price_unit_axo = fields.Monetary(string='PU HT',
        store=True, readonly=True, compute='_compute_punit_axo', help="Price unit")                

    @api.one
    @api.depends('comm_agence','price_unit')
    def _compute_punit_axo(self):
        if self.order_id.refrence_id=='print':  
            product_uom_qty =(1+(self.comm_agence/100))
            self.price_unit_axo = product_uom_qty * self.price_unit or False
            
            
    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id
        if not account:
            raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
        if fpos:
            account = fpos.map_account(account)

        res = {
            'name': self.name,
            'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': account.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'largeur':self.largeur,
            'hauteur':self.hauteur,
            'area':self.area,
            'adresse':self.adresse,
            'du':self.du,
            'au':self.au,
            'comm_agence':self.comm_agence,
            'discount': self.discount,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'layout_category_id': self.layout_category_id and self.layout_category_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
            'account_analytic_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
        }
        return res 
            
                    
class AccountInvoice(models.Model):
    _inherit = 'account.invoice' 
                             
    modalites = fields.One2many('modalite.line','invoice_id',string='Campagne')
    modalite_id = fields.Many2one('modalite.modalite',string='Modalité de paiement')
    compagne = fields.Char(string='Campagne')
    periode = fields.Char(string='Période demandée')
    annance = fields.Char(string='Annonceur')
    num_offer = fields.Char(string='Offre N°')
    refrence_id = fields.Selection([('contract', 'Contrat de prestation'), ('print', 'Réimpression')], string= 'Référence')
    amount_untaxed = fields.Monetary(string='Untaxed Amount',
        store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    
    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        for line in self.invoice_line_ids:
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            product_uom_qty =(1+(line.comm_agence/100))
            product_uom_qty1 =line.area * (1+(line.comm_agence/100))
            if self.refrence_id=='print':
                taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, product_uom_qty1, line.product_id, self.partner_id)['taxes']
                for tax in taxes:
                    val = self._prepare_tax_line_vals(line, tax)
                    key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)
    
                    if key not in tax_grouped:
                        tax_grouped[key] = val
                    else:
                        tax_grouped[key]['amount'] += val['amount']
                        tax_grouped[key]['base'] += val['base']
            else:
                
                taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, product_uom_qty, line.product_id, self.partner_id)['taxes']
                for tax in taxes:
                    val = self._prepare_tax_line_vals(line, tax)
                    key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)
    
                    if key not in tax_grouped:
                        tax_grouped[key] = val
                    else:
                        tax_grouped[key]['amount'] += val['amount']
                        tax_grouped[key]['base'] += val['base']
        return tax_grouped

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign
            
class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'   
                                                                   
    adresse = fields.Char(string='Adresse')
    du = fields.Date(string='Du')
    au = fields.Date(string='Au')
    largeur = fields.Float(string='Largeur') 
    hauteur = fields.Float(string='Hauteur')
    area = fields.Float(string='Surface')
    comm_agence = fields.Integer(string='Comm.Agence')
    #price_subtotal = fields.Monetary(string='Amount',
        #store=True, readonly=True, compute='_compute_subt', help="Total amount without taxes")
    
    price_unit_axo = fields.Monetary(string='PU HT',
        store=True, readonly=True, compute='_compute_punit_axo', help="Price unit")                

    @api.one
    @api.depends('comm_agence','price_unit')
    def _compute_punit_axo(self):
        if self.invoice_id.refrence_id=='print':  
            product_uom_qty =(1+(self.comm_agence/100))
            self.price_unit_axo = product_uom_qty * self.price_unit or False
        


    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.adresse = self.product_id.adress or False
            self.largeur = self.product_id.largeur or False
            self.hauteur = self.product_id.hauteur or False
            self.area = self.product_id.area or False

    @api.onchange('largeur','hauteur')
    def _compute_area(self):
        if self.largeur and self.hauteur:
            self.area = self.largeur * self.hauteur or False

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        product_uom_qty =(1+(self.comm_agence/100))
        product_uom_qty1 =self.area * (1+(self.comm_agence/100))
        taxes = False
        if self.invoice_id.refrence_id=='print':  
            if self.invoice_line_tax_ids:
                taxes = self.invoice_line_tax_ids.compute_all(price, currency, product_uom_qty1, product=self.product_id, partner=self.invoice_id.partner_id)
            self.price_subtotal = price_subtotal_signed =  product_uom_qty1 * price
            self.price_total = taxes['total_included'] if taxes else self.price_subtotal
        else:
            if self.invoice_line_tax_ids:
                taxes = self.invoice_line_tax_ids.compute_all(price, currency, product_uom_qty, product=self.product_id, partner=self.invoice_id.partner_id)
            self.price_subtotal = price_subtotal_signed =  product_uom_qty * price
            self.price_total = taxes['total_included'] if taxes else self.price_subtotal
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign

    """@api.one
    @api.depends('price_unit', 'comm_agence')
    def _compute_subt(self):
        if self.invoice_id.refrence_id=='print':  
            product_uom_qty =self.area * (1+(self.comm_agence/100))
            self.price_subtotal = product_uom_qty * self.price_unit or False
        else:
            product_uom_qty =(1+(self.comm_agence/100))
            self.price_subtotal = product_uom_qty * self.price_unit or False"""
                                                                
class ModalitePai(models.Model):
    _name = 'modalite.modalite' 

    name = fields.Char(string='Nom')
    code = fields.Char(string='Code')

class PaymentMode(models.Model):
    _name = 'payment.mode' 

    name = fields.Char(string='Nom')
    code = fields.Char(string='Code')
    
class Modalites(models.Model):
    _name = 'modalite.line' 
                             
    mode_id = fields.Many2one('payment.mode', string= 'Mode de règlement')
    percent = fields.Integer(string='%')
    echeance = fields.Date(string='échéance')
    amount = fields.Float(compute='_compute_amount', string='Montant')
    invoice_id = fields.Many2one('account.invoice',string='échéance')
    
    @api.one
    @api.depends('percent','invoice_id.amount_total')
    def _compute_amount(self):
        if self.percent:
            self.amount = (self.percent/100) * self.invoice_id.amount_total or False
            