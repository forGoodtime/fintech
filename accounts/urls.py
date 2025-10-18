from django.urls import path
from django.http import JsonResponse
from . import views

def auth_endpoints(request):
    return JsonResponse({
        'endpoints': {
            'register': '/api/auth/register/',
            'login': '/api/auth/login/',
            'logout': '/api/auth/logout/',
            'profile': '/api/auth/profile/',
            'profile_details': '/api/auth/profile/details/',
            'change_password': '/api/auth/change-password/',
            'users': '/api/auth/users/',
        }
    })

urlpatterns = [
    path('', auth_endpoints, name='auth-endpoints'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/details/', views.UserProfileDetailView.as_view(), name='user-profile-details'),
    path('change-password/', views.change_password, name='change-password'),
    path('users/', views.UserListView.as_view(), name='user-list'),
]
