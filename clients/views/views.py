# Python
import os
import io
from cgi import escape

# Django
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.template.loader import get_template
from django.template import Context
from django.contrib import messages

# xhtml2pdf
import xhtml2pdf.pisa as pisa

# PerfectArchOrthotics
from search import get_query
from clients.models import Client, Dependent, Claim, Insurance, CoverageType, \
    Person, Item, ClaimItem
from clients.forms.forms import ClientForm, DependentForm, InsuranceForm, \
    CoverageForm, ClaimForm


#TODO: split into multiple views

# Convert HTML URIs to absolute system paths
#  so xhtml2pdf can access those resources
def link_callback(uri, rel):
    # use short variable names
    sUrl = settings.STATIC_URL    # Typically /static/
    sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL     # Typically /static/media/
    mRoot = settings.MEDIA_ROOT   # Typically /home/userX/project_static/media/

    # convert URIs to absolute system paths
    path = ""
    path2 = ""
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
        # Also check other static dirs, for devl
        path2 = path.replace("static", "assets")

    # make sure that file exists
    if os.path.isfile(path):
        return path
    elif os.path.isfile(path2):
        return os.path.normpath(path2)
    else:
        raise Exception('media URI must start with %s or %s' %
                        (sUrl, mUrl))


@login_required
def render_to_pdf(request, template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)
    result = io.BytesIO()

    # 'utf-8' didn't work
    # pdf = pisa.pisaDocument(io.BytesIO("Test".encode("ISO-8859-1")),
    #                         result,
    #                         link_callback=link_callback
    #                         )
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")),
                            result,
                            link_callback=link_callback
                            )
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))

    #file = open(os.join(settings.MEDIA_ROOT, 'test.pdf'), "w+b")
    #pisaStatus = pisa.CreatePDF(html, dest=file, link_callback=link_callback)


def invoice_view(request, client_id, claim_id):
    claim, client, invoice, invoice_number = _invoice(
        client_id, claim_id)
    bill_to = settings.BILL_TO[0][1]
    perfect_arch_name = bill_to.split('\n')[0]
    perfect_arch_address = bill_to.replace(perfect_arch_name + '\n', '')

    return render_to_pdf(request,
                         'clients/pdfs/invoice.html',
                         {'pagesize': 'A4',
                          'claim': claim,
                          'client': client,
                          'invoice': invoice,
                          'invoice_number': invoice_number,
                          'perfect_arch_name': perfect_arch_name,
                          'perfect_arch_address': perfect_arch_address,
                          'item_class': Item,
                          'claim_item_class': ClaimItem,
                          'insurance_class': Insurance,
                          'business_number': settings.BUSINESS_NUMBER}
                         )


def _invoice(client_id, claim_id):
    claim = Claim.objects.get(id=claim_id)
    client = claim.client
    invoice = None
    try:
        invoice = claim.invoice_set.all()[0]
    except:
        pass
    invoice_number = "{0:04d}".format(claim.id)

    return claim, client, invoice, invoice_number


def insurance_letter_view(request, client_id, claim_id):
    claim, client, insurance_letter = _insurance_letter(client_id,
                                                        claim_id)

    # Because !@#$ xhtml2pdf (putting these in css classes didnt work)
    underline = (
        'border-bottom: 1pt solid #000000;'
        ' width: 25px;'
        ' text-align: center;'
        ' line-height: 5px;'
        ' font-family: monospace;'
    )
    notunderline = (
        'text-align: left;'
        ' line-height: 5px;'
    )

    return render_to_pdf(request,
                         'clients/pdfs/insurance_letter.html',
                         {'pagesize': 'A4',
                          'claim': claim,
                          'client': client,
                          'insurance_letter': insurance_letter,
                          'underline': underline,
                          'notunderline': notunderline})


def _insurance_letter(client_id, claim_id):
    claim = Claim.objects.get(id=claim_id)
    client = claim.client
    insurance_letter = None
    try:
        insurance_letter = claim.insuranceletter_set.all()[0]
    except:
        pass

    return claim, client, insurance_letter


