from django import http
from django import template
from django import shortcuts
from django.views import generic
from django.conf import settings
from django.core import urlresolvers

from clients import models as clients_models
from clients.views import views as clients_views
from clients.forms import claim_forms


class BiomechanicalGaitCreate(generic.CreateView):
    model = clients_models.BiomechanicalGait
    template_name = 'clients/claim/biomechanical_gait.html'
    form_class = claim_forms.BiomechanicalGaitModelForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['save_text'] = 'create'
        context['model_name'] = self.model._meta.verbose_name
        context['cancel_url'] = urlresolvers.reverse(
            'claim', kwargs={'claim_id': self.kwargs['claim_pk']}
        )

        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.claim_id = self.kwargs['claim_pk']
        self.object.save()

        return http.HttpResponseRedirect(self.get_success_url())


class BiomechanicalGaitUpdate(generic.UpdateView):
    model = clients_models.BiomechanicalGait
    template_name = 'clients/claim/biomechanical_gait.html'
    form_class = claim_forms.BiomechanicalGaitModelForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['save_text'] = 'update'
        context['model_name'] = self.model._meta.verbose_name
        context['cancel_url'] = self.object.get_absolute_url()

        return context


def _biomechanical_gait(claim_pk):
    claim = clients_models.Claim.objects.select_related(
        'patient', 'biomechanicalgait'
    ).get(pk=claim_pk)
    try:
        biomechanical_gait = claim.biomechanicalgait
    except clients_models.BiomechanicalGait.DoesNotExist:
        biomechanical_gait = None

    return claim, biomechanical_gait


def biomechanical_gait_fill_out(request, claim_pk):
    context = template.RequestContext(request)

    claim, biomechanical_gait = _biomechanical_gait(claim_pk)

    return shortcuts.render_to_response(
        'clients/make_biomechanical_gait.html',
        {
            'claim': claim,
            'biomechanical_gait': biomechanical_gait,
        },
        context
    )


def biomechanical_gait_pdf(request, claim_pk):
    claim, biomechanical_gait = _biomechanical_gait(claim_pk)

    # return shortcuts.render(
    #     request,
    #     'clients/pdfs/biomechanical_gait.html',
    #     {
    #         'title': "Bio-mechanical/Gait Examination",
    #         'claim': claim,
    #         'biomechanical_gait': biomechanical_gait,
    #         'address': settings.BILL_TO[0][1],
    #         'email': settings.DANNY_EMAIL,
    #     }
    # )
    return clients_views.render_to_pdf(
        request,
        'clients/pdfs/biomechanical_gait.html',
        {
            'title': "Bio-mechanical/Gait Examination",
            'claim': claim,
            'biomechanical_gait': biomechanical_gait,
            'address': settings.BILL_TO[0][1],
            'email': settings.DANNY_EMAIL,
        }
    )
