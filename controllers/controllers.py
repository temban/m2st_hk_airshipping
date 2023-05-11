from odoo import http, fields
from odoo.http import request
from io import BytesIO
import base64
from PIL import Image
import json

class FileUploadController(http.Controller):

    # Controller that redirect to the page of a new travel
    @http.route('/travel/new', auth='public', csrf=False, website=True)
    def file_upload_form(self, **kwargs):
        # check_cni = request.env['m2st_hk_airshipping.airshipping_file_upload'].sudo().search([('partner_id', '=', 3 )])
        # print(check_cni.partner_id.name)
        return http.request.render('m2st_hk_airshipping.travel_create')


    # @http.route('/file_upload/update/<int:file_id>', auth='public', website=True, methods=['POST'])
    # def files_update(self, file_id, **kwargs):
    #     file = request.env['m2st_hk_airshipping.airshipping'].sudo().browse(file_id)
    #     file.write({
    #         'first_file': kwargs['first_file'].read(),
    #         'first_file_name': kwargs['first_file'].filename,
    #         'second_file': kwargs['second_file'].read(),
    #         'second_file_name': kwargs['second_file'].filename,
    #     })
    #     return http.request.redirect('/file_upload/thanks')
    #

    # Controller that gets all travels
    @http.route('/api/airshipping', methods=['GET'], auth='public', website=True, csrf=False)
    def travel_list(self, **kw):
        airshippings = request.env['m2st_hk_airshipping.airshipping'].sudo().search([])
        return request.render('m2st_hk_airshipping.user_airshippings', {'airshippings': airshippings})





    # Controller that get all travel by parner id
    # @http.route('/api/user/airshippings/<int:user_partner_id>', methods=['GET'], auth='public', website=True,
    #             csrf=False)
    # def user_travel_list(self, user_partner_id, **kw):
    #     airshippings = request.env['m2st_hk_airshipping.airshipping'].sudo().search(
    #         [('user_partner_id', '=', user_partner_id)])
    #     return request.render('m2st_hk_airshipping.user_travels', {'airshippings': airshippings})





        @http.route('/create_partner', auth='public', website=True, csrf=False, methods=['POST'])
        def create_partner(self, **kwargs):
            values = {
                'name': kwargs.get('name'),
                'email': kwargs.get('email'),
                'phone': kwargs.get('phone'),
                'street': kwargs.get('street'),
                'city': kwargs.get('city'),
                'zip': kwargs.get('zip'),
            }
            partner = request.env['res.partner'].sudo().create(values)
            return http.request.redirect('/partner_created/%s' % partner.id)

    @http.route('/res/get_data', auth='public', csrf=False, website=True, methods=['GET'])
    def function(self, **kwargs):
        partners = http.request.env['res.partner'].sudo().search([])
        partner_list = []
        for partner in partners:
            partner_dict = {
                'id': partner.id,
                'name': partner.name,
                'email': partner.email,
                'phone': partner.phone,
                # Add any other fields you want to include in the JSON object
            }
            partner_list.append(partner_dict)
        return json.dumps(partner_list)


    @http.route('/my_module/get_data', auth='public', csrf=False, website=True)
    def get_data(self):
        partners = request.env['m2st_hk_airshipping.airshipping'].sudo().search([])
        partner_data = []
        for partner in partners:
            partner_data.append({
                'user_partner_id': partner.user_partner_id.id,
                'Type_voyage': partner.travel_type,
                'departure_town': partner.departure_town,
                'arrival_town': partner.arrival_town,
                # 'departure_date': partner.departure_date,
                # 'arrival_date': partner.arrival_date,
                'kilo_qty': partner.kilo_qty,
                'price_per_kilo': partner.price_per_kilo,
                'type_of_luggage_accepted': partner.type_of_luggage_accepted,
            })
        return json.dumps(partner_data)

