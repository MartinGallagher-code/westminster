def supporter_status(request):
    """Add is_supporter flag to template context for all authenticated users."""
    if request.user.is_authenticated:
        try:
            return {
                'is_supporter': request.user.supporter_subscription.is_active
            }
        except Exception:
            pass
    return {'is_supporter': False}
