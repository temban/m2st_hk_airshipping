from odoo.tests.common import HttpCase
import json

class TestUserTravelList(HttpCase):
    def test_user_travel_list(self):
        # create a mock user partner
        user_partner = self.env['res.partner'].create({'name': 'Test User'})
        # create a mock travel record for the user
        travel = self.env['m2st_hk_airshipping.airshipping'].create({
            'user_partner_id': user_partner.id,
            'travel_type': 'by_air',
            'departure_town': 'London',
            'arrival_town': 'Paris',
            'Validation': True,
            'departure_date': '2022-01-01',
            'arrival_date': '2022-01-02',
            'kilo_qty': 20,
            'price_per_kilo': 10,
            'type_of_luggage_accepted': 'Suitcase'
        })
        # perform the controller request
        response = self.url_open(
            '/api/current/user/travels',
            headers={'Content-Type': 'application/json'},
            type='json',
            auth='user',
            user=user_partner.user_ids[0]
        )
        # check the response data
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), {'status': 200, 'response': [{
            'id': travel.id,
            'travel_type': travel.travel_type,
            'departure_town': travel.departure_town,
            'arrival_town': travel.arrival_town,
            'validation': travel.Validation,
            'departure_date': '2022-01-01',
            'arrival_date': '2022-01-02',
            'kilo_qty': 20,
            'price_per_kilo': 10,
            'type_of_luggage_accepted': 'Suitcase'
        }], 'message': 'success'})