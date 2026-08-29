"""The three necessary conditions for acting against one's strongest schema.

The whole model is a product of three numbers in [0, 1]. That is the point: the
conditions are requirements, not contributors, so no surplus in one lifts the cap
another one sets.

    A = detection * acceptance * override

What is *not* trivial is where each factor comes from, and in particular that
`acceptance` is governed by quantities the other two do not share. See `latent.py`.

Units throughout are arbitrary and illustrative. They demonstrate an ordering, not
a measurement, and none of the numbers should be quoted as measured values.

The doctests below are the worked example from the paper and run in CI. If a number
here ever disagrees with the manuscript, the build fails.
"""

from __future__ import annotations

from math import exp, isnan

__all__ = ["sigmoid", "autonomy", "ceiling", "attainable", "depth_effect"]


def _in_einheitsintervall(name: str, wert: float) -> float:
    """Wirft, wenn der Wert nicht in [0, 1] liegt. NaN faellt hier ebenfalls durch.

    NaN braucht die eigene Abfrage, weil jeder Vergleich mit NaN False ergibt und ein
    naives `0 <= x <= 1` es deshalb durchlaesst.
    """
    if isnan(wert) or not 0.0 <= wert <= 1.0:
        raise ValueError(f"{name} must lie in [0, 1], got {wert!r}")
    return float(wert)


def sigmoid(x: float) -> float:
    """Logistic function, used for every contest between a signal and a resistance.

    >>> round(sigmoid(0.0), 4)
    0.5
    >>> round(sigmoid(2.0), 4)
    0.8808
    >>> round(sigmoid(-3.0), 4)
    0.0474

    Written in two branches because the one-line version overflows below about -709,
    and a shut gate is the case this model cares about most:

    >>> sigmoid(-1000.0)
    0.0
    """
    if x >= 0.0:
        return 1.0 / (1.0 + exp(-x))
    e = exp(x)
    return e / (1.0 + e)


def autonomy(detection: float, acceptance: float, override: float) -> float:
    """How far a person can act against their strongest schema, in [0, 1].

    The able narcissist from the paper: an excellent error detector and formidable
    modelling ability, meeting a criticism that lands exactly where his self-worth
    is staked.

    >>> round(autonomy(sigmoid(2), sigmoid(-3), sigmoid(2)), 4)
    0.0368

    Strip him of both faculties and he barely moves, because acceptance was the
    binding cap all along:

    >>> round(autonomy(0.5, sigmoid(-3), 0.5), 4)
    0.0119

    His two great faculties multiplied a near-zero by roughly three:

    >>> round(autonomy(sigmoid(2), sigmoid(-3), sigmoid(2))
    ...       / autonomy(0.5, sigmoid(-3), 0.5), 2)
    3.1

    Pass the factors in rounded and you get a different answer. Chaining rounded
    intermediates is itself a way to get a worked example wrong, which is why the
    doctests above use the exact logistic values:

    >>> round(autonomy(0.88, 0.05, 0.88), 5)
    0.03872
    """
    d = _in_einheitsintervall("detection", detection)
    a = _in_einheitsintervall("acceptance", acceptance)
    o = _in_einheitsintervall("override", override)
    return d * a * o


def ceiling(*factors: float) -> float:
    """The upper bound any subset of conditions places on the outcome.

    This is what "necessary condition" means here, and it is weaker than a minimum:
    a product is bounded by each of its factors, but it is not equal to the smallest
    one. Compensation stays possible everywhere; it just gets arbitrarily expensive
    near the edge.

    >>> ceiling(0.9, 0.2, 0.7)
    0.2
    >>> round(ceiling(sigmoid(2), sigmoid(-3)), 4)
    0.0474

    This is the loose bound. The tighter one, and the one worth quoting, is
    `attainable()` below.
    """
    if not factors:
        raise ValueError("ceiling() needs at least one factor")
    # Checked, unlike in the first version. A "ceiling" of 2.0 on a quantity in [0, 1]
    # is not a ceiling, and with NaN in the list min() returns whichever value it met
    # first: the same inputs in a different order gave a different answer.
    return min(_in_einheitsintervall(f"factor {i}", f) for i, f in enumerate(factors))


def attainable(*fixed: float) -> float:
    """The most the outcome can reach while the given conditions stay as they are.

    Hold some factors fixed and let every other condition be perfect: what is left
    is their product. That is the supremum the manuscript writes for the able
    narcissist, detection times acceptance with override at its maximum:

    >>> round(attainable(sigmoid(2), sigmoid(-3)), 4)
    0.0418

    He reaches 0.0368 of a possible 0.0418. Almost all of what he loses, he loses
    at the second condition, and nothing he is good at can be spent there.

    The two bounds are not the same thing, which is why they are two functions.
    `ceiling` is what "necessary condition" means; `attainable` is what the person
    could still do. The first version of this module quoted both under one name.
    """
    if not fixed:
        raise ValueError("attainable() needs at least one factor")
    product = 1.0
    for value in fixed:
        product *= _in_einheitsintervall("factors", value)
    return product


def depth_effect(acceptance: float, detection: float,
                 low: float, high: float) -> float:
    """How much autonomy is actually gained by raising forecasting depth.

    This is the quantity the paper preregisters, and until now the repository did not
    carry it. What it showed instead was the *ratio* of the two autonomies, which is
    constant across acceptance and looks like a striking result. Section 7 of the
    manuscript says why it is not one: take logarithms and the product turns additive,
    so a constant ratio is removable by rescaling and licenses no inference.

    The absolute effect behaves differently, and that difference is the claim:

    >>> from acceptance_gate.latent import override
    >>> weak = override(depth=0.5, habit=1.0, time_cost=0.5)
    >>> strong = override(depth=4.0, habit=1.0, time_cost=0.5)
    >>> for acc in (0.9, 0.1, 0.001):
    ...     print(acc, round(depth_effect(acc, 0.8, weak, strong), 6))
    0.9 0.527191
    0.1 0.058577
    0.001 0.000586

    Three orders of magnitude in acceptance, three in the effect. As acceptance goes to
    zero the gain from ability does too, which is what the model forbids an additive
    account from predicting.

    TODO: rival missing, so this is one side of the disagreement only.
    """
    return (autonomy(detection, acceptance, high)
            - autonomy(detection, acceptance, low))
