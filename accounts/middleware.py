from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect


class BlockedUserMiddleware:
    """Log out and redirect users whose profile is_blocked=True."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                if request.user.profile.is_blocked:
                    logout(request)
                    messages.error(
                        request,
                        'Your account has been blocked. '
                        'Please contact the administrator.'
                    )
                    return redirect('accounts:login')
            except Exception:
                pass

        return self.get_response(request)