def proof_of_manufacturing_view(request, client_id, claim_id):
    claim, proof_of_manufacturing, invoice_number = _proof_of_manufacturing(
        claim_id)

    return render_to_pdf(request,
                         'clients/pdfs/proof_of_manufacturing.html',
                         {'pagesize': 'A4',
                          'claim': claim,
                          'proof_of_manufacturing': proof_of_manufacturing,
                          'invoice_number': invoice_number})


def _proof_of_manufacturing(claim_id):
    claim = Claim.objects.get(id=claim_id)
    proof_of_manufacturing = None
    try:
        proof_of_manufacturing = claim.proofofmanufacturing_set.all()[0]
    except:
        pass
    invoice_number = "{0:04d}".format(claim.id)

    return claim, proof_of_manufacturing, invoice_number


@login_required
def fillOutInvoiceView(request, client_id, claim_id):
    context = RequestContext(request)

    claim, client, invoice, invoice_number = _invoice(
        client_id, claim_id)

    return render_to_response('clients/make_invoice.html',
                              {'client': client,
                               'claim': claim,
                               'invoice': invoice,
                               'insurance_class': Insurance,
                               'business_number': settings.BUSINESS_NUMBER,
                               'invoice_number': invoice_number},
                              context)


@login_required
def fillOutInsuranceLetterView(request, client_id, claim_id):
    context = RequestContext(request)

    claim, client, insurance_letter = _insurance_letter(client_id,
                                                        claim_id)

    return render_to_response('clients/make_insurance_letter.html',
                              {'client': client,
                               'claim': claim,
                               'insurance_letter': insurance_letter},
                              context)


@login_required
def fillOutProofOfManufacturingView(request, client_id, claim_id):
    context = RequestContext(request)

    client = Client.objects.get(id=client_id)
    claim, proof_of_manufacturing, invoice_number = _proof_of_manufacturing(
        claim_id)

    return render_to_response(
        'clients/make_proof_of_manufacturing.html',
        {'client': client,
         'claim': claim,
         'proof_of_manufacturing': proof_of_manufacturing,
         'invoice_number': invoice_number},
        context)


@login_required
def clients(request):
    context = RequestContext(request)

    client_list = Client.objects.order_by('-id')
    paginator = Paginator(client_list, 5)
    page = request.GET.get('page')
    try:
        clients = paginator.page(page)
    except PageNotAnInteger:
        clients = paginator.page(1)
    except EmptyPage:
        clients = paginator.page(paginator.num_pages)

    client_dict = {'clients': clients}

    return render_to_response('clients/clients.html', client_dict, context)


@login_required
def claimsView(request):
    context = RequestContext(request)

    # TODO: Change this order_by to be on time
    claim_list = Claim.objects.order_by('-id')
    paginator = Paginator(claim_list, 5)
    page = request.GET.get('page')
    try:
        claims = paginator.page(page)
    except PageNotAnInteger:
        claims = paginator.page(1)
    except EmptyPage:
        claims = paginator.page(paginator.num_pages)

    context_dict = {'claims': claims}
    return render_to_response('clients/claims.html', context_dict, context)


@login_required
def claimView(request, client_id, claim_id):
    context = RequestContext(request)

    client = Client.objects.get(id=client_id)
    claim = Claim.objects.get(id=claim_id)
    has_orthotics = claim.coverage_types.filter(coverage_type="o").count() > 0
    context_dict = {'claim': claim, 'client': client,
                    'has_orthotics': has_orthotics}
    return render_to_response('clients/claim.html', context_dict, context)


@login_required
def insuranceView(request):
    context = RequestContext(request)

    insurance_list = Insurance.objects.all()
    paginator = Paginator(insurance_list, 5)
    page = request.GET.get('page')
    try:
        insurances = paginator.page(page)
    except PageNotAnInteger:
        insurances = paginator.page(1)
    except EmptyPage:
        insurances = paginator.page(paginator.num_pages)

    context_dict = {'insurances': insurances}
    return render_to_response('clients/insurances.html', context_dict, context)


