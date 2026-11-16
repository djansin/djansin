"""Burst and sustained throttles layered on top of the base user throttle.

This module defines two additional user-scoped throttles used to
implement a two-tier rate-limiting policy:

* **Burst** — a short-window limit to absorb traffic spikes.
* **Sustained** — a long-window limit to cap overall usage.

Both throttles inherit from :class:`core.throttling.UserRateThrottle`
and differ only in their ``scope`` (unique cache key) and ``rate``.
Because each ``scope`` is unique, their counters are fully independent:
a client is throttled as soon as *either* limit is reached.

Note:
    ``UserRateThrottle`` falls back to the client IP for unauthenticated
    requests, so these throttles also apply to anonymous traffic.
"""

from core.views.throttling import UserRateThrottle


class BurstRateThrottle(UserRateThrottle):
    """Short-window throttle limiting clients to 20 requests/minute.

    Intended to protect the API against sudden bursts of traffic. The
    cache key is scoped as ``"burst"`` so it does not collide with the
    daily user counter or the sustained counter.

    Attributes:
        scope (str): Unique cache key scope, ``"burst"``.
        rate (str): Allowed request rate, ``"20/min"``.
    """

    scope = "burst"
    rate = "20/min"


class SustainedRateThrottle(UserRateThrottle):
    """Long-window throttle limiting clients to 1000 requests/day.

    Complements :class:`BurstRateThrottle` by capping sustained usage
    over a full day. The cache key is scoped as ``"sustained"`` so it
    is fully independent of the burst and base user counters.

    Attributes:
        scope (str): Unique cache key scope, ``"sustained"``.
        rate (str): Allowed request rate, ``"1000/day"``.
    """

    scope = "sustained"
    rate = "1000/day"
