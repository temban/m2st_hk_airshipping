from odoo import http, fields
from odoo.http import request
import json
import base64
from werkzeug.wrappers import Response


class TRAVEL_CRUD(http.Controller):

    # Controller that uploads a travel documents
    @http.route('/travel/document/upload', type='http', auth='user', website=True, csrf=False, methods=['POST'], cors='*')
    def create_file_upload(self, **kwargs):
        # Read the file data and convert to base64
        cni_doc_data = kwargs['cni_doc'].read()
        cni_doc_name = kwargs['cni_doc']
        cni_doc_base64 = base64.b64encode(cni_doc_data).decode('utf-8') if cni_doc_data else False

        ticket_doc_data = kwargs['ticket_doc'].read()
        ticket_doc_name = kwargs['ticket_doc']
        ticket_doc_base64 = base64.b64encode(ticket_doc_data).decode('utf-8') if ticket_doc_data else False

        values = {
            'cni_doc': cni_doc_base64,
            'cni_name': cni_doc_name.filename,
            'ticket_doc': ticket_doc_base64,
            'ticket_name': ticket_doc_name.filename,
            'travel_id': kwargs.get('travel_id')
        }
        new_file_upload = request.env['m2st_hk_airshipping.airshipping_file_upload'].sudo().create(values)
        return json.dumps({'file_upload_id': new_file_upload.id})
        # return json.dumps({'file_upload_id': new_file_upload.cni_doc.decode('utf-8')})

    @http.route('/update/travel/document/upload/<int:file_upload_id>',  type='http', auth='user', website=True, csrf=False, methods=['POST'], cors='*')
    def update_file_upload(self, file_upload_id, **kwargs):
        file_upload = request.env['m2st_hk_airshipping.airshipping_file_upload'].sudo().browse(file_upload_id)
        # Read the file data and convert to base64
        cni_doc_data = kwargs['cni_doc'].read()
        cni_doc_name = kwargs['cni_doc']
        cni_doc_base64 = base64.b64encode(cni_doc_data).decode('utf-8') if cni_doc_data else False

        ticket_doc_data = kwargs['ticket_doc'].read()
        ticket_doc_name = kwargs['ticket_doc']
        ticket_doc_base64 = base64.b64encode(ticket_doc_data).decode('utf-8') if ticket_doc_data else False

        values = {
            'cni_doc': cni_doc_base64,
            'cni_name': cni_doc_name.filename,
            'ticket_doc': ticket_doc_base64,
            'ticket_name': ticket_doc_name.filename,
        }
        updated_file_upload = file_upload.write(values)
        return json.dumps({'status': 200, 'message': 'success'})

    # @http.route('/delete_file_upload/<int:file_upload_id>', type='json', auth="user", methods=['POST'])
    # def delete_file_upload(self, file_upload_id, **kwargs):
    #     file_upload = request.env['m2st_hk_airshipping.airshipping_file_upload'].sudo().browse(file_upload_id)
    #     file_upload.unlink()
    #     return response(status=200)

    @http.route('/list_file_uploads', type='json', auth="user", methods=['GET'])
    def list_file_uploads(self, **kwargs):
        file_uploads = request.env['m2st_hk_airshipping.airshipping_file_upload'].sudo().search([])
        return {'file_uploads': file_uploads.read()}

    # Controller that creates a new travel
    @http.route('/api/travel/create', type='json', auth='user', website=True, csrf=False, methods=['POST'], cors='*')
    def travel_create(self, **kwargs):

        travel = {
            'user_partner_id': http.request.env.user.partner_id.id,
            'departure_town': kwargs.get('departure_town'),
            'arrival_town': kwargs.get('arrival_town'),
            'departure_date': fields.Date.to_date(kwargs.get('departure_date')),
            'arrival_date': fields.Date.to_date(kwargs.get('arrival_date')),
            'kilo_qty': kwargs.get('kilo_qty'),
            'price_per_kilo': kwargs.get('price_per_kilo'),
            'type_of_luggage_accepted': kwargs.get('type_of_luggage_accepted'),
        }
        travel_info = request.env['m2st_hk_airshipping.airshipping'].sudo().create(travel)
        if travel_info:
            return {'status': 'success',
                    'travel': {
                        'id': travel_info.id,
                        'user_partner_id': http.request.env.user.partner_id.id,
                        'travel_type': travel_info.travel_type,
                        'departure_town': travel_info.departure_town,
                        'arrival_town': travel_info.arrival_town,
                        'status': travel_info.status,
                        'departure_date': travel_info.departure_date.strftime('%Y-%m-%d'),
                        'arrival_date': travel_info.arrival_date.strftime('%Y-%m-%d'),
                        'kilo_qty': travel_info.kilo_qty,
                        'price_per_kilo': travel_info.price_per_kilo,
                        'type_of_luggage_accepted': travel_info.type_of_luggage_accepted,
                    }}
        else:
            return "Request failed!"

    # Controller that gets all travels
    @http.route('/all/air/travels', type='http', auth='public', csrf=False, website=True, methods=['GET'], cors='*')
    def travels(self, **kwargs):
        travels = request.env['m2st_hk_airshipping.airshipping'].sudo().search(
            [('status', '=', 'accepted'), ('disable', '=', False)])
        travels_list = []
        if travels:
            for travel in travels:
                travels_dict = {
                    'id': travel.id,
                    'travel_type': travel.travel_type,
                    'departure_town': travel.departure_town,
                    'arrival_town': travel.arrival_town,
                    'status': travel.status,
                    'disable': travel.disable,
                    'departure_date': travel.departure_date.strftime('%Y-%m-%d'),
                    'arrival_date': travel.arrival_date.strftime('%Y-%m-%d'),
                    'kilo_qty': travel.kilo_qty,
                    'price_per_kilo': travel.price_per_kilo,
                    'type_of_luggage_accepted': travel.type_of_luggage_accepted,
                    'user': {
                        'user_id': travel.user_partner_id.id,
                        'user_name': travel.user_partner_id.name,
                        'user_email': travel.user_partner_id.email,
                        'image_1920': travel.user_partner_id.image_1920.decode('utf-8')
                    }
                }
                travels_list.append(travels_dict)
                data = {'status': 200, 'response': travels_list, 'message': 'success'}
                print(data)
            return json.dumps(data)
        else:
            return 'Empty!'

    # Controller that search travels by source and destination
    @http.route('/search/travel', type='json', auth='public', csrf=False, website=True, methods=['POST'], cors='*')
    def travel_search(self, **kw):
        print(kw)
        departure_town = kw.get('departure_town')
        arrival_town = kw.get('arrival_town')
        travel_type = kw.get('travel_type')
        print(kw)
        airshippings = request.env['m2st_hk_airshipping.airshipping'].sudo().search(
            [('travel_type', '=', travel_type), ('departure_town', '=', departure_town),
             ('arrival_town', '=', arrival_town), ('status', '=', 'accepted'), ('disable', '=', False)])
        travels_search = []
        if airshippings:
            for travel in airshippings:
                travels_results = {
                    'id': travel.id,
                    'travel_type': travel.travel_type,
                    'departure_town': travel.departure_town,
                    'arrival_town': travel.arrival_town,
                    'status': travel.status,
                    'disable': travel.disable,
                    'departure_date': travel.departure_date.strftime('%Y-%m-%d'),
                    'arrival_date': travel.arrival_date.strftime('%Y-%m-%d'),
                    'kilo_qty': travel.kilo_qty,
                    'price_per_kilo': travel.price_per_kilo,
                    'type_of_luggage_accepted': travel.type_of_luggage_accepted,
                    'user': {
                        'user_id': travel.user_partner_id.id,
                        'user_name': travel.user_partner_id.name,
                        'user_email': travel.user_partner_id.email,
                        'image_1920': travel.user_partner_id.image_1920.decode('utf-8')
                    }
                }
                travels_search.append(travels_results)
            result = {'status': 200, 'response': travels_search, 'message': 'success'}
            return result
        else:
            return 'Empty!'

    # controller that gets a travel by id
    @http.route('/travel/view/<int:travel_id>', type='http', auth='user', csrf=False, website=True, methods=['GET'],
                cors='*')
    def view_travel(self, travel_id, **kw):
        travel = request.env['m2st_hk_airshipping.airshipping'].browse(travel_id)
        if travel:
            travel_result = {
                'id': travel.id,
                'travel_type': travel.travel_type,
                'departure_town': travel.departure_town,
                'arrival_town': travel.arrival_town,
                'status': travel.status,
                'disable': travel.disable,
                'departure_date': travel.departure_date.strftime('%Y-%m-%d'),
                'arrival_date': travel.arrival_date.strftime('%Y-%m-%d'),
                'kilo_qty': travel.kilo_qty,
                'price_per_kilo': travel.price_per_kilo,
                'type_of_luggage_accepted': travel.type_of_luggage_accepted,
                'user': {
                    'user_id': travel.user_partner_id.id,
                    'user_name': travel.user_partner_id.name,
                    'user_email': travel.user_partner_id.email,
                    'image_1920': travel.user_partner_id.image_1920.decode('utf-8')
                }
            }
            result = {'status': 200, 'response': travel_result, 'message': 'success'}
            return json.dumps(result)
        else:
            return 'Not found!'

    # Controller that get all current user travels by partner id
    @http.route('/api/current/user/travels', type='http', auth='user', csrf=False, website=True, methods=['GET'],
                cors='*')
    def current_user_travel_list(self, **kw):
        travels = request.env['m2st_hk_airshipping.airshipping'].search(
            [('user_partner_id', '=', http.request.env.user.partner_id.id)])
        user_travels_list = []
        if travels:
            for user_travel in travels:
                travels_dict = {
                    'id': user_travel.id,
                    'travel_type': user_travel.travel_type,
                    'departure_town': user_travel.departure_town,
                    'arrival_town': user_travel.arrival_town,
                    'status': user_travel.status,
                    'disable': user_travel.disable,
                    'departure_date': user_travel.departure_date.strftime('%Y-%m-%d'),
                    'arrival_date': user_travel.arrival_date.strftime('%Y-%m-%d'),
                    'kilo_qty': user_travel.kilo_qty,
                    'price_per_kilo': user_travel.price_per_kilo,
                    'type_of_luggage_accepted': user_travel.type_of_luggage_accepted,
                }
                user_travels_list.append(travels_dict)
                data = {'status': 200, 'response': user_travels_list, 'message': 'success'}
                print(data)
            return json.dumps(data)
        else:
            return 'Empty'

    # Controller that get all current user travels by partner id
    @http.route('/api/user/all/travels/<int:partner_id>', type='http', auth='user', csrf=False, website=True,
                methods=['GET'], cors='*')
    def user_travel_list(self, partner_id, **kw):
        travels = request.env['m2st_hk_airshipping.airshipping'].search([('user_partner_id', '=', partner_id)])
        user_travels_list = []
        if travels:
            for user_travel in travels:
                travels_dict = {
                    'id': user_travel.id,
                    'travel_type': user_travel.travel_type,
                    'departure_town': user_travel.departure_town,
                    'arrival_town': user_travel.arrival_town,
                    'status': user_travel.status,
                    'departure_date': user_travel.departure_date.strftime('%Y-%m-%d'),
                    'arrival_date': user_travel.arrival_date.strftime('%Y-%m-%d'),
                    'kilo_qty': user_travel.kilo_qty,
                    'price_per_kilo': user_travel.price_per_kilo,
                    'type_of_luggage_accepted': user_travel.type_of_luggage_accepted,
                    'user': {
                        'user_id': user_travel.user_partner_id.id,
                        'user_name': user_travel.user_partner_id.name,
                        'user_email': user_travel.user_partner_id.email,
                        'image_1920': user_travel.user_partner_id.image_1920.decode('utf-8')
                    }
                }
                user_travels_list.append(travels_dict)
                data = {'status': 200, 'response': user_travels_list, 'message': 'success'}
                print(data)
            return json.dumps(data)
        else:
            return 'Empty!'

    # Controller that delete a travel
    @http.route('/api/travel/delete/<int:airshipping_id>', auth='user', csrf=False, website=True, methods=['DELETE'],
                cors='*')
    def delete_travel(self, airshipping_id, **kw):
        travel = request.env['m2st_hk_airshipping.airshipping'].browse(airshipping_id)
        if travel:
            travel.write({
                'disable': True,
            })
            return json.dumps({'status': 200, 'message': 'deleted'})
        else:
            return 'Request Failed'

    # Controller that update a travel by id
    @http.route('/travel/update/<int:travel_id>', type='json', auth='user', methods=['PUT'], website=True, csrf=False)
    def update_travel(self, travel_id, **kwargs):
        travel = request.env['m2st_hk_airshipping.airshipping'].sudo().browse(travel_id)
        print(travel.user_partner_id.id)
        print(http.request.env.user.partner_id.id)
        if travel.user_partner_id.id == http.request.env.user.partner_id.id:
            travel.write({
                'departure_town': kwargs.get('departure_town'),
                'arrival_town': kwargs.get('arrival_town'),
                'departure_date': fields.Date.to_date(kwargs.get('departure_date')),
                'arrival_date': fields.Date.to_date(kwargs.get('arrival_date')),
                'kilo_qty': kwargs.get('kilo_qty'),
                'price_per_kilo': kwargs.get('price_per_kilo'),
                'type_of_luggage_accepted': kwargs.get('type_of_luggage_accepted')
            })
            travel_updated = {
                'travel_type': travel.travel_type,
                'departure_town': travel.departure_town,
                'arrival_town': travel.arrival_town,
                'departure_date': travel.departure_date.strftime('%Y-%m-%d'),
                'arrival_date': travel.arrival_date.strftime('%Y-%m-%d'),
                'kilo_qty': travel.kilo_qty,
                'price_per_kilo': travel.price_per_kilo,
                'type_of_luggage_accepted': travel.type_of_luggage_accepted,
            }
            data = {'status': 200, 'response': travel_updated, 'message': 'success'}
            return data
        else:
            return 'Something went wrong!'

    # @http.route('/employee/get/all_air/travels', type='http', auth='user', csrf=False, website=True, methods=['GET'], cors='*')
    # def employee_get_all_travels(self, **kwargs):
    #     travels = request.env['m2st_hk_airshipping.airshipping'].sudo().search([])
    #     travels_list = []
    #     if travels:
    #         for travel in travels:
    #             travels_dict = {
    #                 'id': travel.id,
    #                 'travel_type': travel.travel_type,
    #                 'departure_town': travel.departure_town,
    #                 'arrival_town': travel.arrival_town,
    #                 'validation': travel.Validation,
    #                 'disable': travel.disable,
    #                 'departure_date': travel.departure_date.strftime('%Y-%m-%d'),
    #                 'arrival_date': travel.arrival_date.strftime('%Y-%m-%d'),
    #                 'kilo_qty': travel.kilo_qty,
    #                 'price_per_kilo': travel.price_per_kilo,
    #                 'type_of_luggage_accepted': travel.type_of_luggage_accepted,
    #                 'user': {
    #                     'user_id': travel.user_partner_id.id,
    #                     'user_name': travel.user_partner_id.name,
    #                     'user_email': travel.user_partner_id.email,
    #                 }
    #             }
    #             travels_list.append(travels_dict)
    #             data = {'status': 200, 'response': travels_list, 'message': 'success'}
    #             print(data)
    #         return json.dumps(data)
    #     else:
    #         return 'Empty!'
    #
    # # Controller to let employee validate user's travel
    # @http.route('/employee/travel/validation/<int:travel_id>', type='json', auth='user', methods=['POST'], website=True,
    #             csrf=False, cors='*')
    # def validate_travel(self, travel_id, **kwargs):
    #     travel = request.env['m2st_hk_airshipping.airshipping'].sudo().browse(travel_id)
    #     if travel:
    #         travel.write({
    #             'Validation': True,
    #         })
    #         travel_validate = {
    #             'id': travel.id,
    #             'travel_type': travel.travel_type,
    #             'departure_town': travel.departure_town,
    #             'arrival_town': travel.arrival_town,
    #             'validation': travel.Validation,
    #             'disable': travel.disable,
    #             'departure_date': travel.departure_date.strftime('%Y-%m-%d'),
    #             'arrival_date': travel.arrival_date.strftime('%Y-%m-%d'),
    #             'kilo_qty': travel.kilo_qty,
    #             'price_per_kilo': travel.price_per_kilo,
    #             'type_of_luggage_accepted': travel.type_of_luggage_accepted,
    #             'user': {
    #                 'user_id': travel.user_partner_id.id,
    #                 'user_name': travel.user_partner_id.name,
    #                 'user_email': travel.user_partner_id.email,
    #             }
    #         }
    #         data = {'status': 200, 'response': travel_validate, 'message': 'success'}
    #         return data
    #     else:
    #         return 'Request failed!'
    #
    # # Controller to let employee reject user's travel
    # @http.route('/employee/travel/rejection/<int:travel_id>', type='json', auth='user', methods=['POST'], website=True,
    #             csrf=False, cors='*')
    # def travel_rejection(self, travel_id, **kwargs):
    #     travel = request.env['m2st_hk_airshipping.airshipping'].sudo().browse(travel_id)
    #     if travel:
    #         travel.write({
    #             'rejected': True,
    #         })
    #         travel_validate = {
    #             'id': travel.id,
    #             'travel_type': travel.travel_type,
    #             'departure_town': travel.departure_town,
    #             'arrival_town': travel.arrival_town,
    #             'validation': travel.Validation,
    #             'disable': travel.disable,
    #             'rejected': travel.rejected,
    #             'departure_date': travel.departure_date.strftime('%Y-%m-%d'),
    #             'arrival_date': travel.arrival_date.strftime('%Y-%m-%d'),
    #             'kilo_qty': travel.kilo_qty,
    #             'price_per_kilo': travel.price_per_kilo,
    #             'type_of_luggage_accepted': travel.type_of_luggage_accepted,
    #             'user': {
    #                 'user_id': travel.user_partner_id.id,
    #                 'user_name': travel.user_partner_id.name,
    #                 'user_email': travel.user_partner_id.email,
    #             }
    #         }
    #         data = {'status': 200, 'response': travel_validate, 'message': 'success'}
    #         return data
    #     else:
    #         return 'Request failed!'
