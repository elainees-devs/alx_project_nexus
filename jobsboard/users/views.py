from django.shortcuts import render, redirect
from django.views import View
from .forms import SignupForm, LoginForm, passwordResetRequestForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode,force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, method_decorator
from django.core.mail import send_mail

User = get_user_model()

# Signup view
class SignupView(View):
    def get(self, request):
        return render(request, 'templates/signup.html', {'form': 'form'})

    def post(self, request):
        # Handle user signup logic
        form=SignupForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
        return render(request, 'templates/signup.html', {'form': form})
       
        
# Login view
class LoginView(View):
    def get(self, request):
        form=LoginForm()
        return render(request, 'templates/login.html', {'form': form})

    def post(self, request):
        # Handle user login logic
        form=LoginForm(request.POST)
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully.')
            return redirect('templates/profile')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'templates/login.html', {'form': form})


# Logout view
class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Logged out successfully.')
        return redirect('templates/login')


# Password reset view
class PasswordResetView(View):
    def get(self, request):
        form=passwordResetRequestForm()
        return render(request, 'templates/password_reset.html', {'form': form})

    def post(self, request):
        form=passwordResetRequestForm(request.POST)
        if form.is_valid():
            # Handle password reset logic
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid= urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = request.build_absolute_uri(f"/reset/{uid}/{token}/")

            # Send a password reset email
                send_mail(
                   recipient_list=[email],
                   subject="Password Reset Request",
                   message=f"Click the link to reset your password: {reset_link}",
                   from_email="noreply@example.com")
                   
                messages.success(request, 'Password reset link sent to your email.')
            except User.DoesNotExist:
                messages.error(request, 'No user found with this email address.')

                return redirect('templates/login')


# Profile view
@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        return render(request, 'templates/profile.html', {'user': request.user})