@login_required
def clientSearchView(request):
    context = RequestContext(request)
    context_dict = {}
    query_string = request.GET['q']
    fields = ['first_name', 'last_name', 'address', 'phone_number', 'employer',
              'health_care_number']
    clients = None
    if ('q' in request.GET) and request.GET['q'].strip():
        page = request.GET.get('page')
        query_string = request.GET['q']
        context_dict['q'] = query_string
        client_query = get_query(query_string, fields)
        found_clients = Client.objects.filter(client_query)
        paginator = Paginator(found_clients, 5)
        try:
            clients = paginator.page(page)
        except PageNotAnInteger:
            clients = paginator.page(1)
        except EmptyPage:
            clients = paginator.page(paginator.num_pages)
        context_dict['clients'] = clients

    return render_to_response('clients/clients.html',
                              context_dict,
                              context)


@login_required
def claimSearchView(request):
    context = RequestContext(request)
    context_dict = {}
    query_string = request.GET['q']
    fields = ['client__first_name', 'client__last_name', 'client__employer']
    claims = None
    if ('q' in request.GET) and request.GET['q'].strip():
        page = request.GET.get('page')
        query_string = request.GET['q']
        context_dict['q'] = query_string
        claim_query = get_query(query_string, fields)
        found_claims = Claim.objects.filter(claim_query)
        paginator = Paginator(found_claims, 5)
        try:
            claims = paginator.page(page)
        except PageNotAnInteger:
            claims = paginator.page(1)
        except EmptyPage:
            claims = paginator.page(paginator.num_pages)
        context_dict['claims'] = claims

    return render_to_response('clients/claims.html',
                              context_dict,
                              context)


@login_required
def insuranceSearchView(request):
    context = RequestContext(request)
    context_dict = {}
    query_string = request.GET['q']
    fields = ["client__employer", "provider", "policy_number",
              "client__first_name", "client__last_name"]
    insurances = None
    if ('q' in request.GET) and request.GET['q'].strip():
        page = request.GET.get('page')
        query_string = request.GET['q']
        context_dict['q'] = query_string
        insurance_query = get_query(query_string, fields)
        found_insurances = Insurance.objects.filter(insurance_query)
        paginator = Paginator(found_insurances, 5)
        try:
            insurances = paginator.page(page)
        except PageNotAnInteger:
            insurances = paginator.page(1)
        except EmptyPage:
            insurances = paginator.page(paginator.num_pages)
        context_dict['insurances'] = insurances

    return render_to_response('clients/insurances.html',
                              context_dict,
                              context)


def getFieldsFromRequest(request, default=""):
    """This is not used currently, will maybe be used in the future."""
    if 'fields' in request.GET and request.GET['fields'].strip():
        querydict = dict(request.GET.iterlists())
        return querydict['fields']
    else:
        return [default]


@login_required
def clientView(request, client_id):
    context = RequestContext(request)

    client = Client.objects.get(id=client_id)
    insurance = client.insurance_set.all()
    dependents = client.dependent_set.all()
    claims = client.claim_set.all()
    spouse = None
    children = []
    for dependent in dependents:
        if dependent.relationship == Dependent.SPOUSE:
            spouse = dependent
        else:
            children.append(dependent)

    context_dict = {'client': client,
                    'client_insurance': insurance,
                    'client_claims': claims,
                    'spouse': spouse,
                    'children': children,
                    'dependent_class': Dependent}
    return render_to_response('clients/client.html', context_dict, context)


@login_required
def add_client(request):
    context = RequestContext(request)

    if request.method == 'POST':
        form = ClientForm(request.POST)

        if form.is_valid():
            saved = form.save(commit=True)

            form = DependentForm()
            return redirect('add_dependent', saved.id)
            #return render_to_response('clients/add_dependent.html',
                                       # {'form': form}, context)
    else:
        form = ClientForm()

    return render_to_response('clients/add_client.html',
                              {'form': form}, context)


@login_required
def editClientView(request, client_id):
    context = RequestContext(request)

    client = Client.objects.get(id=client_id)
    if request.method == 'POST':
        client_form = ClientForm(request.POST, instance=client)
        if client_form.is_valid():
            saved = client_form.save(commit=True)
            return redirect('client', saved.id)

    else:
        client_form = ClientForm(instance=client)

    return render_to_response('clients/edit_client.html',
                              {'client': client,
                               'client_form': client_form},
                              context)


