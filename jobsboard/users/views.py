from django.shortcuts import render, redirect
from django.views import View
from .forms import SignupForm
from django.contrib import messages

# Signup view
class SignupView(View):
    def get(self, request):
        return render(request, 'template/signup.html', {'form': 'form'})

    def post(self, request):
        # Handle user signup logic here
        form=SignupForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
        return render(request, 'template/signup.html', {'form': form})
       
        

# Login view

# Logout view

# Profile view

