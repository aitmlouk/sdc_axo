from odoo import models, fields, api,_
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.addons import decimal_precision as dp

    
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
    
"""class Partner(models.Model):
    _inherit = 'res.partner' 
    
    rc = fields.Char(string='N°RC')
    patente = fields.Char(string='Patente')
    ifs = fields.Char(string='Identifiant Fiscal')
    cnss = fields.Char(string='CNSS')
    ice = fields.Char(string='I.C.E')"""
        
class ProductTemplate(models.Model):
    _inherit = 'product.template' 

    @api.onchange('width','height')
    def _compute_area(self):
        if self.width and self.height:
            self.area = self.width * self.height or False
                
    internal_category_id = fields.Many2one('product.internal',string='Catégorie Emplac.')
    display_type_id = fields.Many2one('product.display',string='Type d\'affichage') 
    adress = fields.Char(string='Adresse') 
    city_id = fields.Many2one('res.city',string='Ville') 
    width = fields.Float(string='Largeur') 
    height = fields.Float(string='Hauteur')
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
       
    @api.depends('order_line')
    def _compute_display(self):
            display = []
            if self.order_line:
                for l in self.order_line: 
                    if l.product_id.display_type_id.name not in display:           
                        display.append(l.product_id.display_type_id.name) 
                display_name = ', '.join(str(v) for v in display)
                self.display = display_name or False
            return True
                
                
    compagne = fields.Char(string='Campagne')
    periode = fields.Char(string='Période demandée')
    annance = fields.Char(string='Annonceur')
    display = fields.Char(compute='_compute_display',string='Choix d\'affichage')
    refrence_id = fields.Selection([('contract', 'Contrat de prestation'), ('print', 'Réimpression')], string= 'Référence')
   
 
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'   


    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': line.price_unit*(1+(line.product_uom_qty/100)),
            })
            
    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.adresse = self.product_id.adress or False
            self.width = self.product_id.width or False
            self.height = self.product_id.height or False
            self.area = self.product_id.area or False

    @api.onchange('width','height')
    def _compute_area(self):
        if self.width and self.height:
            self.area = self.width * self.height or False
                                                    
    adresse = fields.Char(string='Adresse')
    du = fields.Date(string='Du')
    au = fields.Date(string='Au')
    month_nbr = fields.Integer(string='Nbr mois') 
    width = fields.Float(string='Largeur') 
    height = fields.Float(string='Hauteur')
    area = fields.Float(string='Surface')  
    dimension = fields.Char(string='Dimension')
    vailable = fields.Date(string='Disponibilité')
    product_uom_qty = fields.Float(string='Comm. Agence', digits=dp.get_precision('Product Unit of Measure'), required=True, default=0.0)

    
    
    
    