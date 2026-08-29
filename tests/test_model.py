"""What the model forbids.

A test suite for a theory is worth something when it fails on claims the theory
rules out, not when it confirms arithmetic. Each test below is named after the
statement it would refute.

Run with:  pytest
"""

from __future__ import annotations

import inspect
import re
from pathlib import Path

import pytest

from acceptance_gate.gate import (attainable, autonomy, ceiling, depth_effect,
                                  sigmoid)
from acceptance_gate.latent import acceptance, detection, optimal_intensity, override
from acceptance_gate.vignettes import (ABLE_NARCISSIST, QUIET_HINT_ON_A_ROUTINE,
                                       STRIPPED_OF_ABILITY, SURGEON_AT_HOME,
                                       SURGEON_AT_WORK, Case, report)

REPO = Path(__file__).resolve().parents[1]


# --- The worked example must keep matching the manuscript -------------------------

def test_vignette_reproduces_the_published_numbers():
    """If the manuscript and this file ever disagree, someone has to look."""
    assert round(ABLE_NARCISSIST.autonomy, 4) == 0.0368
    assert round(STRIPPED_OF_ABILITY.autonomy, 4) == 0.0119
    assert round(ABLE_NARCISSIST.autonomy / STRIPPED_OF_ABILITY.autonomy, 2) == 3.10


def test_rounded_inputs_give_a_different_answer():
    """Chaining rounded intermediates is a way to get a worked example wrong.

    This is not a curiosity. An earlier public draft printed the exact result next
    to rounded inputs, and anyone with a calculator could see the two did not match.
    """
    exact = autonomy(sigmoid(2), sigmoid(-3), sigmoid(2))
    rounded = autonomy(0.88, 0.05, 0.88)
    assert round(exact, 4) == 0.0368
    assert round(rounded, 5) == 0.03872
    assert abs(exact - rounded) > 0.001


# --- The central claim: ability cannot buy its way past a closed gate --------------

def test_ability_multiplies_but_does_not_rescue():
    """Both faculties at their best, and he is still near the floor.

    The temptation is to say ability does nothing. The equation does not support
    that and neither do we: it does something, roughly a factor of three. It just
    does it under a cap.
    """
    gain = ABLE_NARCISSIST.autonomy / STRIPPED_OF_ABILITY.autonomy
    assert gain > 3.0, "ability must visibly help, otherwise we are overclaiming"
    assert ABLE_NARCISSIST.autonomy < 0.05, "and it must not rescue him"


def test_the_absolute_effect_vanishes_with_acceptance():
    """The prediction the manuscript actually preregisters.

    As acceptance goes to zero, the gain from more forecasting depth goes to zero
    with it. An account where the three conditions add up says the opposite: there,
    a large ability compensates a small acceptance.

    Note which quantity this is. The *ratio* of the two autonomies is constant across
    acceptance, which looks impressive and shows nothing: logarithms turn a product
    into a sum, so a constant ratio survives any monotone rescaling of the outcome.
    Section 7 of the paper says so itself. The absolute difference is the claim.
    """
    weak = override(depth=0.5, habit=1.0, time_cost=0.5)
    strong = override(depth=4.0, habit=1.0, time_cost=0.5)

    effekte = [depth_effect(acc, 0.8, weak, strong)
               for acc in (0.9, 0.1, 0.01, 0.001)]
    for vorher, nachher in zip(effekte, effekte[1:]):
        assert nachher < vorher / 5, "the effect has to fall roughly with acceptance"
    assert effekte[-1] < 0.001
    assert effekte[0] > 0.5


def test_the_ratio_is_constant_and_that_is_why_it_proves_nothing():
    """Kept as a warning, not as evidence.

    The constant factor is real and it is what an earlier version of the README put
    forward as the discriminating result. It is a property of any product, and the
    test exists so nobody rediscovers it and mistakes it for a finding.
    """
    weak = override(depth=0.5, habit=1.0, time_cost=0.5)
    strong = override(depth=4.0, habit=1.0, time_cost=0.5)
    for acc in (0.9, 0.5, 0.1, 0.01, 0.001):
        gain = autonomy(0.8, acc, strong) / autonomy(0.8, acc, weak)
        assert gain == pytest.approx(4.815, abs=0.001)


def test_the_surgeon_is_two_people_in_one_day():
    """Same detector, same override, same head. Only the threat differs."""
    assert SURGEON_AT_WORK.detection == SURGEON_AT_HOME.detection
    assert SURGEON_AT_WORK.override == SURGEON_AT_HOME.override
    assert SURGEON_AT_WORK.autonomy > 0.7
    assert SURGEON_AT_HOME.autonomy < 0.05
    ratio = SURGEON_AT_WORK.autonomy / SURGEON_AT_HOME.autonomy
    assert ratio > 15, "the situational difference has to be large, or there is no claim"


