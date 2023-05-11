from odoo import fields, models, api


class m0st_hk_base(models.Model):
    _inherit = "res.partner"
    _description = 'Management of the basic entities of HUB KILO'
    birthday = fields.Date(string='born on', required=True)
    birthplace = fields.Char(string="born at", required=True)
    sex = fields.Char(string="Sex", required=True)
    is_traveler = fields.Boolean(default=False)
    type_of_piece = fields.Char(string="Type of piece", required=True)


class FileUpload(models.Model):
    _name = 'm2st_hk_airshipping.airshipping_file_upload'
    _description = 'File Upload'

    partner_id = fields.Many2one('res.partner')
    cni_doc = fields.Binary(string='cni doc')
    cni_name = fields.Char(string='cni name')
    ticket_doc = fields.Binary(string='ticket doc')
    ticket_name = fields.Char(string='ticket name')


class Airshipping(models.Model):
    _name = 'm2st_hk_airshipping.airshipping'
    _description = 'Management of air shipments'

    user_partner_id = fields.Many2one('res.partner')
    travel_type = fields.Selection([
        ('by_road', 'By_Land'),
        ('by_air', 'By_Air'),
        ('by_sea', 'By_Sea')
    ], string='Type voyage', default='by_air', required=True)
    Validation = fields.Boolean(string='Travel Validation', default=False)
    departure_town = fields.Char(string='Ville depart', required=True)
    arrival_town = fields.Char(string='Ville arrivé', required=True)
    departure_date = fields.Date(string='Heure depart', required=True)
    arrival_date = fields.Date(string='Heure arrivé', required=True)
    kilo_qty = fields.Integer(string='Nombre kilo', required=True)
    price_per_kilo = fields.Integer(string='Prix par kilo', required=True)
    type_of_luggage_accepted = fields.Char(string='Type de paquet accepté', required=True)

class ResUsers(models.Model):
    _inherit = 'res.partner'

    airshipping_ids = fields.One2many('m2st_hk_airshipping.airshipping', 'user_partner_id')
    fileUpload_ids = fields.One2many('m2st_hk_airshipping.airshipping_file_upload', 'partner_id')


    # def _compute_total_price(self):
    #     for booking in self:
    #         # your price calculation logic here
    #         booking.total_price = 100.0