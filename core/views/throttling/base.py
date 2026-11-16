"""Rate-limiting throttles for the public API.

This module provides customized DRF throttle classes that override the
default request rates for anonymous and authenticated clients. The
throttles are consumed by views via the ``throttle_classes`` attribute
or globally through ``DEFAULT_THROTTLE_CLASSES``.

Rates are expressed using DRF's rate syntax, e.g. ``"500/day"`` or
``"20/min"``. The trailing period may be one of ``s``, ``m``, ``h``,
or ``d`` (or their long forms, e.g. ``second``, ``minute``).

Note:
    The rates defined here take precedence over
    ``DEFAULT_THROTTLE_RATES`` because the ``rate`` attribute is set
    explicitly on each class.

    The built-in DRF throttle implementations use non-atomic cache
    operations and are therefore subject to race conditions under high
    concurrency. For strict guarantees, provide a custom atomic
    implementation (e.g. using Redis ``INCR``).
"""

from rest_framework.throttling import (
    AnonRateThrottle as DrfAnonRateThrottle,
    UserRateThrottle as DrfUserRateThrottle,
)


class AnonRateThrottle(DrfAnonRateThrottle):
    """Throttle that limits unauthenticated clients to 500 requests/day.

    The throttle key is derived from the client's IP address (resolved
    from ``X-Forwarded-For`` when present, otherwise ``REMOTE_ADDR``).
    Authenticated requests are ignored by this throttle; use
    :class:`UserRateThrottle` for those.

    Attributes:
        rate (str): The allowed request rate, in DRF rate syntax.
            Overrides ``DEFAULT_THROTTLE_RATES['anon']``.
        scope (str): Cache key scope inherited from the DRF base class
            (``"anon"``).
    """

    rate = "500/day"


class UserRateThrottle(DrfUserRateThrottle):
    """Throttle that limits authenticated clients to 1000 requests/day.

    The throttle key is derived from the authenticated user's primary
    key. Unauthenticated requests fall back to the client's IP address,
    mirroring DRF's default ``UserRateThrottle`` behavior.

    Attributes:
        rate (str): The allowed request rate, in DRF rate syntax.
            Overrides ``DEFAULT_THROTTLE_RATES['user']``.
        scope (str): Cache key scope inherited from the DRF base class
            (``"user"``). Subclasses that add more user throttles
            **must** override ``scope`` to avoid sharing counters.
    """

    rate = "1000/day"
