# accounts/views.py
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
# from django.views import View
from .forms import CustomUserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from .models import CustomUser
from devicedata.models import Company

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = "registration/signup.html"

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/devicedata/dashboard')
            # if hasattr(user, 'company'):
            #     return redirect('/milldata/dashboard')
            # else:
            #     return redirect('blog')
        else:
            return redirect('signup')
    else:
        form = AuthenticationForm()
        return render(request, 'registration/login.html', {'form': form})
        
@login_required
def dashboard_view(request):
    company = request.user.company
    context = {'company': company}
    return render(request, 'dashboard.html', context)

class Login_View(TemplateView):
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_id = self.kwargs.get('company_id')  # use .get() method to avoid KeyError
        company = Company.objects.get(id=company_id)
        context['company'] = company
        return context


    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            companies = Company.objects.filter(owner=request.user)
            if companies.count() >= 1:
                return redirect(reverse('dashboard', kwargs={'pk': request.user.pk}))
            else:
                return redirect(reverse('blog'))
        else:
            form = AuthenticationForm()
            return render(request, 'registration/login.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = CustomUser.objects.get(username=form.cleaned_data['username'])
            login(request, user)
            companies = Company.objects.filter(owner=user)
            if companies.count() >= 1:
                return redirect(reverse('dashboard', kwargs={'pk': user.pk}))
            else:
                return redirect(reverse('home'))
        else:
            return render(request, 'registration/login.html', {'form': form})