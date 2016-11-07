from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import ReportForm
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect, QueryDict


# Create your views here.

def register_success(request):
    return render(request,'fileshare/register_success.html')

def profile(request):
	return

@login_required(login_url='login')
def main(request):

	if request.method == 'POST':
		report_form = ReportForm(request.POST)

		if report_form.is_valid():
			report = report_form.save(commit=False)
			report.owned_by = request.user
			#report.group = None
			report.save()
			return redirect('main')
	else:
		report_form = ReportForm()
	
	return render(request, 'fileshare/main.html', {'report_form': report_form})
