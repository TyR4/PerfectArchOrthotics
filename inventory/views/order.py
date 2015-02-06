import collections

from django.http import HttpResponseRedirect
from django.views.generic import DetailView, ListView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages

from utils.search import get_query, get_date_query
from inventory.models import Order


class CreateOrderView(CreateView):
    template_name = 'utils/generics/create.html'
    model = Order
    fields = '__all__'

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        order_form = form_class(**self.get_form_kwargs())
        queryset = order_form.fields['claimant'].queryset
        queryset = queryset.extra(
            select={
                'lower_first_name': 'lower(first_name)'
                }).order_by('lower_first_name')
        order_form.fields['claimant'].queryset = queryset
        return order_form

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.object.shoe:
            client_credit = self.object.claimant.get_client().credit()
            shoe_credit_value = self.object.shoe.credit_value
            if shoe_credit_value > client_credit:
                messages.add_message(
                    self.request, messages.ERROR,
                    "Shoe's Credit Value (%s) is greater than "
                    "Client's Credit (%s)." % (shoe_credit_value,
                                               client_credit))
                return self.form_invalid(form)
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(CreateOrderView, self).get_context_data(**kwargs)
        context['model_name_plural'] = self.model._meta.verbose_name_plural
        context['model_name'] = self.model._meta.verbose_name
        context['indefinite_article'] = 'an'
        return context

    def get_success_url(self):
        self.success_url = self.object.get_absolute_url()
        return self.success_url


class ListOrderView(ListView):
    template_name = "utils/generics/list.html"
    model = Order
    paginate_by = 20

    def get_paginate_by(self, queryset):
        if self.request.session.get('rows_per_page', False):
            self.paginate_by = self.request.session['rows_per_page']
        if ('rows_per_page' in self.request.GET
                and self.request.GET['rows_per_page'].strip()):
            self.paginate_by = self.request.GET['rows_per_page']
            self.request.session['rows_per_page'] = self.paginate_by
        return self.paginate_by

    def get_context_data(self, **kwargs):
        context = super(ListOrderView, self).get_context_data(**kwargs)
        context['model_name_plural'] = self.model._meta.verbose_name_plural
        context['model_name'] = self.model._meta.verbose_name
        context['indefinite_article'] = 'an'
        context['rows_per_page'] = self.request.session.get(
            'rows_per_page', self.paginate_by)
        context['datesearch'] = True

        if ('q' in self.request.GET) and self.request.GET['q'].strip():
            query_string = self.request.GET['q']
            context['q'] = query_string
        if ('df' in self.request.GET) and self.request.GET['df'].strip():
            query_string = self.request.GET['df']
            context['df'] = query_string
        if ('dt' in self.request.GET) and self.request.GET['dt'].strip():
            query_string = self.request.GET['dt']
            context['dt'] = query_string

        Option = collections.namedtuple('Option', ['value',
                                                   'value_display',
                                                   'selected'])
        Select = collections.namedtuple('Select', ['label', 'options'])
        order_types = []
        for order_type in Order.ORDER_TYPES:
            if ("order_type" in self.request.GET
                    and self.request.GET["order_type"].strip()
                    and self.request.GET["order_type"] == order_type[0]):
                order_types.append(Option(order_type[0], order_type[1], True))
            else:
                order_types.append(Option(order_type[0], order_type[1], False))
        selects = collections.OrderedDict()
        selects.update({"order_type": Select("Order Type", order_types)})
        context['selects'] = selects

        return context

    def get_queryset(self):
        # Start from all, drilldown to q
        queryset = super(ListOrderView, self).get_queryset()

        if ('q' in self.request.GET) and self.request.GET['q'].strip():
            fields = ['claimant__first_name', 'claimant__last_name',
                      'description', 'where', 'shoe__name']
            query_string = self.request.GET['q']
            order_query = get_query(query_string, fields)
            if queryset:
                queryset = queryset.filter(order_query)
            else:
                queryset = Order.objects.filter(order_query)

        if ('order_type' in self.request.GET
                and self.request.GET['order_type'].strip()):
            fields = ['order_type']
            query_string = self.request.GET['order_type']
            order_query = get_query(query_string, fields, exact=True)
            if queryset:
                queryset = queryset.filter(order_query)
            else:
                queryset = Order.objects.filter(order_query)

        if (('df' in self.request.GET) and self.request.GET['df'].strip()
                and ('dt' in self.request.GET)
                and self.request.GET['dt'].strip()):
            date_fields = ['ordered_date', 'arrived_date', 'dispensed_date']
            query_date_from_string = self.request.GET['df']
            query_date_to_string = self.request.GET['dt']
            order_query = get_date_query(query_date_from_string,
                                         query_date_to_string, date_fields)
            if queryset:
                queryset = queryset.filter(order_query)
            else:
                queryset = Order.objects.filter(order_query)
        elif ('df' in self.request.GET) and self.request.GET['df'].strip():
            date_fields = ['ordered_date', 'arrived_date', 'dispensed_date']
            query_date_from_string = self.request.GET['df']
            order_query = get_date_query(query_date_from_string,
                                         None, date_fields)
            if queryset:
                queryset = queryset.filter(order_query)
            else:
                queryset = Order.objects.filter(order_query)
        elif ('dt' in self.request.GET) and self.request.GET['dt'].strip():
            date_fields = ['ordered_date', 'arrived_date', 'dispensed_date']
            query_date_to_string = self.request.GET['dt']
            order_query = get_date_query(None,
                                         query_date_to_string, date_fields)
            if queryset:
                queryset = queryset.filter(order_query)
            else:
                queryset = Order.objects.filter(order_query)

        return queryset.distinct()


class DetailOrderView(DetailView):
    template_name = "utils/generics/detail.html"
    model = Order

    def get_context_data(self, **kwargs):
        context = super(DetailOrderView, self).get_context_data(**kwargs)
        context['model_name'] = self.model._meta.verbose_name
        return context


class UpdateOrderView(UpdateView):
    template_name = 'utils/generics/update.html'
    model = Order
    fields = '__all__'

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        order_form = form_class(**self.get_form_kwargs())
        queryset = order_form.fields['claimant'].queryset
        queryset = queryset.extra(
            select={
                'lower_first_name': 'lower(first_name)'
                }).order_by('lower_first_name')
        order_form.fields['claimant'].queryset = queryset
        return order_form

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.object.shoe:
            client_credit = self.object.claimant.get_client().credit()
            shoe_credit_value = self.object.shoe.credit_value
            if shoe_credit_value > client_credit:
                messages.add_message(
                    self.request, messages.ERROR,
                    "Shoe's Credit Value (%s) is greater than "
                    "Client's Credit (%s)." % (shoe_credit_value,
                                               client_credit))
                return self.form_invalid(form)
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(UpdateOrderView, self).get_context_data(**kwargs)
        context['model_name_plural'] = self.model._meta.verbose_name_plural
        context['model_name'] = self.model._meta.verbose_name
        context['indefinite_article'] = 'an'
        return context

    def get_success_url(self):
        self.success_url = self.object.get_absolute_url()
        return self.success_url


class DeleteOrderView(DeleteView):
    template_name = 'utils/generics/delete.html'
    model = Order

    def get_context_data(self, **kwargs):
        context = super(DeleteOrderView, self).get_context_data(**kwargs)
        context['model_name'] = self.model._meta.verbose_name
        return context

    def get_success_url(self):
        self.success_url = reverse_lazy('order_list')
        return self.success_url