# --- Architecture: what must NOT be connected -------------------------------------

def test_ability_does_not_enter_detection_or_acceptance():
    """The load-bearing separation, checked at the signatures and in the source.

    If ability leaked into detection or acceptance, the model would collapse into
    "cleverer people cope better" and there would be nothing left to argue about.
    The signature check alone was a name filter: it would have stayed green had
    someone called the argument `forecast` instead, or had `detection` quietly
    called `override()` inside. So the body is read as well.
    """
    for fn in (detection, acceptance):
        parameter = set(inspect.signature(fn).parameters)
        assert not parameter & {"depth", "fluid", "ability", "cost_weight", "forecast"}, (
            f"{fn.__name__} must not take an ability argument")
        body = inspect.getsource(fn).split('"""')[-1]      # code after the docstring
        for forbidden in ("override(", "optimal_intensity(", "depth"):
            assert forbidden not in body, f"{fn.__name__} reaches into ability via {forbidden!r}"
    assert "depth" in inspect.signature(override).parameters


def test_forecasting_depth_enters_quadratically():
    """Doubling the depth quadruples the benefit term, it does not double it.

    This is a consequence of choosing the effort worth spending, not a stipulation,
    and it predicts a specific curvature that a linear account does not.
    """
    def benefit(depth):
        # invert the logistic to recover what went in
        from math import log
        y = override(depth=depth, habit=0.0, time_cost=0.0)
        return log(y / (1 - y))

    assert benefit(4.0) == pytest.approx(4 * benefit(2.0), rel=1e-9)
    assert optimal_intensity(depth=4.0) == 2.0


# --- Boundaries the model claims for itself ---------------------------------------

def test_no_condition_can_be_bought_off():
    """Perfect in two, hopeless in the third, and the outcome stays hopeless."""
    assert autonomy(1.0, 0.02, 1.0) <= 0.02
    assert autonomy(0.02, 1.0, 1.0) <= 0.02
    assert autonomy(1.0, 1.0, 0.02) <= 0.02


def test_a_product_is_not_a_minimum():
    """We say each condition caps the outcome. We do not say the smallest one IS it.

    Confusing the two would commit us to a claim the evidence does not support, and
    it would make compensation impossible rather than merely expensive.
    """
    a = autonomy(0.5, 0.5, 0.5)
    assert a < ceiling(0.5, 0.5, 0.5), "the product must sit strictly below the minimum"
    assert a == 0.125


def test_the_attainable_bound_sits_between_outcome_and_minimum():
    """What he could still reach lies above what he reaches and below the loose cap."""
    reached = ABLE_NARCISSIST.autonomy
    could = attainable(ABLE_NARCISSIST.detection, ABLE_NARCISSIST.acceptance)
    loose = ceiling(ABLE_NARCISSIST.detection, ABLE_NARCISSIST.acceptance)
    assert reached < could < loose
    assert round(could, 4) == 0.0418


# --- The prose must keep matching the code ----------------------------------------
#
# README and explainer page each print numbers. Nothing stops a hand-edited table
# from going stale except a test that reads it, so these two do.

def test_readme_table_matches_report():
    """Named for what it does. It compares against report(), not against the output
    of the documented command, which prints two further lines about the units."""
    text = (REPO / "README.md").read_text(encoding="utf-8")
    block = re.search(r"\$ python -m acceptance_gate\.vignettes\n(.*?)```", text, re.S)
    assert block, "the README no longer shows the vignette table"
    printed = [line for line in block.group(1).splitlines() if line.strip()]
    assert printed == report().splitlines()


def test_every_condition_binds_in_at_least_one_case():
    """A model advertising three ceilings should show each of them doing some work.

    Until the fifth case was added, all four bound at acceptance, and a reader could
    reasonably ask whether the other two conditions were decorative.
    """
    bindend = {c.binds_at for c in (ABLE_NARCISSIST, SURGEON_AT_HOME,
                                    QUIET_HINT_ON_A_ROUTINE, SURGEON_AT_WORK)}
    assert "acceptance" in bindend
    assert "detection" in bindend
    assert "nothing; all three admit" in bindend
    # TODO: no case binds at the override. Needs one from the paper, not invented.


def test_an_impossible_case_cannot_be_built():
    """The dataclass used to accept anything and answer questions about it.

    Case(detection=5.0, ...) came into being without complaint, and binds_at then
    reported which condition bound for a person who cannot exist.
    """
    with pytest.raises(ValueError):
        Case(name="impossible", detection=5.0, acceptance=-2.0, override=0.5,
             source="none")


