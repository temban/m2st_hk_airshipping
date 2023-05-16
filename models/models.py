# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import datetime, date


class Publicity(models.Model):
    _name = 'm2st_hk_airshipping.publicity'
    _description = 'Publicity showcase'

    image = fields.Binary(string='image')
    text = fields.Text(string='text')


class FileUpload(models.Model):
    _name = 'm2st_hk_airshipping.airshipping_file_upload'
    _description = 'File Upload'

    cni_doc = fields.Binary(string='cni doc')
    cni_name = fields.Char(string='cni name')
    ticket_doc = fields.Binary(string='ticket doc')
    ticket_name = fields.Char(string='ticket name')
    travel_id = fields.Many2one('m2st_hk_airshipping.airshipping')


class AirShipping(models.Model):
    _name = 'm2st_hk_airshipping.airshipping'
    _description = 'Management of air shipments'

    user_partner_id = fields.Many2one('res.partner')
    travel_type = fields.Char(string='Travel type', default='Air')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted')
    ], string='status', default='pending')
    disable = fields.Boolean(string='Travel disable', compute='_compute_disable', store=True, default=False)
    departure_town = fields.Char(string='Departure town', required=True)
    arrival_town = fields.Char(string='Arrival town', required=True)
    departure_date = fields.Date(string='Departure date', required=True)
    arrival_date = fields.Date(string='Arrival date', required=True)
    kilo_qty = fields.Integer(string='kilo', required=True)
    price_per_kilo = fields.Integer(string='Prix par kilo', required=True)
    type_of_luggage_accepted = fields.Char(string='Type of luggage accepted', required=True)
    files_uploaded_id = fields.One2many('m2st_hk_airshipping.airshipping_file_upload', 'travel_id')


class ResUsers(models.Model):
    _inherit = 'res.partner'

    airshipping_ids = fields.One2many('m2st_hk_airshipping.airshipping', 'user_partner_id')
    # image_1920 = fields.Binary(string='Image', attachment=True)
