from odoo import http, fields
from odoo.http import request
import json
import base64
from datetime import datetime, timedelta

from werkzeug.wrappers import Response


class TravelFiles(http.Controller):

    # Controller that uploads and update a travel documents
    @http.route('/air/travel/document/upload', type='http', auth='user', website=True, csrf=False, methods=['POST'],
                cors='*')
    def create_file_upload(self, **kwargs):

        check_doc = request.env['m2st_hk_airshipping.airshipping_file_upload'].sudo().search(
            [('travel_id', '=', int(kwargs.get('travel_id')))])
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
        print(kwargs.get('travel_id'))
        print(check_doc)
        if check_doc:
            return json.dumps({'Error': 'Travel documents already exist!'})
        else:
            # Read the file data and convert to base64
            new_file_upload = request.env['m2st_hk_airshipping.airshipping_file_upload'].sudo().create(values)
            return json.dumps({'status': 200, 'file_upload_id': new_file_upload.id, 'message': 'success'})
        # return json.dumps({'file_upload_id': new_file_upload.cni_doc.decode('utf-8')})

    @http.route('/air/update/travel/document/upload/<int:file_upload_id>', type='http', auth='user', website=True,
                csrf=False, methods=['POST'], cors='*')
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


class TravelCrud(http.Controller):
    # function that disable due travels
    def update_due_travels_disable(self):
        due_travels = http.request.env['m2st_hk_airshipping.airshipping'].sudo().search([])
        if due_travels:
            for due_travel in due_travels:
                current_date = datetime.now().date()
                if due_travel.departure_date and (due_travel.departure_date - timedelta(days=1)) <= current_date:
                    due_travel.disable = True
                    print("due_departure_date", (due_travel.departure_date - timedelta(days=1)), '<=', "previous_date",
                          current_date, 'sattus', due_travel.disable)
                else:
                    'still valid'

    # Controller that creates a new travel
    @http.route('/air/api/travel/create', type='json', auth='user', website=True, csrf=False, methods=['POST'],
                cors='*')
    def travel_create(self, **kwargs):
        travel = {
            'user_partner_id': http.request.env.user.partner_id.id,
            'departure_town': kwargs.get('departure_town').lower(),
            'arrival_town': kwargs.get('arrival_town').lower(),
            'departure_date': fields.Date.to_date(kwargs.get('departure_date')),
            'arrival_date': fields.Date.to_date(kwargs.get('arrival_date')),
            'kilo_qty': kwargs.get('kilo_qty'),
            'negotiation': kwargs.get('negotiation'),
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
                        'negotiation': travel_info.negotiation,
                        'price_per_kilo': travel_info.price_per_kilo,
                        'type_of_luggage_accepted': travel_info.type_of_luggage_accepted,
                    }}
        else:
            return "Request failed!"

    # Controller that gets all travels
    @http.route('/air/all/travels', type='http', auth='public', csrf=False, website=True, methods=['GET'], cors='*')
    def travels(self, **kwargs):
        self.update_due_travels_disable()
        travels = request.env['m2st_hk_airshipping.airshipping'].sudo().search(
            [('status', '=', 'accepted'), ('disable', '=', False)])
        travels_list = []
        if travels:
            for travel in travels:
                files_uploaded_id = travel.files_uploaded_id[0].id if travel.files_uploaded_id else None
                travels_dict = {
                    'id': travel.id,
                    'travel_type': travel.travel_type,
                    'departure_town': travel.departure_town,
                    'arrival_town': travel.arrival_town,
                    'status': travel.status,
                    'disable': travel.disable,
                    'negotiation': travel.negotiation,
                    'departure_date': travel.departure_date.strftime('%Y-%m-%d'),
                    'arrival_date': travel.arrival_date.strftime('%Y-%m-%d'),
                    'kilo_qty': travel.kilo_qty,
                    'price_per_kilo': travel.price_per_kilo,
                    'type_of_luggage_accepted': travel.type_of_luggage_accepted,
                    'files_uploaded_id': files_uploaded_id,
                    'user': {
                        'user_id': travel.user_partner_id.id,
                        'user_name': travel.user_partner_id.name,
                        'user_email': travel.user_partner_id.email,
                        'image_1920': travel.user_partner_id.image_1920.decode('utf-8') if travel.user_partner_id.image_1920 else None
                    }
                }
                travels_list.append(travels_dict)
                data = {'status': 200, 'response': travels_list, 'message': 'success'}
                print(data)
            return json.dumps(data)
        else:
            return 'Empty!'

    # Controller that search travels by source and destination
    @http.route('/air/search/travel', type='json', auth='public', csrf=False, website=True, methods=['POST'], cors='*')
    def travel_search(self, **kw):
        print(kw)
        departure_town = kw.get('departure_town').lower()
        arrival_town = kw.get('arrival_town').lower()
        travel_type = kw.get('travel_type')
        print(kw)
        airshippings = request.env['m2st_hk_airshipping.airshipping'].sudo().search(
            [('travel_type', '=', travel_type), ('departure_town', '=', departure_town),
             ('arrival_town', '=', arrival_town), ('status', '=', 'accepted'), ('disable', '=', False)])
        travels_search = []
        if airshippings:
            for travel in airshippings:
                files_uploaded_id = travel.files_uploaded_id[0].id if travel.files_uploaded_id else None
                travels_results = {
                    'id': travel.id,
                    'travel_type': travel.travel_type,
                    'departure_town': travel.departure_town,
                    'arrival_town': travel.arrival_town,
                    'status': travel.status,
                    'disable': travel.disable,
                    # 'negotiation': travel.negotiation,
                    'departure_date': travel.departure_date.strftime('%Y-%m-%d'),
                    'arrival_date': travel.arrival_date.strftime('%Y-%m-%d'),
                    'kilo_qty': travel.kilo_qty,
                    'price_per_kilo': travel.price_per_kilo,
                    'type_of_luggage_accepted': travel.type_of_luggage_accepted,
                    'files_uploaded_id': files_uploaded_id,
                    'user': {
                        'user_id': travel.user_partner_id.id,
                        'user_name': travel.user_partner_id.name,
                        'user_email': travel.user_partner_id.email,
                        'image_1920': travel.user_partner_id.image_1920.decode('utf-8') if travel.user_partner_id.image_1920 else None
                    }
                }
                travels_search.append(travels_results)
            result = {'status': 200, 'response': travels_search, 'message': 'success'}
            return result
        else:
            return 'Empty!'

    # controller that gets a travel by id
    @http.route('/air/travel/view/<int:travel_id>', type='http', auth='user', csrf=False, website=True, methods=['GET'],
                cors='*')
    def view_travel(self, travel_id, **kw):
        self.update_due_travels_disable()
        travel = request.env['m2st_hk_airshipping.airshipping'].sudo().browse(travel_id)
        if travel:
            files_uploaded_id = travel.files_uploaded_id[0].id if travel.files_uploaded_id else None
            travel_result = {
                'id': travel.id,
                'travel_type': travel.travel_type,
                'departure_town': travel.departure_town,
                'arrival_town': travel.arrival_town,
                'status': travel.status,
                'disable': travel.disable,
                'negotiation': travel.negotiation,
                'departure_date': travel.departure_date.strftime('%Y-%m-%d'),
                'arrival_date': travel.arrival_date.strftime('%Y-%m-%d'),
                'kilo_qty': travel.kilo_qty,
                'price_per_kilo': travel.price_per_kilo,
                'type_of_luggage_accepted': travel.type_of_luggage_accepted,
                'files_uploaded_id': files_uploaded_id,
                'user': {
                    'user_id': travel.user_partner_id.id,
                    'user_name': travel.user_partner_id.name,
                    'user_email': travel.user_partner_id.email,
                    'image_1920': travel.user_partner_id.image_1920.decode('utf-8') if travel.user_partner_id.image_1920 else None
                }
            }
            result = {'status': 200, 'response': travel_result, 'message': 'success'}
            return json.dumps(result)
        else:
            return 'Not found!'

    # Controller that get all current user travels by partner id
    @http.route('/air/api/current/user/travels', type='http', auth='user', csrf=False, website=True, methods=['GET'],
                cors='*')
    def current_user_travel_list(self, **kw):
        self.update_due_travels_disable()
        travels = request.env['m2st_hk_airshipping.airshipping'].sudo().search(
            [('user_partner_id', '=', http.request.env.user.partner_id.id), ('disable', '=', False)])
        user_travels_list = []

        if travels:
            for user_travel in travels:
                files_uploaded_id = user_travel.files_uploaded_id[0].id if user_travel.files_uploaded_id else None
                travels_dict = {
                    'id': user_travel.id,
                    'files_uploaded_id': files_uploaded_id,
                    'travel_type': user_travel.travel_type,
                    'departure_town': user_travel.departure_town,
                    'arrival_town': user_travel.arrival_town,
                    'status': user_travel.status,
                    'disable': user_travel.disable,
                    'negotiation': user_travel.negotiation,
                    'departure_date': user_travel.departure_date.strftime('%Y-%m-%d'),
                    'arrival_date': user_travel.arrival_date.strftime('%Y-%m-%d'),
                    'kilo_qty': user_travel.kilo_qty,
                    'price_per_kilo': user_travel.price_per_kilo,
                    'type_of_luggage_accepted': user_travel.type_of_luggage_accepted,
                }
                user_travels_list.append(travels_dict)

            data = {'status': 200, 'response': user_travels_list, 'message': 'success'}
            return json.dumps(data)
        else:
            return 'Empty'

    # Controller that get all current user travels by partner id
    @http.route('/air/api/user/all/travels/<int:partner_id>', type='http', auth='user', csrf=False, website=True,
                methods=['GET'], cors='*')
    def user_travel_list(self, partner_id, **kw):
        self.update_due_travels_disable()
        travels = request.env['m2st_hk_airshipping.airshipping'].sudo().search([('user_partner_id', '=', partner_id),('disable', '=', False)])
        user_travels_list = []
        if travels:
            for user_travel in travels:
                files_uploaded_id = user_travel.files_uploaded_id[0].id if user_travel.files_uploaded_id else None
                travels_dict = {
                    'id': user_travel.id,
                    'travel_type': user_travel.travel_type,
                    'departure_town': user_travel.departure_town,
                    'arrival_town': user_travel.arrival_town,
                    'status': user_travel.status,
                    'negotiation': user_travel.negotiation,
                    'departure_date': user_travel.departure_date.strftime('%Y-%m-%d'),
                    'arrival_date': user_travel.arrival_date.strftime('%Y-%m-%d'),
                    'kilo_qty': user_travel.kilo_qty,
                    'price_per_kilo': user_travel.price_per_kilo,
                    'type_of_luggage_accepted': user_travel.type_of_luggage_accepted,
                    'files_uploaded_id': files_uploaded_id,

                    'user': {
                        'user_id': user_travel.user_partner_id.id,
                        'user_name': user_travel.user_partner_id.name,
                        'user_email': user_travel.user_partner_id.email,
                        'image_1920': user_travel.user_partner_id.image_1920.decode('utf-8') if user_travel.user_partner_id.image_1920 else None
                    }
                }
                user_travels_list.append(travels_dict)
                data = {'status': 200, 'response': user_travels_list, 'message': 'success'}
                print(data)
            return json.dumps(data)
        else:
            return 'Empty!'

    # Controller that delete a travel
    @http.route('/air/api/travel/delete/<int:airshipping_id>', auth='user', csrf=False, website=True,
                methods=['DELETE'],
                cors='*')
    def delete_travel(self, airshipping_id, **kw):
        travel = request.env['m2st_hk_airshipping.airshipping'].sudo().browse(airshipping_id)
        if travel.status == 'accepted':
            error_response = {
                'success': False,
                'error_message': 'This travel has already been accepted!.'
            }
            return error_response
        if travel:
            print(travel)
            travel.sudo().write({
                'disable': True,
            })
            return json.dumps({'status': 200, 'message': 'deleted'})
        else:
            return 'Request Failed'

    # Controller that update a travel by id
    @http.route('/air/travel/update/<int:travel_id>', type='json', auth='user', methods=['PUT'], website=True,
                csrf=False)
    def update_travel(self, travel_id, **kwargs):
        travel = request.env['m2st_hk_airshipping.airshipping'].sudo().browse(travel_id)
        print(travel.user_partner_id.id)
        print(http.request.env.user.partner_id.id)
        if travel.status == 'accepted':
            error_response = {
                'success': False,
                'error_message': 'This travel has already been accepted!.'
            }
            return error_response
        if travel.disable:
            error_response = {
                'success': False,
                'error_message': 'This travel does not exist!.'
            }
            return error_response
        if travel.user_partner_id.id == http.request.env.user.partner_id.id:
            travel.write({
                'departure_town': kwargs.get('departure_town'),
                'arrival_town': kwargs.get('arrival_town'),
                'departure_date': fields.Date.to_date(kwargs.get('departure_date')),
                'arrival_date': fields.Date.to_date(kwargs.get('arrival_date')),
                'kilo_qty': kwargs.get('kilo_qty'),
                'price_per_kilo': kwargs.get('price_per_kilo'),
                'status': 'pending',
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



#
# +---------------------+                +--------------------+                 +---------------------+
# |     User Interface  |                |     Controller     |                 |      Data Access     |
# +---------------------+                +--------------------+                 +---------------------+
#           |                                        |                                         |
#           |       loadStudents(file)                |                                         |
#           |--------------------------------------->|                                         |
#           |                                        |                                         |
#           |                                 createStudent(studentData)                      |
#           |--------------------------------------->|                                         |
#           |                                        |             saveStudent(student)        |
#           |                                        |--------------------------------------->|
#           |                                        |                                         |
#           |       changeStatus(studentID, status)   |                                         |
#           |--------------------------------------->|                                         |
#           |                                        |              updateStudent(student)     |
#           |                                        |--------------------------------------->|
#           |                                        |                                         |
#           |                         notifySuccess() |                                         |
#           |<---------------------------------------|                                         |
#           |                                        |                                         |
#
#         +--------------+         +--------------+
#         |   Course     |         |   Teacher    |
#         +--------------+         +--------------+
#         | - courseID   |         | - teacherID  |
#         | - name       |         | - name       |
#         | - students   |         +--------------+
#         +--------------+
#              |      |
#              |      |         +-----------------+
#              |      +---------|   Student       |
#              |                +-----------------+
#              |                | - studentID     |
#              |                | - name          |
#              |                | - status        |
#              |                +-----------------+
#         +--------------+
#         |   File       |
#         +--------------+
#         | - fileID     |
#         | - name       |
#         | - path       |
#         +--------------+


# Class diagram:
#
#
# +------------------------+             +-------------+
# |       CourseService    |             | StudentService  |
# +------------------------+             +-------------+
# | +createCourse()        |             | +createStudent()|
# | +updateCourse()        |             | +updateStudent()|
# | +deleteCourse()        |             | +deleteStudent()|
# | +getCourseById()       |             | +getStudentById()|
# | +getAllCourses()       |             | +getAllStudents()|
# | +searchCourses()       |             | +searchStudents()|
# | +uploadExcelFile()     |             | +uploadExcelFile()|
# +------------------------+             +-------------+
#                 |                                      |
#                 |                                      |
#                 V                                      V
#        +---------------+                      +---------------+
#        |     Course    |                      |    Student    |
#        +---------------+                      +---------------+
#        | id:int        |                      |id:int         |
#        | name:String   |                      |name:String   |
#        | teacher:Teacher|                      |email:String  |
#        | students:int[] |                      |status:String |
#        +---------------+                      |course:Course |
#                                                +---------------+
#        +----------------+                   ~> +----------------+                 +------------------------+
#        |     Teacher    |                      |     Grade      |                 |   FinanceService        |
#        +----------------+                      +----------------+                 +------------------------+
#        | id:int         |                      | id:int         |                 | +importFinanceFile()    |
#        | name:String    |                      | grade:int      |                 | +exportFinanceFile()    |
#        | courses:int[]  |                      | student:Student|                 | +uploadExcelFile()      |
#        +----------------+                      +----------------+                 | +matchAndGenerateFile() |
#                                                 | course: Course |<~~~~~~~~~~~~~|    | +sendMailToPaidStudents()|
#                                                 +----------------+
#
#
#                                                 Sequence diagram:
#
  # +----------------+              +-----------------------+               +------------------+
  # |   User/Teacher |              |   System (JavaFX app) |               |     File System  |
  # +----------------+              +-----------------------+               +------------------+
  #        |                                    |                                     |
  #        |       Create Course                |                                     |
  #        |----------------------------------->|                                     |
  #        |                                    |                                     |
  #        |       Upload Course Excel          |                                     |
  #        |----------------------------------->|                                     |
  #        |                                    |                                     |
  #        |       Assign Teacher               |                                     |
  #        |----------------------------------->|                                     |
  #        |                                    |                                     |
  #        |       Perform CRUD/Search          |                                     |
  #        |       Operations on Courses        |                                     |
  #        |----------------------------------->|                                     |
  #        |                                    |                                     |
  #        |                                    |    Save Finance_Student_File        |
  #        |                                    |------------------------------------>|
  #        |                                    |                                     |
  #        |                                    |                                     |
  #        |       Load Student Excel            |                                     |
  #        |       Update Student Status         |                                     |
  #        |----------------------------------->|                                     |
  #        |                                    |                                     |
  #        |       Perform CRUD/Search          |                                     |
  #        |       Operations on Students        |                                     |
  #        |----------------------------------->|                                     |
  #        |                                    |                                     |
  #        |                                    |      Export Finance_Student_File    |
  #        |                                    |<------------------------------------|
  #        |                                    |                                     |
  #        |                                    |                                     |
  #        |                                    |      Import Finance_Student_File    |
  #        |                                    |----------------------------------->|
  #        |                                    |                                     |
  #        |                                    |      Import Student Results File    |
  #        |                                    |----------------------------------->|
  #        |                                    |                                     |
  #        |                                    |         Perform Matching            |
  #        |                                    |          and Grade Attribution      |
  #        |                                    |----------------------------------->|
  #        |                                    |                                     |
  #        |                                    |       Perform CRUD/Search           |
  #        |                                    |       Operations on Result File      |
  #        |                                    |----------------------------------->|
  #        |                                    |                                     |
  #        |                                    |       Export Result File            |
  #        |                                    |<------------------------------------|
  #        |                                    |                                     |
  #        |                                    |       Send Mail to Paid Students     |
  #        |                                    |----------------------------------->|
  #        |                                    |                                     |
  #        |                                    |                                     |
