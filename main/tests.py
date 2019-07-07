from django.test import TestCase
from django.urls import reverse
from django.core.management import call_command
from django import forms


class TownApiTestCase(TestCase):
    def setUp(self):
        # TODO: create towns ourselves to have more visiblity on their data
        call_command('import_towns_data', 'data/towns_tests.tsv')

    def call(self, url, method, status_code=200, *args, **kwargs):
        response = getattr(self.client, method.lower())(url, *args, **kwargs)
        self.assertEqual(response.status_code, status_code)

        if 'application/json' in response._headers['content-type'][1]:
            return response.json()

        return response

    def test_list_towns(self):
        url = reverse('main:towns-list')

        # check that response is paginated
        response = self.call(url, 'GET')
        self.assertEqual(len(response['results']), 100)
        self.assertTrue(response['next'])

        response = self.call(url + '?ordering=population', 'GET')
        self.assertEqual(response['results'][0]['population'], 23)

        response = self.call(url + '?min_population=50&ordering=population', 'GET')
        self.assertEqual(response['results'][0]['population'], 50)

        response = self.call(url + '?max_population=50&ordering=-population', 'GET')
        self.assertEqual(response['results'][0]['population'], 50)

        # test invalid inputs
        with self.assertRaises(forms.ValidationError):
            self.call(url + '?min_population=foo', 'GET', 400)
            self.call(url + '?max_population=foo', 'GET', 400)
