from odoo import http, fields
from odoo.http import request
import json
import base64
import uuid
from datetime import datetime, timedelta

from werkzeug.wrappers import Response


class TravelBookingController(http.Controller):

    @http.route('/air/travel/booking/new_price/<int:booking_id>', auth='user', csrf=False, website=True,
                methods=['PUT'], type='json', cors='*')
    def user_new_price_booking(self, booking_id, **kw):
        new_price = kw.get('new_price')
        booking = request.env['m2st_hk_airshipping.travel_booking'].sudo().browse(booking_id)
        if booking.status == 'accepted' or booking.status == 'rejected' or booking.status == 'completed':
            error_response = {
                'success': False,
                'error_message': 'This booking is no longer accessible!'
            }
            return error_response
        if booking:
            # booking.travel_id.sudo().write({
            #     'price_per_kilo': new_price,
            # })
            booking.sudo().write({
                'kilo_booked_price': booking.kilo_booked * new_price,
                'status': 'accepted',
            })
            # print(" booking.travel_id.kilo_qty", booking.travel_id.kilo_qty, "int(booking.kilo_booked)")
            return {'status': 200, 'message': 'Price changed!'}
        else:
            return 'Request Failed'

    @http.route('/air/booking/completed', auth='user', csrf=False, website=True,
                methods=['PUT'], type='json', cors='*')
    def complete_booking(self, **post):
        booking_code = post.get('booking_code')
        booking = request.env['m2st_hk_airshipping.travel_booking'].sudo().search([('code', '=', booking_code)])
        if booking.status == 'pending' or booking.status == 'rejected':
            error_response = {
                'success': False,
                'error_message': 'This booking can not change to complete!'
            }
            return error_response
        if booking.status == 'completed':
            error_response = {
                'success': False,
                'error_message': 'This booking was already completed!'
            }
            return error_response
        if booking:
            booking.write({'status': 'completed'})
            return "Booking completed successfully."
        else:
            return "Booking not found."

    @http.route('/air/open/travel/negotiations/<int:booking_id>', auth='user', csrf=False, website=True,
                methods=['PUT'], type='json', cors='*')
    def user_negotiations_booking(self, booking_id, **kw):
        booking = request.env['m2st_hk_airshipping.travel_booking'].sudo().browse(booking_id)
        if not booking:
            error_response = {
                'success': False,
                'error_message': 'Booking not found!'
            }
            return error_response
        if booking:
            booking.travel_id.sudo().write({
                'negotiation': True,
            })
            # print(" booking.travel_id.kilo_qty", booking.travel_id.kilo_qty, "int(booking.kilo_booked)")
            return {'status': 200, 'message': 'Negotiations activated'}
        else:
            return 'Request Failed'

    @http.route('/air/accept/booking/<int:booking_id>', auth='user', csrf=False, website=True,
                methods=['PUT'], type='json', cors='*')
    def user_confirm_booking(self, booking_id, **kw):
        booking = request.env['m2st_hk_airshipping.travel_booking'].sudo().browse(booking_id)
        if not booking:
            error_response = {
                'success': False,
                'error_message': 'Booking not found!'
            }
            return json.dumps(error_response)
        if booking:
            booking.sudo().write({
                'status': 'accepted',
            })

            booking.travel_id.kilo_qty -= int(booking.kilo_booked)
            # print(" booking.travel_id.kilo_qty", booking.travel_id.kilo_qty, "int(booking.kilo_booked)")
            return {'status': 200, 'message': 'accepted'}
        else:
            return 'Request Failed'

    @http.route('/air/reject/booking/<int:booking_id>', auth='user', csrf=False, website=True,
                methods=['PUT'], type='json', cors='*')
    def user_reject_booking(self, booking_id, **kw):
        booking = request.env['m2st_hk_airshipping.travel_booking'].sudo().browse(booking_id)
        if booking.status == 'rejected' or booking.status == 'completed' or booking.status == 'accepted':
            error_response = {
                'success': False,
                'error_message': 'Operation failed!'
            }
            return error_response
        if booking:
            booking.sudo().write({
                'status': 'rejected',
            })
            # booking.travel_id.kilo_qty -= int(booking.kilo_booked)
            # print(" booking.travel_id.kilo_qty", booking.travel_id.kilo_qty, "int(booking.kilo_booked)")
            return {'status': 200, 'message': 'rejected'}
        else:
            return 'Request Failed'

    @http.route('/air/travel/booking/create', type='json', auth='user', website=True, csrf=False, methods=['POST'],
                cors='*')
    def create_booking(self, **post):
        travel_id = post.get('travel_id')
        receiver_partner_id = post.get('receiver_partner_id')
        receiver_name = post.get('receiver_name')
        receiver_email = post.get('receiver_email')
        receiver_phone = post.get('receiver_phone')
        receiver_address = post.get('receiver_address')
        type_of_luggage = post.get('type_of_luggage')
        kilo_booked = post.get('kilo_booked')
        code = str(uuid.uuid4())[:8]
        if not receiver_partner_id and not (receiver_name and receiver_email and receiver_phone):
            error_response = {
                'success': False,
                'error_message': 'Receiver information is incomplete.'
            }
            return error_response

        booking_vals = {
            'sender_id': http.request.env.user.partner_id.id,
            'travel_id': travel_id,
            'receiver_name': receiver_name,
            'receiver_email': receiver_email,
            'receiver_phone': receiver_phone,
            'receiver_address': receiver_address,
            'code': code,

            'type_of_luggage': type_of_luggage,
            # 'luggage_image_base64': luggage_image_base64,
            'kilo_booked': kilo_booked,
        }
        booking_vals1 = {
            'sender_id': http.request.env.user.partner_id.id,
            'travel_id': travel_id,
            'receiver_partner_id': receiver_partner_id,
            'code': code,

            'type_of_luggage': type_of_luggage,
            # 'luggage_image_base64': luggage_image_base64,
            'kilo_booked': kilo_booked,
        }

        if receiver_partner_id:
            booking = request.env['m2st_hk_airshipping.travel_booking'].sudo().create(booking_vals1)
            booking._onchange_receiver_partner_id()
            booking._onchange_kilo_booked_price()
        elif receiver_name and receiver_email or receiver_phone or receiver_address:
            booking = request.env['m2st_hk_airshipping.travel_booking'].sudo().create(booking_vals)
            booking._onchange_receiver_info()
            booking._onchange_kilo_booked_price()

        success_response = {
            'booking_id': booking.id,
            'kilo_booked': booking.kilo_booked,
            'type_of_luggage': booking.type_of_luggage,
            # 'luggage_image_base64': luggage_image_base64,
            'receiver': {
                'travel_id': booking.travel_id,
                'receiver_partner_id': booking.receiver_partner_id,
                'receiver_name': booking.receiver_name,
                'receiver_email': booking.receiver_email,
                'receiver_phone': booking.receiver_phone,
                'receiver_address': booking.receiver_address,
            }
        }
        return {'status': 200, 'response': success_response, 'message': 'success'}

    @http.route('/air/booking/luggage_image/<int:booking_id>', type='http', auth='user', website=True, csrf=False,
                methods=['PUT'],
                cors='*')
    def update_luggage_image(self, booking_id, **kwargs):
        booking = request.env['m2st_hk_airshipping.travel_booking'].sudo().browse(int(booking_id))

        luggage_image_data = kwargs['luggage_image'].read()
        luggage_image_base64 = base64.b64encode(luggage_image_data).decode('utf-8') if luggage_image_data else False
        result = booking.sudo().write({'luggage_image': luggage_image_base64})
        return json.dumps({'status': 200, 'luggage_image': result, 'message': 'Luggage image updated successfully'})

    @http.route('/air/travel/booking/update/<int:booking_id>', type='json', auth='user', website=True, csrf=False,
                methods=['PUT'], cors='*')
    def update_booking(self, booking_id, **post):
        booking = request.env['m2st_hk_airshipping.travel_booking'].sudo().browse(int(booking_id))
        if not booking:
            error_response = {
                'success': False,
                'error_message': 'Booking not found!'
            }
            return json.dumps(error_response)
        if booking.status == 'accepted' or booking.status == 'rejected' or booking.status == 'completed':
            error_response = {
                'success': False,
                'error_message': 'This booking is no longer accessible!'
            }
            return error_response
        receiver_partner_id = post.get('receiver_partner_id')
        receiver_name = post.get('receiver_name')
        receiver_email = post.get('receiver_email')
        receiver_phone = post.get('receiver_phone')
        receiver_address = post.get('receiver_address')
        code = str(uuid.uuid4())[:8]

        type_of_luggage = post.get('type_of_luggage')
        kilo_booked = post.get('kilo_booked')

        if not booking_id:
            error_response = {
                'success': False,
                'error_message': 'Booking ID is missing.'
            }
            return error_response

        if not booking:
            error_response = {
                'success': False,
                'error_message': 'Booking not found.'
            }
            return error_response

        update_vals = {
            'receiver_name': receiver_name,
            'receiver_email': receiver_email,
            'receiver_phone': receiver_phone,
            'receiver_address': receiver_address,
            'type_of_luggage': type_of_luggage,
            'kilo_booked': kilo_booked,
            'code': code,
        }
        update_vals1 = {
            'receiver_partner_id': receiver_partner_id,
            'type_of_luggage': type_of_luggage,
            'kilo_booked': kilo_booked,
            'code': code,
        }

        if receiver_partner_id:
            booking.write(update_vals1)
            booking._onchange_receiver_info()
            booking._onchange_kilo_booked_price()
        elif receiver_name and receiver_email or receiver_phone or receiver_address:
            booking.write(update_vals)
            booking._onchange_receiver_info()
            booking._onchange_kilo_booked_price()

        success_response = {
            'booking_id': booking.id,
            'kilo_booked': booking.kilo_booked,
            'type_of_luggage': booking.type_of_luggage,
            'receiver': {
                'travel_id': booking.travel_id,
                'receiver_partner_id': booking.receiver_partner_id,
                'receiver_name': booking.receiver_name,
                'receiver_email': booking.receiver_email,
                'receiver_phone': booking.receiver_phone,
                'receiver_address': booking.receiver_address,
            }
        }

        return {'status': 200, 'response': success_response, 'message': 'success'}

    @http.route('/air/api/get_all_bookings', type='http', auth='user', website=True, csrf=False, methods=['GET'],
                cors='*')
    def get_travel_bookings(self, **kw):
        TravelBooking = http.request.env['m2st_hk_airshipping.travel_booking']
        travel_bookings = TravelBooking.sudo().search([('disable', '=', False)])
        bookings_data = []
        for booking in travel_bookings:
            if booking:
                booking_data = {

                    'id': booking.id,
                    'kilo_booked': booking.kilo_booked,
                    'kilo_booked_price': booking.kilo_booked_price,
                    'status': booking.status,
                    'disable': booking.disable,
                    'code': booking.code,
                    # 'negotiation': booking.negotiation,
                    'type_of_luggage': booking.type_of_luggage,
                    'sender': {
                        'sender_id': booking.sender_id.id,
                        'sender_name': booking.sender_id.name,
                        'sender_email': booking.sender_id.email,
                        'sender_phone': booking.sender_id.phone,
                    },
                    'receiver': {
                        'receiver_partner_id': booking.receiver_partner_id.id,
                        'receiver_name': booking.receiver_name,
                        'receiver_email': booking.receiver_email,
                        'receiver_phone': booking.receiver_phone,
                        'receiver_address': booking.receiver_address,
                    },
                    'travel': {
                        'id': booking.travel_id.id,
                        'travel_type': booking.travel_id.travel_type,
                        'departure_town': booking.travel_id.departure_town,
                        'arrival_town': booking.travel_id.arrival_town,
                        'status': booking.travel_id.status,
                        'disable': booking.travel_id.disable,
                        'negotiation': booking.travel_id.negotiation,
                        'departure_date': booking.travel_id.departure_date.strftime('%Y-%m-%d'),
                        'arrival_date': booking.travel_id.arrival_date.strftime('%Y-%m-%d'),
                        'kilo_qty': booking.travel_id.kilo_qty,
                        'price_per_kilo': booking.travel_id.price_per_kilo,
                        'type_of_luggage_accepted': booking.travel_id.type_of_luggage_accepted,
                        'files_uploaded_id': booking.travel_id.files_uploaded_id.id,
                        'traveler': {
                            'user_id': booking.travel_id.user_partner_id.id,
                            'user_name': booking.travel_id.user_partner_id.name,
                            'user_email': booking.travel_id.user_partner_id.email,
                            'image_1920': booking.travel_id.user_partner_id.image_1920.decode(
                                'utf-8') if booking.travel_id.user_partner_id.image_1920 else None
                        }
                    }
                }
                bookings_data.append(booking_data)
        return json.dumps(bookings_data)

    @http.route('/air/current/user/travel/books/<int:travel_id>', type='http', auth='user', website=True, csrf=False,
                methods=['GET'],
                cors='*')
    def current_user_get_travel_bookings(self, travel_id, **kw):
        TravelBooking = http.request.env['m2st_hk_airshipping.travel_booking']
        travel_bookings = TravelBooking.sudo().search(
            [('disable', '=', False), ('travel_id.user_partner_id.id', '=', http.request.env.user.partner_id.id),
             ('travel_id.id', '=', int(travel_id))])
        bookings_data = []
        for booking in travel_bookings:
            if booking:
                booking_data = {
                    'id': booking.id,
                    'kilo_booked': booking.kilo_booked,
                    'kilo_booked_price': booking.kilo_booked_price,
                    'status': booking.status,
                    'disable': booking.disable,
                    'code': booking.code,
                    # 'negotiation': booking.negotiation,
                    'type_of_luggage': booking.type_of_luggage,
                    'sender': {
                        'sender_id': booking.sender_id.id,
                        'sender_name': booking.sender_id.name,
                        'sender_email': booking.sender_id.email,
                        'sender_phone': booking.sender_id.phone,
                    },
                    'receiver': {
                        'receiver_partner_id': booking.receiver_partner_id.id,
                        'receiver_name': booking.receiver_name,
                        'receiver_email': booking.receiver_email,
                        'receiver_phone': booking.receiver_phone,
                        'receiver_address': booking.receiver_address,
                    },
                    'travel': {
                        'id': booking.travel_id.id,
                        'travel_type': booking.travel_id.travel_type,
                        'departure_town': booking.travel_id.departure_town,
                        'arrival_town': booking.travel_id.arrival_town,
                        'status': booking.travel_id.status,
                        'disable': booking.travel_id.disable,
                        'negotiation': booking.travel_id.negotiation,
                        'departure_date': booking.travel_id.departure_date.strftime('%Y-%m-%d'),
                        'arrival_date': booking.travel_id.arrival_date.strftime('%Y-%m-%d'),
                        'kilo_qty': booking.travel_id.kilo_qty,
                        'price_per_kilo': booking.travel_id.price_per_kilo,
                        'type_of_luggage_accepted': booking.travel_id.type_of_luggage_accepted,
                        'files_uploaded_id': booking.travel_id.files_uploaded_id.id,
                        'traveler': {
                            'user_id': booking.travel_id.user_partner_id.id,
                            'user_name': booking.travel_id.user_partner_id.name,
                            'user_email': booking.travel_id.user_partner_id.email,
                            'image_1920': booking.travel_id.user_partner_id.image_1920.decode(
                                'utf-8') if booking.travel_id.user_partner_id.image_1920 else None
                        }
                    }
                }
                bookings_data.append(booking_data)
        return json.dumps(bookings_data)

    @http.route('/air/current/user/my_booking/made', type='http', auth='user', website=True, csrf=False,
                methods=['GET'],
                cors='*')
    def current_user_get_bookings(self, **kw):
        TravelBooking = http.request.env['m2st_hk_airshipping.travel_booking']
        travel_bookings = TravelBooking.sudo().search(
            [('disable', '=', False), ('sender_id.id', '=', http.request.env.user.partner_id.id)])
        bookings_data = []
        for booking in travel_bookings:
            if booking:
                booking_data = {
                    'id': booking.id,
                    'kilo_booked': booking.kilo_booked,
                    'kilo_booked_price': booking.kilo_booked_price,
                    'status': booking.status,
                    'disable': booking.disable,
                    'code': booking.code,
                    # 'negotiation': booking.negotiation,
                    'type_of_luggage': booking.type_of_luggage,
                    'sender': {
                        'sender_id': booking.sender_id.id,
                        'sender_name': booking.sender_id.name,
                        'sender_email': booking.sender_id.email,
                        'sender_phone': booking.sender_id.phone,
                    },
                    'receiver': {
                        'receiver_partner_id': booking.receiver_partner_id.id,
                        'receiver_name': booking.receiver_name,
                        'receiver_email': booking.receiver_email,
                        'receiver_phone': booking.receiver_phone,
                        'receiver_address': booking.receiver_address,
                    },
                    'travel': {
                        'id': booking.travel_id.id,
                        'travel_type': booking.travel_id.travel_type,
                        'departure_town': booking.travel_id.departure_town,
                        'arrival_town': booking.travel_id.arrival_town,
                        'status': booking.travel_id.status,
                        'disable': booking.travel_id.disable,
                        'negotiation': booking.travel_id.negotiation,
                        'departure_date': booking.travel_id.departure_date.strftime('%Y-%m-%d'),
                        'arrival_date': booking.travel_id.arrival_date.strftime('%Y-%m-%d'),
                        'kilo_qty': booking.travel_id.kilo_qty,
                        'price_per_kilo': booking.travel_id.price_per_kilo,
                        'type_of_luggage_accepted': booking.travel_id.type_of_luggage_accepted,
                        'files_uploaded_id': booking.travel_id.files_uploaded_id.id,
                        'traveler': {
                            'user_id': booking.travel_id.user_partner_id.id,
                            'user_name': booking.travel_id.user_partner_id.name,
                            'user_email': booking.travel_id.user_partner_id.email,
                            'image_1920': booking.travel_id.user_partner_id.image_1920.decode(
                                'utf-8') if booking.travel_id.user_partner_id.image_1920 else None
                        }
                    }
                }
                bookings_data.append(booking_data)
        return json.dumps(bookings_data)

    @http.route('/air/current/user/travel/booked', type='http', auth='user', website=True, csrf=False, methods=['GET'],
                cors='*')
    def current_user_get_travel_reservations(self, **kw):
        TravelBooking = http.request.env['m2st_hk_airshipping.travel_booking']
        travel_bookings = TravelBooking.sudo().search(
            [('disable', '=', False), ('travel_id.user_partner_id.id', '=', http.request.env.user.partner_id.id)])
        bookings_data = []
        for booking in travel_bookings:
            if booking:
                booking_data = {
                    'id': booking.id,
                    'kilo_booked': booking.kilo_booked,
                    'kilo_booked_price': booking.kilo_booked_price,
                    'status': booking.status,
                    'disable': booking.disable,
                    'code': booking.code,
                    # 'negotiation': booking.negotiation,
                    'type_of_luggage': booking.type_of_luggage,
                    'sender': {
                        'sender_id': booking.sender_id.id,
                        'sender_name': booking.sender_id.name,
                        'sender_email': booking.sender_id.email,
                        'sender_phone': booking.sender_id.phone,
                    },
                    'receiver': {
                        'receiver_partner_id': booking.receiver_partner_id.id,
                        'receiver_name': booking.receiver_name,
                        'receiver_email': booking.receiver_email,
                        'receiver_phone': booking.receiver_phone,
                        'receiver_address': booking.receiver_address,
                    },
                    'travel': {
                        'id': booking.travel_id.id,
                        'travel_type': booking.travel_id.travel_type,
                        'departure_town': booking.travel_id.departure_town,
                        'arrival_town': booking.travel_id.arrival_town,
                        'status': booking.travel_id.status,
                        'disable': booking.travel_id.disable,
                        'negotiation': booking.travel_id.negotiation,
                        'departure_date': booking.travel_id.departure_date.strftime('%Y-%m-%d'),
                        'arrival_date': booking.travel_id.arrival_date.strftime('%Y-%m-%d'),
                        'kilo_qty': booking.travel_id.kilo_qty,
                        'price_per_kilo': booking.travel_id.price_per_kilo,
                        'type_of_luggage_accepted': booking.travel_id.type_of_luggage_accepted,
                        'files_uploaded_id': booking.travel_id.files_uploaded_id.id,
                        'traveler': {
                            'user_id': booking.travel_id.user_partner_id.id,
                            'user_name': booking.travel_id.user_partner_id.name,
                            'user_email': booking.travel_id.user_partner_id.email,
                            'image_1920': booking.travel_id.user_partner_id.image_1920.decode(
                                'utf-8') if booking.travel_id.user_partner_id.image_1920 else None
                        }
                    }
                }
                bookings_data.append(booking_data)
        return json.dumps(bookings_data)

    @http.route('/air/current/user/transfer/booking/<int:booking_id>', auth='user', csrf=False, website=True,
                methods=['PUT'], type='json', cors='*')
    def user_transfer_booking(self, booking_id, **kw):
        booking = request.env['m2st_hk_airshipping.travel_booking'].sudo().browse(booking_id)
        if not booking:
            error_response = {
                'success': False,
                'error_message': 'Booking not found!'
            }
            return json.dumps(error_response)
        if booking.status == 'accepted' or booking.status == 'completed':
            error_response = {
                'success': False,
                'error_message': 'This booking is no longer accessible!'
            }
            return error_response
        new_travel_id = kw.get('new_travel_id')
        code = str(uuid.uuid4())[:8]
        if booking:
            booking.write({
                'travel_id': new_travel_id,
                'code': code,
                'status': 'pending'
            })
            booking._onchange_receiver_info()
            booking._onchange_kilo_booked_price()
            return {'status': 200, 'message': 'Transferred'}
        else:
            return 'Request Failed'

    @http.route('/air/booking/<int:booking_id>/delete', auth='user', csrf=False, website=True,
                methods=['DELETE'], cors='*')
    def delete_booking(self, booking_id):
        booking = request.env['m2st_hk_airshipping.travel_booking'].sudo().browse(booking_id)

        if not booking:
            error_response = {
                'success': False,
                'error_message': 'Booking not found!'
            }
            return json.dumps(error_response)
        if booking.status == 'accepted' or booking.status == 'completed':
            error_response = {
                'success': False,
                'error_message': 'Deleting confirm booking is not allowed.'
            }
            return json.dumps(error_response)

        booking.write({
            'disable': True,
        })

        success_response = {
            'success': True,
            'message': 'Booking deleted successfully.'
        }
        return json.dumps(success_response)

    @http.route('/air/view/booking/<int:booking_id>', type='http', auth='user', website=True, csrf=False,
                methods=['GET'],
                cors='*')
    def view_booking(self, booking_id):
        booking = request.env['m2st_hk_airshipping.travel_booking'].sudo().browse(booking_id)
        if not booking:
            error_response = {
                'success': False,
                'error_message': 'Booking not found!'
            }
            return json.dumps(error_response)
        if booking.disable:
            error_response = {
                'success': False,
                'error_message': 'This booking was deleted.'
            }
            return json.dumps(error_response)
        booking_data = {
            'id': booking.id,
            'kilo_booked': booking.kilo_booked,
            'kilo_booked_price': booking.kilo_booked_price,
            'status': booking.status,
            'disable': booking.disable,
            'code': booking.code,
            # 'negotiation': booking.negotiation,
            'type_of_luggage': booking.type_of_luggage,
            'sender': {
                'sender_id': booking.sender_id.id,
                'sender_name': booking.sender_id.name,
                'sender_email': booking.sender_id.email,
                'sender_phone': booking.sender_id.phone,
            },
            'receiver': {
                'receiver_partner_id': booking.receiver_partner_id.id,
                'receiver_name': booking.receiver_name,
                'receiver_email': booking.receiver_email,
                'receiver_phone': booking.receiver_phone,
                'receiver_address': booking.receiver_address,
            },
            'travel': {
                'id': booking.travel_id.id,
                'travel_type': booking.travel_id.travel_type,
                'departure_town': booking.travel_id.departure_town,
                'arrival_town': booking.travel_id.arrival_town,
                'status': booking.travel_id.status,
                'disable': booking.travel_id.disable,
                'negotiation': booking.travel_id.negotiation,
                'departure_date': booking.travel_id.departure_date.strftime('%Y-%m-%d'),
                'arrival_date': booking.travel_id.arrival_date.strftime('%Y-%m-%d'),
                'kilo_qty': booking.travel_id.kilo_qty,
                'price_per_kilo': booking.travel_id.price_per_kilo,
                'type_of_luggage_accepted': booking.travel_id.type_of_luggage_accepted,
                'files_uploaded_id': booking.travel_id.files_uploaded_id.id,
                'traveler': {
                    'user_id': booking.travel_id.user_partner_id.id,
                    'user_name': booking.travel_id.user_partner_id.name,
                    'user_email': booking.travel_id.user_partner_id.email,
                    'image_1920': booking.travel_id.user_partner_id.image_1920.decode(
                        'utf-8') if booking.travel_id.user_partner_id.image_1920 else None
                }
            }
        }
        return json.dumps(booking_data)

#
# @http.route('/air/booking/completed/<int:booking_id>', auth='user', csrf=False, website=True,
#             methods=['PUT'], type='json', cors='*')
# def user_completed_booking(self, booking_id, **kw):
#     booking = request.env['m2st_hk_airshipping.travel_booking'].sudo().browse(booking_id)
#     if booking:
#         booking.sudo().write({
#             'status': 'completed',
#         })
#
#         booking.travel_id.kilo_qty -= int(booking.kilo_booked)
#         # print(" booking.travel_id.kilo_qty", booking.travel_id.kilo_qty, "int(booking.kilo_booked)")
#         return {'status': 200, 'message': 'completed'}
#     else:
#         return 'Request Failed'
