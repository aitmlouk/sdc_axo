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
    
    
class ProductTemplate(models.Model):
    _inherit = 'product.template' 
    
    internal_category_id = fields.Many2one('product.internal',string='Catégorie interne')
    display_type_id = fields.Many2one('product.display',string='Type d\'affichage') 
    adress = fields.Char(string='Adresse') 
    city_id = fields.Many2one('res.city',string='Ville') 
    width = fields.Float(string='Largeur') 
    height = fields.Integer(string='Hauteur')
    area = fields.Integer(string='Surface')  
    time = fields.Integer(string='Temps de pose')


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
    
    compagne = fields.Char(string='Compagne')
    periode = fields.Char(string='Période demandée')
    annance = fields.Char(string='Annanceur')
    refrence_id = fields.Selection([('contract', 'Contrat de prestation'), ('print', 'Réimpression')], string= 'Référence')
    display_id = fields.Many2one('product.display',string='Choix d\'affichage')
   
 
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'   

    @api.one
    @api.depends('product_uom_qty','price_unit')
    def _total_compute(self):
        if self.product_uom_qty:
            self.price_subtotal = 1+(self.product_uom_qty/100)*self.price_unit,
                            
    adresse = fields.Char(string='Adresse')
    du = fields.Date(string='Du')
    au = fields.Date(string='Au')
    month_nbr = fields.Integer(string='Nbr mois') 
    dimension = fields.Char(string='Dimension')
    vailable = fields.Date(string='Disponibilité')
    product_uom_qty = fields.Float(string='Comm. Agence', digits=dp.get_precision('Product Unit of Measure'), required=True, default=0.0)

    
    
    
    