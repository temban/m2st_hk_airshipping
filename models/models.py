# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions
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
    ], string='Status', default='pending')
    disable = fields.Boolean(string='Travel disable', compute='_compute_disable', store=True, default=False, readonly=False)
    negotiation = fields.Boolean(string='Travel negotiation', default=False)
    departure_town = fields.Char(string='Departure town', required=True)
    arrival_town = fields.Char(string='Arrival town', required=True)
    departure_date = fields.Date(string='Departure date', required=True)
    arrival_date = fields.Date(string='Arrival date', required=True)
    kilo_qty = fields.Integer(string='kilo qty', required=True)
    price_per_kilo = fields.Float(string='Price per kilo', required=True)
    type_of_luggage_accepted = fields.Text(string='Type of luggage accepted')
    files_uploaded_id = fields.One2many('m2st_hk_airshipping.airshipping_file_upload', 'travel_id')


class TravelBooking(models.Model):
    _name = 'm2st_hk_airshipping.travel_booking'
    _description = 'Booking of travels'

    sender_id = fields.Many2one('res.partner')
    travel_id = fields.Many2one('m2st_hk_airshipping.airshipping', required=True)
    receiver_partner_id = fields.Many2one('res.partner', string='Receiver')
    receiver_name = fields.Char(string='Receiver Name')
    receiver_email = fields.Char(string='Receiver Email')
    receiver_phone = fields.Char(string='Receiver Phone')
    receiver_address = fields.Text(string='Receiver Address')
    type_of_luggage = fields.Text(string='Type of luggage you want to send', required=True)
    luggage_image = fields.Binary(string='Luggage images')
    kilo_booked = fields.Integer(string='kilo qty', required=True)
    kilo_booked_price = fields.Float(string='Price of reserved kilos', required=True, default=100.0)
    disable = fields.Boolean(string='Disable Booking', default=False)
    confirm = fields.Boolean(string='Booking confirm status', default=False)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted')
    ], string='Status', default='pending')

    @api.onchange('receiver_partner_id')
    def _onchange_receiver_partner_id(self):
        if self.receiver_partner_id:
            self.receiver_name = self.receiver_partner_id.name
            self.receiver_email = self.receiver_partner_id.email
            self.receiver_phone = self.receiver_partner_id.phone or ''
            self.receiver_address = self.receiver_partner_id.street or ''

    @api.onchange('receiver_name', 'receiver_email', 'receiver_phone', 'receiver_address')
    def _onchange_receiver_info(self):
        if self.receiver_partner_id:
            self.receiver_partner_id = False

    @api.constrains('receiver_partner_id', 'receiver_name', 'receiver_email', 'receiver_phone', 'receiver_address')
    def _check_receiver_info(self):
        for booking in self:
            if not booking.receiver_partner_id and not (
                    booking.receiver_name and booking.receiver_email and booking.receiver_phone):
                raise exceptions.ValidationError("Receiver information is incomplete.")


class ResUsers(models.Model):
    _inherit = 'res.partner'

    airshipping_ids = fields.One2many('m2st_hk_airshipping.airshipping', 'user_partner_id')
    booking_ids = fields.One2many('m2st_hk_airshipping.travel_booking', 'sender_id')
    # image_1920 = fields.Binary(string='Image', attachment=True)
