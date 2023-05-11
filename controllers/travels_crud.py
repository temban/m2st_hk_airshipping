from odoo import http, fields
from odoo.http import request
import json


class GET_TRAVELS(http.Controller):
    # Controller that uploads a travel documents
    @http.route('/api/file_upload_submit', type='json', auth='public', website=True, csrf=False, methods=['POST'])
    def file_upload_submit(self, **kwargs):
        check_cni = request.env['m2st_hk_airshipping.airshipping_file_upload'].sudo().search(
            [('partner_id', '=', 3), ('cni_name', '!=', '')])
        values = {
            'partner_id': http.request.env.user.partner_id.id,
            'cni_doc': kwargs['cni_doc'].read(),
            'cni_name': kwargs['cni_doc'].filename,
            'ticket_doc': kwargs['ticket_doc'].read(),
            'ticket_name': kwargs['ticket_doc'].filename,
        }
        values1 = {
            'partner_id': http.request.env.user.partner_id.id,
            'ticket_doc': kwargs['ticket_doc'].read(),
            'ticket_name': kwargs['ticket_doc'].filename,
        }
        if check_cni:
            request.env['m2st_hk_airshipping.airshipping_file_upload'].sudo().create(values1)
        else:
            request.env['m2st_hk_airshipping.airshipping_file_upload'].sudo().create(values)

        return {'status': 'success'}

    # Controller that creates a new travel
    @http.route('/api/travel/create', type='json', auth='public', website=True, csrf=False, methods=['POST'])
    def travel_create(self, **kwargs):

        travel = {
            'user_partner_id': http.request.env.user.partner_id.id,
            'travel_type': kwargs.get('travel_type'),
            'departure_town': kwargs.get('departure_town'),
            'arrival_town': kwargs.get('arrival_town'),
            'departure_date': fields.Date.to_date(kwargs.get('departure_date')),
            'arrival_date': fields.Date.to_date(kwargs.get('arrival_date')),
            'kilo_qty': kwargs.get('kilo_qty'),
            'price_per_kilo': kwargs.get('price_per_kilo'),
            'type_of_luggage_accepted': kwargs.get('type_of_luggage_accepted'),
        }
        travel_info = request.env['m2st_hk_airshipping.airshipping'].sudo().create(travel)
        return {'status': 'success',
                'travel': {
                    'id': travel_info.id,
                    'user_partner_id': http.request.env.user.partner_id.id,
                    'travel_type': travel_info.travel_type,
                    'departure_town': travel_info.departure_town,
                    'arrival_town': travel_info.arrival_town,
                    'validation': travel_info.Validation,
                    'departure_date': travel_info.departure_date.strftime('%Y-%m-%d'),
                    'arrival_date': travel_info.arrival_date.strftime('%Y-%m-%d'),
                    'kilo_qty': travel_info.kilo_qty,
                    'price_per_kilo': travel_info.price_per_kilo,
                    'type_of_luggage_accepted': travel_info.type_of_luggage_accepted,
                }}

    # Controller that gets all travels
    @http.route('/all/air/travels', type='http', auth='public', csrf=False, website=True, methods=['GET'], cors='*')
    def travels(self, **kwargs):
        travels = request.env['m2st_hk_airshipping.airshipping'].sudo().search([])

        travels_list = []
        for travel in travels:
            travels_dict = {
                'id': travel.id,
                'travel_type': travel.travel_type,
                'departure_town': travel.departure_town,
                'arrival_town': travel.arrival_town,
                'validation': travel.Validation,
                'departure_date': travel.departure_date.strftime('%Y-%m-%d'),
                'arrival_date': travel.arrival_date.strftime('%Y-%m-%d'),
                'kilo_qty': travel.kilo_qty,
                'price_per_kilo': travel.price_per_kilo,
                'type_of_luggage_accepted': travel.type_of_luggage_accepted,
                'user': {
                    'user_id': travel.user_partner_id.id,
                    'user_name': travel.user_partner_id.name,
                    'user_email': travel.user_partner_id.email,
                }
            }
            travels_list.append(travels_dict)
            data = {'status': 200, 'response': travels_list, 'message': 'success'}
            print(data)
        return json.dumps(data)

    # Controller that search travels by source and destination
    @http.route('/search/travel', type='json', auth='public', csrf=False, website=True, methods=['POST'], cors='*')
    def travel_search(self, **kw):
        print(kw)
        departure_town = kw.get('departure_town')
        arrival_town = kw.get('arrival_town')
        print(kw)
        airshippings = request.env['m2st_hk_airshipping.airshipping'].sudo().search(
            [('departure_town', '=', departure_town), ('arrival_town', '=', arrival_town)])
        travels_search = []

        for travel in airshippings:
            travels_results = {
                'travel_type': travel.travel_type,
                'departure_town': travel.departure_town,
                'arrival_town': travel.arrival_town,
                'validation': travel.Validation,
                'departure_date': travel.departure_date.strftime('%Y-%m-%d'),
                'arrival_date': travel.arrival_date.strftime('%Y-%m-%d'),
                'kilo_qty': travel.kilo_qty,
                'price_per_kilo': travel.price_per_kilo,
                'type_of_luggage_accepted': travel.type_of_luggage_accepted,
                'user': {
                    'user_id': travel.user_partner_id.id,
                    'user_name': travel.user_partner_id.name,
                    'user_email': travel.user_partner_id.email,
                }
            }
            travels_search.append(travels_results)
        result = {'status': 200, 'response': travels_search, 'message': 'success'}
        return result

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
                'validation': travel.Validation,
                'departure_date': travel.departure_date.strftime('%Y-%m-%d'),
                'arrival_date': travel.arrival_date.strftime('%Y-%m-%d'),
                'kilo_qty': travel.kilo_qty,
                'price_per_kilo': travel.price_per_kilo,
                'type_of_luggage_accepted': travel.type_of_luggage_accepted,
                'user': {
                    'user_id': travel.user_partner_id.id,
                    'user_name': travel.user_partner_id.name,
                    'user_email': travel.user_partner_id.email,
                }
            }
            result = {'status': 200, 'response': travel_result, 'message': 'success'}
            return json.dumps(result)

    # Controller that get all current user travels by partner id
    @http.route('/api/current/user/travels', type='http', auth='user', csrf=False, website=True, methods=['GET'],
                cors='*')
    def user_travel_list(self, **kw):
        travels = request.env['m2st_hk_airshipping.airshipping'].search(
            [('user_partner_id', '=', http.request.env.user.partner_id.id)])
        print(http.request.env.user.partner_id.id, travels)
        user_travels_list = []
        for user_travel in travels:
            travels_dict = {
                'id': user_travel.id,
                'travel_type': user_travel.travel_type,
                'departure_town': user_travel.departure_town,
                'arrival_town': user_travel.arrival_town,
                'validation': user_travel.Validation,
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

    # Controller that get all current user travels by partner id
    @http.route('/api/user/all/travels/<int:partner_id>', type='http', auth='user', csrf=False, website=True,
                methods=['GET'],
                cors='*')
    def user_travel_list(self, partner_id, **kw):
        travels = request.env['m2st_hk_airshipping.airshipping'].search([('user_partner_id', '=', partner_id)])
        print(http.request.env.user.partner_id.id, travels)
        user_travels_list = []
        for user_travel in travels:
            travels_dict = {
                'id': user_travel.id,
                'travel_type': user_travel.travel_type,
                'departure_town': user_travel.departure_town,
                'arrival_town': user_travel.arrival_town,
                'validation': user_travel.Validation,
                'departure_date': user_travel.departure_date.strftime('%Y-%m-%d'),
                'arrival_date': user_travel.arrival_date.strftime('%Y-%m-%d'),
                'kilo_qty': user_travel.kilo_qty,
                'price_per_kilo': user_travel.price_per_kilo,
                'type_of_luggage_accepted': user_travel.type_of_luggage_accepted,
                'user': {
                    'user_id': user_travel.user_partner_id.id,
                    'user_name': user_travel.user_partner_id.name,
                    'user_email': user_travel.user_partner_id.email,
                }
            }
            user_travels_list.append(travels_dict)
            data = {'status': 200, 'response': user_travels_list, 'message': 'success'}
            print(data)
        return json.dumps(data)

    # Controller that delete a travel
    @http.route('/api/travel/delete/<int:airshipping_id>', auth='user', csrf=False, website=True, methods=['DELETE'],
                cors='*')
    def delete_travel(self, airshipping_id, **kw):
        travel = request.env['m2st_hk_airshipping.airshipping'].sudo().browse(airshipping_id)
        if not travel:
            return request.not_found()
        travel.unlink()
        return json.dumps({'status': 200, 'message': 'deleted'})

    # Controller that update a travel by id
    @http.route('/travel/update/<int:travel_id>', type='json', auth='user', methods=['POST'], website=True, csrf=False)
    def update_travel(self, travel_id, **kwargs):
        travel = request.env['m2st_hk_airshipping.airshipping'].sudo().browse(travel_id)
        print(travel.user_partner_id.id)
        print(http.request.env.user.partner_id.id)
        if travel.user_partner_id.id == http.request.env.user.partner_id.id:
            travel.write({
                'travel_type': kwargs.get('travel_type'),
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
                'validation': travel.Validation,
                'departure_date': travel.departure_date.strftime('%Y-%m-%d'),
                'arrival_date': travel.arrival_date.strftime('%Y-%m-%d'),
                'kilo_qty': travel.kilo_qty,
                'price_per_kilo': travel.price_per_kilo,
                'type_of_luggage_accepted': travel.type_of_luggage_accepted,
            }
            data = {'status': 200, 'response': travel_updated, 'message': 'success'}
            return data
        else:
            return 'this is not your travel'
