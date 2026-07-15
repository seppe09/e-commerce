from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

User = get_user_model()

class UserRegisterView(View):
    template_name = "users/register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard_view")
        return render(request, self.template_name)

    def post(self, request):

        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').lower().strip()
        email = request.POST.get('email', '').lower().strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        errors = {}

        if not username:
            errors['username'] = "Username is required."

        if not email:
            errors['email'] = "Email is required."

        if password != confirm_password:
            errors['password'] = "Passwords do not match."

        if User.objects.filter(username=username).exists():
            errors["username"] = "Username is already taken."

        if User.objects.filter(email=email).exists():
            errors["email"] = "Email is already registered."

        context = {
            "errors": errors,
            "data": request.POST
        }        
        
        if errors:
            return render(request, self.template_name, context)
        
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password,
        )

        login(request, user)
        return redirect("dashboard_view")


class UserEditView(LoginRequiredMixin, View):
    login_url = 'login_view'
    template_name = "users/edit.html"

    def get(self, request):
        context = {
            "data": {
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "username": request.user.username,
                "email": request.user.email,
            }
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user = request.user
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').lower().strip()
        email = request.POST.get('email', '').lower().strip()

        errors = {}

        if not username:
            errors['username'] = "Username is required."
        elif User.objects.filter(username=username).exclude(pk=user.pk).exists():
            errors["username"] = "Username is already taken."

        if not email:
            errors['email'] = "Email is required."
        elif User.objects.filter(email=email).exclude(pk=user.pk).exists():
            errors["email"] = "Email is already registered."

        if errors:
            context = {
                "errors": errors,
                "data": request.POST
            }
            return render(request, self.template_name, context)

        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("dashboard_view")


class UserLoginView(View):
    template_name = "users/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard_view")
        return render(request, self.template_name)

    def post(self, request):
        username_or_email = request.POST.get('username_or_email', '').strip()
        password = request.POST.get('password')
        errors = {}

        if not username_or_email:
            errors['username_or_email'] = "Username or Email is required."
        if not password:
            errors['password'] = "Password is required."

        if not errors:
            # Check if username_or_email is an email
            user = None
            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            else:
                user = authenticate(request, username=username_or_email, password=password)
        
            if user is not None:
                if user.deleted_at != True:
                    login(request, user)
                    return redirect("dashboard_view")
                else:
                    errors["deleted_account"] = True
                    errors["username_or_email"] = "This account has been deleted. You can recover it."
            else:
                errors['non_field'] = "Invalid username/email or password."


        context = {
            "errors": errors,
            "data": request.POST
        }
        return render(request, self.template_name, context)


class UserDashboardView(LoginRequiredMixin, View):
    login_url = 'login_view'
    template_name = "users/dashboard.html"

    def get(self, request):
        return render(request, self.template_name)


class UserLogoutView(View):

    def post(self, request):
        logout(request)
        return redirect("login_view")
    

class UserAccountDeletionView(LoginRequiredMixin, View):
    login_url = 'login_view'
    template_name = "users/delete.html"

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        # Only allow deleting own account or admin
        if request.user.pk == pk or request.user.is_staff:
            return render(request, self.template_name, {"profile": user})
        messages.error(request, "You do not have permission to delete this account.")
        return redirect("dashboard_view")
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        # Only allow deleting own account or admin
        if not (request.user.pk == pk or request.user.is_staff):
            messages.error(request, "You do not have permission to delete this account.")
            return redirect("dashboard_view")

        username = request.user.username
        password = request.POST.get("password")

        valid = authenticate(request, username=username, password=password)

        if valid:
            user.deleted_at = True
            user.save(update_fields=["deleted_at"])
            logout(request)
            messages.success(request, "Account deletion was successful.")
            return redirect("login_view")
        
        messages.error(request, "Validation failed, credentials do not match.")
        return redirect("dashboard_view")


class UserAccountRecoveryView(View):
    template_name = "users/recovery.html"

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        username_or_email = request.POST.get("username_or_email", "").strip()
        password = request.POST.get("password")
        errors = {}

        if not username_or_email:
            errors["username_or_email"] = "Username or Email is required."
        if not password:
            errors["password"] = "Password is required."

        if not errors:
            user_obj = None
            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                except User.DoesNotExist:
                    pass
            else:
                try:
                    user_obj = User.objects.get(username=username_or_email)
                except User.DoesNotExist:
                    pass

            if user_obj is not None:
                user = authenticate(request, username=user_obj.username, password=password)
                if user is not None:
                    if user.deleted_at == True:
                        user.deleted_at = False
                        user.save(update_fields=["deleted_at"])
                        login(request, user)
                        messages.success(request, "Account recovery was successful. You are now logged in.")
                        return redirect("dashboard_view")
                    else:
                        errors["non_field"] = "This account is already active. You can just sign in."
                else:
                    errors["non_field"] = "Invalid credentials."
            else:
                errors["non_field"] = "No account found with those credentials."

        context = {
            "errors": errors,
            "data": request.POST
        }
        return render(request, self.template_name, context)


class UserPasswordUpdateView(LoginRequiredMixin, View):
    template_name = "users/password_change.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        
        if not request.user.check_password(old_password):
            messages.error(request, "Old password is incorrect.")
            return redirect("update_password_view")
        
        if new_password != confirm_password:
            messages.error(request, "New passwords are not matching.")
            return redirect("update_password_view")
        
        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "Password updated successfully.")
        return redirect("dashboard_view")


            
            
