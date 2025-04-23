class EnsureSessionMiddleware:
    """
    Ensures every request has a session to link players to game instances without manual checks.
    Creates a session if none exists, as Django doesn’t do this by default.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.session_key:
            request.session.create()
        return self.get_response(request)
