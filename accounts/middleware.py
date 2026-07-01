from django.contrib.auth import logout
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect


class BlockedUserMiddleware:
    """Log out and redirect users whose profile is_blocked=True."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                is_blocked = request.user.profile.is_blocked
            except ObjectDoesNotExist:
                is_blocked = False
            if is_blocked:
                logout(request)
                messages.error(
                    request,
                    'Your account has been blocked. '
                    'Please contact the administrator.'
                )
                return redirect('accounts:login')

        return self.get_response(request)
