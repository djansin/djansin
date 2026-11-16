"""Project-wide three-tier throttling policy for DRF views.

This module exposes :class:`RateLimitThrottleMixin`, a thin mixin that
attaches a three-tier throttling policy to any DRF view or viewset:

    * **Anonymous** (``AnonRateThrottle``) — caps unauthenticated
      traffic per client IP.
    * **Burst** (``BurstRateThrottle``) — a short-window cap that
      absorbs sudden spikes.
    * **Sustained** (``SustainedRateThrottle``) — a long-window cap that
      limits overall daily usage.
"""

from core.views.throttling import (
    AnonRateThrottle,
    BurstRateThrottle,
    SustainedRateThrottle,
)


class RateLimitThrottleMixin:
    """Applies anonymous, burst, and sustained throttles to the view.

    All three throttles are evaluated independently; the request is
    rejected as soon as any bucket is exhausted. Authenticated clients
    are exempt from ``AnonRateThrottle`` but remain subject to burst and
    sustained limits. Throttles run at the view level, so all actions
    (including ``retrieve``) consume the buckets.

    Attributes:
        throttle_classes (list[type]): Default throttles applied to any
            inheriting view. Override per-view to customize the policy.
    """

    throttle_classes = [AnonRateThrottle, BurstRateThrottle, SustainedRateThrottle]
