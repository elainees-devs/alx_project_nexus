from django.shortcuts import render, redirect
from django.views import View
from .forms import SignupForm, LoginForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Signup view
class SignupView(View):
    def get(self, request):
        return render(request, 'template/signup.html', {'form': 'form'})

    def post(self, request):
        # Handle user signup logic
        form=SignupForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
        return render(request, 'template/signup.html', {'form': form})
       
        
# Login view
class LoginView(View):
    def get(self, request):
        form=LoginForm()
        return render(request, 'template/login.html', {'form': form})

    def post(self, request):
        # Handle user login logic
        form=LoginForm(request.POST)
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully.')
            return redirect('template/profile')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'template/login.html', {'form': form})

# Logout view

# Profile view

