import json
from odoo import http
from odoo.http import request
import base64


class PublicityController(http.Controller):

    @http.route('/all/publicity/hubkilo', type='http', auth='public', csrf=False, website=True, methods=['GET'],
                cors='*')
    def get_publicity_json(self, **kwargs):
        publicity_records = request.env['m2st_hk_airshipping.publicity'].sudo().search([])
        publicity_list = []

        if publicity_records:
            for publicity in publicity_records:
                publicity_dict = {
                    'id': publicity.id,
                    'image': publicity.image.decode('utf-8'),
                    'text': publicity.text,
                }
                publicity_list.append(publicity_dict)
                pub = publicity_list
            return json.dumps({'status': 200, 'publicity': pub, 'message': 'success'})
        else:
            return 'Empty!'

        # json_data = json.dumps(publicity_list, indent=4)
        # headers = [('Content-Type', 'application/json')]
        # return http.Response(json_data, headers=headers)
