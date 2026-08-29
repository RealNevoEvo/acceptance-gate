"""A three-condition model of the capacity to act against one's strongest schema.

    >>> from acceptance_gate import autonomy, sigmoid
    >>> round(autonomy(sigmoid(2), sigmoid(-3), sigmoid(2)), 4)
    0.0368

Companion code to *The Acceptance Gate: Three Necessary Conditions for the Capacity
to Act Against One's Strongest Schema*.

Units are arbitrary and illustrative. They demonstrate an ordering, not a measurement.
"""

from .gate import attainable, autonomy, ceiling, depth_effect, sigmoid
from .latent import acceptance, detection, optimal_intensity, override

__version__ = "0.1.0"
__all__ = ["autonomy", "ceiling", "attainable", "depth_effect", "sigmoid",
           "acceptance", "detection", "override", "optimal_intensity"]
