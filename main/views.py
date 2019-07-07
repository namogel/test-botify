from rest_framework import viewsets, mixins, filters
from rest_framework.response import Response
import serpy
from django.db.models import Min, Max, Avg
from django import forms
from rest_framework.decorators import api_view

from main.models import Town
from dsl.parser import translate_query, DslError


def validate_form(request, form_class):
    form = form_class(data=request.GET)
    if not form.is_valid():
        raise forms.ValidationError(form.errors)

    return form.cleaned_data


class TownSerializer(serpy.Serializer):
    name = serpy.StrField()
    region_name = serpy.StrField()
    town_code = serpy.IntField(attr='code')
    department = serpy.StrField(attr='dept_code')
    population = serpy.IntField()


class TownQueryFilterForm(forms.Form):
    min_population = forms.IntegerField(required=False)
    max_population = forms.IntegerField(required=False)


class TownQueryFilter(object):
    def filter_by_min_population(self, queryset, min_population):
        return queryset.filter(population__gte=min_population)

    def filter_by_max_population(self, queryset, max_population):
        return queryset.filter(population__lte=max_population)

    def filter_queryset(self, request, queryset, *args, **kwargs):
        data = validate_form(request, TownQueryFilterForm)
        for key, value in data.items():
            if value is not None:
                queryset = getattr(self, 'filter_by_{}'.format(key))(queryset, value)

        return queryset


class TownViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Town.objects.all()
    serializer_class = TownSerializer
    filter_backends = (TownQueryFilter, filters.OrderingFilter)
    ordering_fields = ('population',)
    ordering = ('region_code', 'dept_code', 'code')


class AggregateForm(forms.Form):
    key = forms.ChoiceField(choices=(
        ('region_code', 'region_code'),
        ('dept_code', 'dept_code')
    ))


class AggregateViewSet(viewsets.GenericViewSet):
    queryset = Town.objects.all()

    def list(self, request, *args, **kwargs):
        data = validate_form(request, AggregateForm)
        key = data['key']

        data = self.queryset.values(key).annotate(
            min_pop=Min('population'),
            max_pop=Max('population'),
            avg_age=Avg('average_age')
        ).values(key, 'min_pop', 'max_pop', 'avg_age')

        return Response(list(data))


@api_view(['POST'])
def query(request, *args, **kwargs):
    try:
        res = translate_query(request.data['query'])
    except DslError as e:
        return Response({'detail': str(e)}, status=400)
    else:
        return Response(res)
