"""
Custom Axes authentication backend.

Axes 6.x backends are monitoring-only: they never authenticate a user, and
they only refuse when ``settings.AXES_LOCK_OUT_AT_FAILURE`` is True — in which
case the failed attempt that *reaches* the failure limit is itself flagged
(so the 5th failure would already produce a lockout response).

This project's login UX (and its test suite) expects the opposite: the 5
failed attempts are plain 401s, and only the *next* attempt is blocked. With
``AXES_LOCK_OUT_AT_FAILURE=False`` Axes never blocks at all, so this backend
re-implements the lockout check based on failures recorded by **previous**
attempts and marks the request for the DRF exception handler (which converts
the 401 into a 403 lockout response).
"""

from axes.backends import AxesStandaloneBackend
from axes.exceptions import AxesBackendPermissionDenied, AxesBackendRequestParameterRequired
from axes.handlers.proxy import AxesProxyHandler
from axes.helpers import get_credentials, get_failure_limit


class AxesNextAttemptLockoutBackend(AxesStandaloneBackend):
    """
    Block login attempts once failures recorded by previous attempts reach
    ``AXES_FAILURE_LIMIT``, without flagging the attempt that reached the limit.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if request is None:
            raise AxesBackendRequestParameterRequired("AxesBackend requires a request as an argument to authenticate")

        credentials = get_credentials(username=username, password=password, **kwargs)

        # Failures recorded by *previous* attempts (this attempt's failure is
        # only recorded later, via the user_login_failed signal).
        if AxesProxyHandler.get_failures(request, credentials) >= get_failure_limit(request, credentials):
            request.axes_locked_out = True
            request.axes_credentials = credentials
            raise AxesBackendPermissionDenied("AxesBackend detected that the given user is locked out")

        return None