@login_required
def makeClaimView(request, client_id):
    context = RequestContext(request)

    client = Client.objects.get(id=client_id)
    insurances = client.insurance_set.all()
    claim_form = ClaimForm()
    items = {}
    for coverage_type in CoverageType.COVERAGE_TYPES:
        items[coverage_type[0]] = Item.objects.filter(
            coverage_type=coverage_type[0]).order_by('gender', 'product_code')
    # SUPER GROSS, MOVE TO FORM!
    if request.method == 'POST':
        # the check for if the right coverage and amount are selected
        claim_form = ClaimForm(request.POST)
        if claim_form.is_valid():
            valid = True
            querydict = request.POST
            if 'patient' not in querydict:
                valid = False
                messages.add_message(
                    request, messages.ERROR,
                    "Please select a Patient.")
            if 'insurance' not in querydict:
                valid = False
                messages.add_message(
                    request, messages.ERROR,
                    "Please select an Insurance.")
            if 'coverageSelected' not in querydict:
                valid = False
                messages.add_message(
                    request, messages.ERROR,
                    "Please select at least one Coverage Type.")

            claim = claim_form.save(commit=False)
            coverage_types = []
            claim_items = []
            if valid:
                amount_claimed_total = 0
                estimated_expected_back_total = 0
                for coverage_id in querydict.getlist('coverageSelected'):
                    coverage_type = CoverageType.objects.get(
                        id=coverage_id)
                    coverage_types.append(coverage_type)
                    item_selected = ('item_selected_'
                                     + coverage_type.coverage_type)
                    if item_selected not in querydict:
                        valid = False
                        messages.add_message(
                            request, messages.ERROR,
                            "Please select at least one Item for "
                            + coverage_type.get_coverage_type_display() + ".")
                        continue
                    item_list = querydict.getlist(item_selected)
                    for item_id in item_list:
                        quantity = float(querydict['pairs_%s' % item_id])
                        new_item = Item.objects.get(id=item_id)
                        claim_items.append(ClaimItem(item=new_item,
                                                     quantity=quantity))
                        amount = float(querydict['amount_%s' % item_id])
                        amount_total = amount * quantity
                        coverage_remaining = coverage_type.coverage_remaining()
                        if quantity > coverage_type.quantity:
                            valid = False
                            messages.add_message(
                                request, messages.ERROR,
                                "Product Code: "
                                + querydict['product_code_%s' % item_id]
                                + " Quantity is more than "
                                + coverage_type.get_coverage_type_display()
                                + " Pair Remaining.")
                        elif amount_total > coverage_remaining:
                            valid = False
                            messages.add_message(
                                request, messages.ERROR,
                                "Product Code: "
                                + querydict['product_code_%s' % item_id]
                                + " Claim Amount * Quantity is more than "
                                + coverage_type.get_coverage_type_display()
                                + " Coverage Remaining")
                        else:
                            coverage_type.quantity -= quantity
                            coverage_type.total_claimed += amount_total

                            coverage_percent = coverage_type.coverage_percent
                            amount_claimed_total += amount_total
                            estimated_expected_back_total += float(
                                amount_total * (float(coverage_percent)
                                                / 100))
                claim.amount_claimed = amount_claimed_total
                claim.estimated_expected_back = estimated_expected_back_total

            if valid:
                claim.client = client
                patient = Person.objects.get(id=querydict['patient'])
                claim.patient = patient
                insurance = Insurance.objects.get(id=querydict['insurance'])
                claim.insurance = insurance

                claim.save()

                for coverage_type in coverage_types:
                    coverage_type.save()
                    claim.coverage_types.add(coverage_type)
                for claim_item in claim_items:
                    claim_item.claim = claim
                    claim_item.save()

                return redirect('claim', client.id, claim.id)

    return render_to_response('clients/make_claim.html',
                              {'client': client,
                               'insurances': insurances,
                               'claim_form': claim_form,
                               'items': items,
                               },
                              context)


