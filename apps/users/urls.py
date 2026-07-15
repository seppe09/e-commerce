from django.urls import path
from .views import UserRegisterView, UserLoginView, UserDashboardView, UserLogoutView, UserDeletionView, UserRecoveryView, UserEditView, UserPasswordUpdate

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register_view'),
    path('login/', UserLoginView.as_view(), name='login_view'),
    path('dashboard/', UserDashboardView.as_view(), name='dashboard_view'),
    path('logout/', UserLogoutView.as_view(), name='logout_view'),
    path('delete/<int:pk>/', UserDeletionView.as_view(), name='delete_view'),
    path('recovery/', UserRecoveryView.as_view(), name='recovery_view'),
    path('profile/edit/', UserEditView.as_view(), name='edit_profile_view'),
    path('profile/password-update/', UserPasswordUpdate.as_view(), name='update_password_view'),
]