def test_explainer_constants_are_the_surgeon():
    """The page carries its own copy of the model in JavaScript. Same numbers, or red."""
    page = (REPO / "docs" / "index.html").read_text(encoding="utf-8")

    def const(name):
        found = re.search(rf"const {name}\s*=\s*sig\((-?[\d.]+)\)", page)
        assert found, f"{name} not found on the explainer page"
        return sigmoid(float(found.group(1)))

    assert const("DETECTION") == SURGEON_AT_WORK.detection
    assert const("ACC_THEATRE") == SURGEON_AT_WORK.acceptance
    assert const("ACC_HOME") == SURGEON_AT_HOME.acceptance

    costs = re.search(r"const C = ([\d.]+), S2 = ([\d.]+), R_DT = ([\d.]+)", page)
    assert costs, "cost constants not found on the explainer page"
    c, s2, r_dt = (float(v) for v in costs.groups())
    slider_max = float(re.search(r'id="r-p"[^>]*max="([\d.]+)"', page).group(1))
    assert override(depth=slider_max, habit=s2, cost_weight=c, time_cost=r_dt) \
        == SURGEON_AT_WORK.override

    # The slider's left end sets the reference point for the factor the page prints.
    p_min = float(re.search(r"const P_MIN = ([\d.]+)", page).group(1))
    assert p_min < slider_max


def test_explainer_printed_results_are_real():
    """The two numbers in the page's example block.

    They were the last unchecked figures on the page, and the block showed them as
    bare interpreter output while the true value has fourteen more digits. Changing
    either one used to leave the suite green.
    """
    page = (REPO / "docs" / "index.html").read_text(encoding="utf-8")
    block = re.search(r"&gt;&gt;&gt; round\(autonomy\(sigmoid\(2\).*?</pre>", page, re.S)
    assert block, "the example block on the explainer page has moved or changed shape"
    gedruckt = re.findall(r"^(0\.\d+)$", block.group(0), re.M)
    assert gedruckt == ["0.0368", "0.0119"], gedruckt
    assert round(autonomy(sigmoid(2), sigmoid(-3), sigmoid(2)), 4) == 0.0368
    assert round(autonomy(0.5, sigmoid(-3), 0.5), 4) == 0.0119


def test_the_version_is_the_same_in_all_four_places():
    """A drifting version is the one error that produces a wrong citation.

    Setting __version__ to something else used to leave the whole suite green.
    """
    import acceptance_gate

    v = acceptance_gate.__version__
    py = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    cff = (REPO / "CITATION.cff").read_text(encoding="utf-8")
    chg = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    assert re.search(rf'^version = "{re.escape(v)}"$', py, re.M)
    assert re.search(rf"^version: {re.escape(v)}$", cff, re.M)
    assert re.search(rf"## {re.escape(v)}", chg)


def test_autonomy_stays_in_the_unit_interval():
    for d in (0.0, 0.3, 1.0):
        for acc in (0.0, 0.6, 1.0):
            for o in (0.0, 0.9, 1.0):
                assert 0.0 <= autonomy(d, acc, o) <= 1.0


def test_impossible_inputs_are_refused_loudly():
    """A silent clamp would hide a modelling error behind a plausible number."""
    with pytest.raises(ValueError):
        autonomy(1.2, 0.5, 0.5)
    with pytest.raises(ValueError):
        autonomy(0.5, -0.1, 0.5)
    with pytest.raises(ValueError):
        override(depth=1.0, habit=0.0, cost_weight=0.0)
    with pytest.raises(ValueError):
        detection(automatic=1.0, conscious=1.0, disposition=5.0)
    with pytest.raises(ValueError):
        override(depth=1.0, habit=-99.0)


def test_a_negative_forecast_buys_no_override():
    """The appendix reads the numerator as max(P, 0) squared.

    Before this test existed, override(-4) returned the same value as override(+4),
    handing the worst forecaster the capacity of the best. A square is blind to
    sign; the model is not supposed to be.
    """
    assert override(depth=-4.0, habit=1.0, time_cost=1.0) == pytest.approx(sigmoid(-2.0))
    assert override(depth=-4.0, habit=1.0, time_cost=1.0) < override(depth=4.0, habit=1.0, time_cost=1.0)
    assert override(depth=-4.0, habit=1.0, time_cost=1.0) == override(depth=0.0, habit=1.0, time_cost=1.0)
    assert optimal_intensity(depth=-4.0) == 0.0
