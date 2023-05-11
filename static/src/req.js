////     function post() {
////    axios.get('/all/air/travels', {
////  headers: {
////  }
////}).then(response => {
////   console.log(response);
////    })
////    .catch(function(error) {
////        console.log(error);
////    });
////    }
//
//
//
////        function us1() {
////    axios.post('/web/session/authenticate', {
////    params: {
////        db: 'odoo15',
////        login: 'tembanblaise12@gmail.com',
////        password: 'odoo15',
////    },
////})
////.then(response => {
////    // Store the session ID in a cookie
////    document.cookie = `session_id=${response.data.session_id}; Secure; SameSite=Strict`;
////    console.log("cookie", ${response.data.session_id}; Secure; SameSite=Strict`);
////    })
////.catch(error => {
////    // Handle the error
////});
////    };
//
//
//
//
//
//
//
//    @http.route('/api/travel/create', type='json', auth='user', website=True, csrf=False, methods=['POST'])
//    def file_upload_submit(self, **kwargs):
//        check_cni = request.env['m2st_hk_airshipping.airshipping_file_upload'].search(
//            [('partner_id', '=', http.request.env.user.partner_id.id), ('cni_name', '!=', '')])
//        print(check_cni)
//        values = {
//            'partner_id': http.request.env.user.partner_id.id,
//            'cni_doc': kwargs['cni_doc'].read(),
//            'cni_name': kwargs['cni_doc'].filename,
//            'ticket_doc': kwargs['ticket_doc'].read(),
//            'ticket_name': kwargs['ticket_doc'].filename,
//        }
//        travel = {
//            'user_partner_id': http.request.env.user.partner_id.id,
//            'travel_type': kwargs.get('travel_type'),
//            'departure_town': kwargs.get('departure_town'),
//            'arrival_town': kwargs.get('arrival_town'),
//            'departure_date': fields.Date.to_date(kwargs.get('departure_date')),
//            'arrival_date': fields.Date.to_date(kwargs.get('arrival_date')),
//            'kilo_qty': kwargs.get('kilo_qty'),
//            'price_per_kilo': kwargs.get('price_per_kilo'),
//            'type_of_luggage_accepted': kwargs.get('type_of_luggage_accepted'),
//        }
//        values1 = {
//            'partner_id': http.request.env.user.partner_id.id,
//            'ticket_doc': kwargs['ticket_doc'].read(),
//            'ticket_name': kwargs['ticket_doc'].filename,
//        }
//        if check_cni:
//            request.env['m2st_hk_airshipping.airshipping_file_upload'].sudo().create(values1)
//            travel = request.env['m2st_hk_airshipping.airshipping'].sudo().create(travel)
//        else:
//            request.env['m2st_hk_airshipping.airshipping_file_upload'].sudo().create(values)
//            travel = request.env['m2st_hk_airshipping.airshipping'].sudo().create(travel)
//
//        travel_data = {
//            'travel_type': travel.travel_type,
//            'departure_town': travel.departure_town,
//            'arrival_town': travel.arrival_town,
//            'validation': travel.Validation,
//            'departure_date': travel.departure_date.strftime('%Y-%m-%d'),
//            'arrival_date': travel.arrival_date.strftime('%Y-%m-%d'),
//            'kilo_qty': travel.kilo_qty,
//            'price_per_kilo': travel.price_per_kilo,
//            'type_of_luggage_accepted': travel.type_of_luggage_accepted,
//        }
//
//        return {'status': 'success',
//                'travel': travel_data}