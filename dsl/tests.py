from django.test import TestCase

from dsl.parser import translate_query, DslError


class DslTestCase(TestCase):
    def test_valid_input(self):
        d1 = {
            'fields': ['name', 'population']
        }
        d2 = {
            'fields': ['name'],
            'filters': {'field': 'dept_code', 'value': 1}
        }
        d3 = {
            'fields': ['name'],
            'filters': {'field': 'population', 'value': 1000, 'predicate': 'gt'}
        }
        d4 = {
            'fields': ['name'],
            'filters': {'and': [
                {'field': 'population', 'value': 10000, 'predicate': 'gt'},
                {'field': 'region_name', 'value': 'Hauts-de', 'predicate': 'contains'}
            ]}
        }
        for d in (d1, d2, d3, d4):
            print(translate_query(d))

    def test_invalid_input(self):
        for d in [
            {'foo': 1},  # invalid json
            {'fields': [], 'filters': {'field': 'foo', 'value': 1}},  # invalid field
            {'fields': [], 'filters': {'field': 'population', 'value': 'foo'}},  # invalid value
        ]:
            with self.assertRaises(DslError):
                translate_query(d)
