# your_project/urls.py

from django.urls import path, include
from .views import CustomSignupView  # Import your custom view

urlpatterns = [
    # Override the default Allauth signup URL
    path('accounts/signup/', CustomSignupView.as_view(), name='account_signup'),

    # Allauth's URLs must come AFTER your custom URL
    path('accounts/', include('allauth.urls')),
]
    # ... other project URLs
