from django.shortcuts import render, redirect
from django.views import View
from .forms import SignupForm, LoginForm, passwordResetRequestForm, setNewPasswordForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode,force_bytes, force_str
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
            
# New Password view
class SetNewPasswordView(View):
    def get(self, request, uidb64, token):
        form = setNewPasswordForm()
        return render(request, 'templates/set_new_password.html', {'form': form, 'uidb64': uidb64, 'token': token, 'validlink': True})

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            form = setNewPasswordForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data['new_password']
                confirm_password = form.cleaned_data['confirm_password']

                if password != confirm_password:
                    messages.error(request, 'Passwords do not match.')
                    return render(request, 'templates/set_new_password.html', {'form': form, 'uidb64': uidb64, 'token': token, 'validlink': True})

                user.set_password(password)
                user.save()
                messages.success(request, 'Password has been reset successfully. Please log in.')
                return redirect('templates/login') 

            # Form is invalid
            return render(request, 'templates/set_new_password.html', {'form': form, 'uidb64': uidb64, 'token': token, 'validlink': True})

        # Invalid token or user
        messages.error(request, 'Invalid or expired token.')
        return render(request, 'templates/set_new_password.html', {'form': setNewPasswordForm(), 'validlink': False})
         

# Profile view
@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        context = {'user': request.user}
        return render(request, 'templates/profile.html', {'user': request.user}, context)

