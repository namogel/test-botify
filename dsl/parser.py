import json


class DslError(Exception):
    pass


with open('dsl/schema.json') as fd:
    SPEC_TYPES = {d['name']: d['type'] for d in json.load(fd)}


OPERATORS = {
    'equal': '=',
    'gt': '>',
    'gte': '>=',
    'lt': '<',
    'lte': '<=',
    'contains': 'LIKE',
}


def validate_query(data):
    # TODO; validate query against json schema
    try:
        fields = data['fields']
    except (Exception, KeyError):
        raise DslError('Invalid json')

    filters = data.get('filters')
    if filters:
        if 'or' in filters:
            [validate_filter(**f) for f in filters['or']]
        elif 'and' in filters:
            [validate_filter(**f)for f in filters['and']]
        else:
            validate_filter(**filters)

    return fields, filters


def validate_filter(field, value, predicate=None):
    try:
        spec_type = SPEC_TYPES[field]
    except KeyError:
        raise DslError(
            '{} is not a valid field, it must be one of {}'
            .format(field, ', '.join(SPEC_TYPES.keys()))
        )

    input_type = type(value)
    expected_type = {'int': int, 'float': float, 'str': str}[spec_type]
    if input_type != expected_type:
        raise DslError(
            '{}: invalid type, expected {}, received {}'
            .format(field, expected_type, input_type)
        )

    if predicate is not None and predicate not in OPERATORS:
        raise DslError(
            '{} is not valid, it must be one of {}'
            .format(predicate, ', '.join(OPERATORS.keys()))
        )


def parse_filters(filters):
    if 'and'in filters or 'or' in filters:
        if 'and' in filters:
            operator = 'AND'
            sub_filters = filters['and']
        elif 'or' in filters:
            operator = 'OR'
            sub_filters = filters['or']

        compound = '\n\t{} '.format(operator).join(parse_filter(**f) for f in sub_filters)

        return '(\n\t{}\n)'.format(compound)

    return parse_filter(**filters)


def parse_filter(field, value, predicate='equal'):
    operator = OPERATORS[predicate]

    if predicate == 'contains':
        value = '%{}%'.format(value)

    return '{field} {operator} {value}'.format(
        field=field,
        operator=operator,
        value=value,
    )


def translate_query(query):
    fields, filters = validate_query(query)

    sql_query = 'SELECT {}\nFROM main_towns'.format(', '.join(fields))
    if filters:
        sql_query += '\nWHERE {}'.format(parse_filters(filters))

    return sql_query
