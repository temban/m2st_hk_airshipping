# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions
import random
import string
from datetime import datetime, date
import random
import string


class Publicity(models.Model):
    _name = 'm2st_hk_airshipping.publicity'
    _description = 'Publicity showcase'

    image = fields.Binary(string='image')
    text = fields.Text(string='text')


class FileUpload(models.Model):
    _name = 'm2st_hk_airshipping.airshipping_file_upload'
    _description = 'File Upload'

    cni_doc = fields.Binary(string='National identity card or Passport')
    cni_name = fields.Char(string='cni name')
    ticket_doc = fields.Binary(string='Flight ticket')
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
    disable = fields.Boolean(string='Travel disable', compute='_compute_disable', store=True, default=False,
                             readonly=False)
    # negotiation = fields.Boolean(string='Travel negotiation', default=False)
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
    message_ids = fields.One2many('m2st_hk_airshipping.message', 'travel_booking_id', string='Messages')
    receiver_partner_id = fields.Many2one('res.partner', string='Receiver')
    receiver_name = fields.Char(string='Receiver Name')
    receiver_email = fields.Char(string='Receiver Email')
    receiver_phone = fields.Char(string='Receiver Phone')
    receiver_address = fields.Text(string='Receiver Address')
    type_of_luggage = fields.Text(string='Type of luggage you want to send', required=True)
    luggage_image = fields.Binary(string='Luggage images')
    kilo_booked = fields.Integer(string='kilo qty', required=True)
    kilo_booked_price = fields.Float(string='Price of reserved kilos')
    disable = fields.Boolean(string='Disable Booking', default=False)
    negotiation = fields.Boolean(string='Travel negotiation', default=False)
    # confirm = fields.Boolean(string='Booking confirm status', default=False)
    # booking_state = fields.Boolean(string='Booking start, if it is completed', default=False)
    code = fields.Char(string='Booking code', readonly=True)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed')
    ], string='Status', default='pending')

    @api.onchange('disable')
    def _onchange_book_disable(self):
        if self.status == 'accepted':
            self.travel_id.kilo_qty += int(self.kilo_booked)

    @api.onchange('kilo_booked')
    def _onchange_kilo_booked_price(self):
        self.kilo_booked_price = self.travel_id.price_per_kilo * self.kilo_booked

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


class Message(models.Model):
    _name = 'm2st_hk_airshipping.message'
    _description = 'Messaging Model'

    travel_booking_id = fields.Many2one('m2st_hk_airshipping.travel_booking', string='Travel Booked')
    sender_id = fields.Many2one('res.partner', string='Sender')
    receiver_id = fields.Many2one('res.partner', string='Receiver')
    message = fields.Float(string='Message(Price)')
    date = fields.Datetime(string='Date')

    # def send_message(self, sender_id, receiver_id, message, travel_booking_id):
    #     # Create a new message record
    #     new_message = self.sudo().create({
    #         'sender_id': sender_id,
    #         'receiver_id': receiver_id,
    #         'message': message,
    #         'travel_booking_id': travel_booking_id,
    #     })
    #     return new_message
    #
    # def get_messages(self, travel_booking_id):
    #     # Retrieve messages for a specific travel booking
    #     messages = self.sudo().search([('travel_booking_id', '=', travel_booking_id)])
    #     return messages


class ResUsers(models.Model):
    _inherit = 'res.partner'

    airshipping_ids = fields.One2many('m2st_hk_airshipping.airshipping', 'user_partner_id')
    booking_ids = fields.One2many('m2st_hk_airshipping.travel_booking', 'sender_id')
    # image_1920 = fields.Binary(string='Image', attachment=True)

# "access_m2st_hk_airshipping_airshipping_portal_user","m2st.hk.airshipping.airshipping portal user access","model_m2st_hk_airshipping_airshipping","base.group_portal","1","1","1","0"
# "access_m2st_hk_airshipping_publicity_portal_user","m2st.hk.airshipping.publicity portal user access","model_m2st_hk_airshipping_publicity","base.group_portal","1","1","1","0"
# "access_m2st_hk_airshipping_airshipping_file_upload_portal_user","m2st.hk.airshipping.airshipping file upload portal user access","model_m2st_hk_airshipping_airshipping_file_upload","base.group_portal","1","1","1","0"