@login_required
def editDependentsView(request, client_id, dependent_id):
    context = RequestContext(request)

    client = Client.objects.get(id=client_id)
    dependent = client.dependent_set.get(id=dependent_id)
    if request.method == 'POST':
        dependent_form = DependentForm(request.POST, instance=dependent)
        if dependent_form.is_valid():
            saved = dependent_form.save(commit=False)
            saved.client = client
            saved.save()
            return redirect('client', client_id)

    else:
        dependent_form = DependentForm(instance=dependent)

    return render_to_response('clients/dependent/edit_dependent.html',
                              {'client': client,
                               'dependent_form': dependent_form},
                              context)


@login_required
def add_new_dependent(request, client_id):
    context = RequestContext(request)

    client = Client.objects.get(id=client_id)
    if request.method == 'POST':
        form = DependentForm(request.POST)

        if form.is_valid():
            saved = form.save(commit=False)

            client = Client.objects.get(id=client_id)
            saved.client = client
            saved.save()
            return redirect('client', client_id)
    else:
        form = DependentForm()

    return render_to_response('clients/dependent/add_new_dependent.html',
                              {'form': form,
                               'client': client},
                              context)


@login_required
def deleteDependentsView(request, client_id, dependent_id):
    # context = RequestContext(request)

    client = Client.objects.get(id=client_id)
    dependent = client.dependent_set.get(id=dependent_id)
    dependent.delete()
    return redirect('client', client_id)


@login_required
def add_dependent(request, client_id):
    context = RequestContext(request)

    if request.method == 'POST':
        if request.POST['submit'] == "Skip step":
            return redirect('add_insurance', client_id)

        form = DependentForm(request.POST)

        if form.is_valid():
            saved = form.save(commit=False)

            client = Client.objects.get(id=client_id)
            saved.client = client
            saved.save()

            if request.POST['submit'] == "Create and proceed":
                # This means we want to add insurance
                return redirect('add_insurance', client_id)
            else:
                # This means we want to add another
                form = DependentForm()
    else:
        # TODO need to create a formset here isntead of a form
        form = DependentForm()

    return render_to_response('clients/dependent/add_dependent.html',
                              {'form': form}, context)


@login_required
def add_insurance(request, client_id):
    context = RequestContext(request)

    if request.method == 'POST':
        insurance_form = InsuranceForm(request.POST, prefix="insurance_form")
        coverage_form1 = CoverageForm(
            request.POST, prefix="coverage_form1")
        coverage_form2 = CoverageForm(
            request.POST, prefix="coverage_form2")
        coverage_form3 = CoverageForm(
            request.POST, prefix="coverage_form3")

        if (insurance_form.is_valid()
                and coverage_form1.is_valid()
                and coverage_form2.is_valid()
                and coverage_form3.is_valid()):
            saved = insurance_form.save(commit=False)
            client = Client.objects.get(id=client_id)
            saved.client = client
            saved.save()

            coverage_1 = coverage_form1.save(commit=False)
            if coverage_1.coverage_percent == 0:
                pass
            else:
                coverage_1.insurance = saved
                coverage_1.total_claimed = 0
                coverage_1.save()

            coverage_2 = coverage_form2.save(commit=False)
            if coverage_2.coverage_percent == 0:
                pass
            else:
                coverage_2.insurance = saved
                coverage_2.total_claimed = 0
                coverage_2.save()

            coverage_3 = coverage_form3.save(commit=False)
            if coverage_3.coverage_percent == 0:
                pass
            else:
                coverage_3.insurance = saved
                coverage_3.total_claimed = 0
                coverage_3.save()

            return redirect('clients')
    else:
        insurance_form = InsuranceForm(prefix="insurance_form")
        coverage_form1 = CoverageForm(
            prefix="coverage_form1")
        coverage_form2 = CoverageForm(
            prefix="coverage_form2")

        coverage_form3 = CoverageForm(
            prefix="coverage_form3")

    return render_to_response('clients/add_insurance.html',
                              {'insurance_form': insurance_form,
                               'coverage_form1': coverage_form1,
                               'coverage_form2': coverage_form2,
                               'coverage_form3': coverage_form3},
                              context)
