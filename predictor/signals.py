from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .models import LoginActivity


# Getting the IP address of the client
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")

# Creating a receiver for User login event
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    LoginActivity.objects.create(
        user=user,
        event_type="login",
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")
    )

# Creating a receiver for User logout event
@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    LoginActivity.objects.create(
        user=user,
        event_type="logout",
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")
    )

# Creating a receiver for User login-failure event
@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    LoginActivity.objects.create(
        user=None,
        event_type="failed",
        ip_address=get_client_ip(request) if request else None,
        user_agent=request.META.get("HTTP_USER_AGENT", "") if request else ""
    )