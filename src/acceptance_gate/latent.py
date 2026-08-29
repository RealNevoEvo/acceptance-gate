"""Where the three conditions come from.

`gate.autonomy` multiplies three numbers, and that part is nearly trivial. The claim
lives here, in what feeds each factor:

    detection  = sigmoid(Z - S1)                with Z = W3 * (w1*W1 + w2*W2)
    acceptance = sigmoid(g - tau)
    override   = sigmoid(max(P, 0)**2 / (4c) - S2 - r*dt)
                 with P = fluid ability * calibrated experience

Two features of that mapping are the whole point of the paper, and both are visible
in the signatures below.

First, **ability enters once**. It reaches the model through `P` in `override`, and
it enters *quadratically*, because `P**2/(4c)` is what you get when you let a person
choose the effort worth spending rather than paying for effort at a fixed rate. It
does not appear in `detection` and it does not appear in `acceptance`.

Second, **acceptance is governed by quantities the other two do not share**: a global,
non-contingent foundation `g`, set against the threat `tau` that this particular truth
poses to self-worth in this particular domain. That is why the same person can be
open in the operating theatre and closed at the dinner table six hours later: `g` is
the same, `tau` is not.

If either feature is wrong, the model is wrong in the way it is meant to be capable of
being wrong.

Units are arbitrary and illustrative throughout.
"""

from __future__ import annotations

from math import isnan

from .gate import sigmoid

__all__ = ["detection", "acceptance", "override", "optimal_intensity"]


def _nicht_negativ(name: str, wert: float) -> float:
    """Weist negative Werte und NaN ab.

    NaN braucht die eigene Abfrage: `nan <= 0` ist False, also kam NaN frueher durch
    jeden Waechter und starb erst spaeter in autonomy(), mit einer Fehlermeldung, die
    auf die falsche Stelle zeigte.
    """
    if isnan(wert) or wert < 0:
        raise ValueError(f"{name} must be non-negative, got {wert!r}")
    return float(wert)


def detection(automatic: float, conscious: float, disposition: float = 1.0,
              prior_precision: float = 0.0, w1: float = 0.5, w2: float = 0.5) -> float:
    """Does the discrepancy reach metacognition at all?

    The raw signal has an automatic part (the error-related negativity) and a
    conscious part (the error positivity). `disposition` is the standing tendency to
    pursue a discrepancy rather than let it pass; it scales the raw signal instead of
    adding to it, which is why a person who never follows anything up cannot be
    rescued by a louder signal.

    `prior_precision` is the resistance: how firmly the expectation is held that the
    signal has to argue against.

    Note what is absent from the signature: ability.

    >>> round(detection(automatic=2.0, conscious=2.0), 4)
    0.8808
    >>> round(detection(automatic=2.0, conscious=2.0, disposition=0.0), 4)
    0.5

    A disposition of zero does not silence the signal, it removes the gain on it.
    What remains is the contest between nothing and the prior, and with no prior
    to argue against that contest is a coin toss.

    `disposition` lives in [0, 1]: it scales, it does not amplify. The appendix
    says so, and a value above one would let a keen temperament manufacture
    evidence that never arrived. `prior_precision` is an inverse variance and so
    cannot be negative; that was written in a comment before it was enforced here.

    The weights default to half each and are not estimates. The manuscript declines
    to give numbers for them, and so does this: they are here so the signature matches
    the equation, not because 0.5 means anything.
    """
    if isnan(disposition) or not 0.0 <= disposition <= 1.0:
        raise ValueError(f"disposition must lie in [0, 1], got {disposition!r}")
    _nicht_negativ("prior_precision", prior_precision)
    raw = disposition * (w1 * automatic + w2 * conscious)
    return sigmoid(raw - prior_precision)


def acceptance(foundation: float, threat: float) -> float:
    """Is the truth allowed to be true of oneself?

    `foundation` is self-worth that does not hang on this or any other outcome.
    `threat` is what admitting this particular truth would cost in the domain where
    worth happens to be staked.

    A warning that matters more than it looks: `foundation` is **not** how high
    someone's self-esteem is. On most instruments the narcissist reports more of it
    than you do. It is whether worth is contingent on being right here.

    >>> round(acceptance(foundation=2.0, threat=0.0), 4)
    0.8808
    >>> round(acceptance(foundation=2.0, threat=5.0), 4)
    0.0474

    Same foundation, different domain, and the gate has shut. Nothing about the
    person changed between the two lines.
    """
    return sigmoid(foundation - threat)


def optimal_intensity(depth: float, cost_weight: float = 1.0) -> float:
    """How hard it is worth pushing, given how far ahead one can see.

    Effort has a benefit as well as a price. Maximising `intensity*depth - c*intensity**2`
    over intensity gives `depth / (2c)`. Writing only the cost, as an earlier version of
    this model did, would imply that the surest route to overriding a habit is not to
    try at all.

    >>> optimal_intensity(depth=4.0, cost_weight=1.0)
    2.0
    >>> optimal_intensity(depth=-4.0)
    0.0

    A negative forecast points nowhere. There is nothing to spend effort on, and
    without the floor the formula would prescribe negative effort, which means
    nothing at all.
    """
    if isnan(cost_weight) or cost_weight <= 0:
        raise ValueError(f"cost_weight must be positive, got {cost_weight!r}")
    return max(depth, 0.0) / (2.0 * cost_weight)


def override(depth: float, habit: float, cost_weight: float = 1.0,
             time_cost: float = 0.0) -> float:
    """Does the new intention beat the practised one?

    `depth` is how far the person can project the consequences, the product of fluid
    ability and calibrated experience. Substituting the optimal effort from above
    turns the benefit term into `depth**2 / (4c)`, so **forecasting depth enters
    quadratically**. That is a consequence, not a stipulation, and it is a testable
    one: it predicts a specific curvature rather than a general "more is better".

    `habit` is the categorical pull of the practised policy, `time_cost` the price of
    holding control open.

    >>> round(override(depth=4.0, habit=1.0, time_cost=0.5), 4)
    0.9241
    >>> round(override(depth=0.5, habit=1.0, time_cost=0.5), 4)
    0.1919

    Eight times the depth, but the two numbers differ by less than a factor of five,
    because a logistic saturates. Ability runs out of room even where nothing blocks it.

    The numerator is read as `max(depth, 0)**2`, because a square is blind to sign
    and would otherwise hand the worst forecaster the same override as the best:

    >>> round(override(depth=-4.0, habit=1.0, time_cost=1.0), 4)
    0.1192

    That is sigmoid(-2): no benefit, only the habit and the cost of waiting. The
    appendix states the domain; this file did not enforce it at first.

    `habit` here is the effective pull of the practised policy. The manuscript splits
    it into the habit proper and an inhibition trace that suppression leaves behind,
    which is how a recovering addict differs from an active one. That trace is carried
    in the paper but not used, and it is not modelled here either.

    TODO: time_cost has no upper bound. Ask whether the paper wants one.
    """
    if isnan(cost_weight) or cost_weight <= 0:
        raise ValueError(f"cost_weight must be positive, got {cost_weight!r}")
    _nicht_negativ("habit", habit)
    _nicht_negativ("time_cost", time_cost)
    benefit = max(depth, 0.0) ** 2 / (4.0 * cost_weight)
    return sigmoid(benefit - habit - time_cost)
