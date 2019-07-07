import locale

from django.core.management import BaseCommand

from main.models import Town


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('filename')

    def handle(self, *, filename, **options):
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

        i = 0
        towns = []
        with open(filename) as fd:
            for line in fd:
                i += 1
                if not i % 5000:
                    Town.objects.bulk_create(towns)
                    towns = []
                region_code, region_name, dept_code, distr_code, code, name,\
                    population, average_age = line.rstrip('\n').split('\t')
                towns += [Town(
                    region_code=region_code,
                    region_name=region_name,
                    dept_code=dept_code,
                    distr_code=distr_code,
                    code=code,
                    name=name.strip(),
                    population=locale.atoi(population),
                    average_age=average_age
                )]
        Town.objects.bulk_create(towns)
