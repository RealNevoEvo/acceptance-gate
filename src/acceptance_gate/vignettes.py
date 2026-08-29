"""The worked cases from the paper, as data.

Keeping them here rather than inside the tests means the numbers have one home. If
the manuscript changes, this file changes, and the tests fail until someone looks.

Units are arbitrary and illustrative. They demonstrate an ordering, not a measurement,
and none of them should be quoted as measured values.
"""

from __future__ import annotations

from dataclasses import dataclass

from .gate import autonomy as _autonomy
from .latent import acceptance, detection, override

__all__ = ["Case", "ABLE_NARCISSIST", "STRIPPED_OF_ABILITY",
           "SURGEON_AT_WORK", "SURGEON_AT_HOME", "QUIET_HINT_ON_A_ROUTINE",
           "ALL_CASES"]

# Below this, a condition is called the one that binds. Above it, nothing does.
# The line is a reading aid for the table, not a claim; the manuscript draws none.
_BINDING_LINE = 0.5


@dataclass(frozen=True)
class Case:
    """One person meeting one truth in one situation.

    `source` says where the case comes from. Two of the four are worked through
    in the manuscript with these exact numbers; the surgeon is a scene from the
    introduction whose parameters were chosen here, to make the scene calculable.
    """

    name: str
    detection: float
    acceptance: float
    override: float
    source: str

    def __post_init__(self) -> None:
        # Ohne das liess sich ein Fall mit detection=5.0 bauen, und binds_at
        # beantwortete brav eine Frage ueber eine Person, die es nicht geben kann.
        # Erst autonomy warf, also zu spaet.
        _autonomy(self.detection, self.acceptance, self.override)

    @property
    def autonomy(self) -> float:
        return _autonomy(self.detection, self.acceptance, self.override)

    @property
    def binds_at(self) -> str:
        """Which condition sets the cap, derived from the numbers rather than typed.

        A typed label can go quietly stale when a parameter changes. This one
        cannot: it is the name of the smallest factor, if that factor is low.
        """
        smallest = min(("detection", self.detection), ("acceptance", self.acceptance),
                       ("override", self.override), key=lambda pair: pair[1])
        if smallest[1] >= _BINDING_LINE:
            return "nothing; all three admit"
        return smallest[0]


# --- The able narcissist, section "A worked example" ------------------------------
# Excellent detector, formidable modelling, criticism landing exactly where his
# self-worth is staked. Both faculties are two units above their resistance; the
# threat is three units above his foundation. The override arguments are chosen so that
# the term inside the logistic is exactly 2, matching sigma(2) in the manuscript.
# The detector gets there with a strong signal against a neutral prior, not with a
# negative precision: a precision is an inverse variance, it has no sign to flip.

ABLE_NARCISSIST = Case(
    name="able narcissist",
    detection=detection(automatic=2.0, conscious=2.0),
    acceptance=acceptance(foundation=0.0, threat=3.0),
    override=override(depth=4.0, habit=1.0, time_cost=1.0),
    source="manuscript, sec:worked, these numbers",
)

STRIPPED_OF_ABILITY = Case(
    name="same man, both faculties removed",
    detection=0.5,
    acceptance=acceptance(foundation=0.0, threat=3.0),
    override=0.5,
    source="manuscript, sec:worked, these numbers",
)

# --- The surgeon, opening of the paper ---------------------------------------------
# The same woman, six hours apart. Detection and override are identical, because it is
# the same head. Only the threat to what her worth rests on differs.
#
# The manuscript tells the scene and gives no numbers for it. The parameters below
# were chosen for this repository: her detector and her override match the able
# narcissist's, her foundation is solid, and the afternoon threat is set high enough
# to shut the gate. Do not look for 0.7170 in the paper, it is not there.

_HER_DETECTION = detection(automatic=2.0, conscious=2.0)
_HER_OVERRIDE = override(depth=4.0, habit=1.0, time_cost=0.5)

SURGEON_AT_WORK = Case(
    name="surgeon, 9am, operating theatre",
    detection=_HER_DETECTION,
    acceptance=acceptance(foundation=2.0, threat=0.0),
    override=_HER_OVERRIDE,
    source="manuscript, sec:intro, the scene; parameters chosen here",
)

SURGEON_AT_HOME = Case(
    name="surgeon, 3pm, at home",
    detection=_HER_DETECTION,
    acceptance=acceptance(foundation=2.0, threat=5.0),
    override=_HER_OVERRIDE,
    source="manuscript, sec:intro, the scene; parameters chosen here",
)

# --- A case where the FIRST condition binds ----------------------------------------
# The four cases above all bind at acceptance, which made the table lopsided: a model
# advertising three ceilings never showed the first one doing any work. This is an
# ordinary situation, not a clinical one. A practitioner, sure of a routine, gets a
# quiet hint from someone junior. Nothing is wrong with her openness and nothing is
# wrong with her control; the signal simply loses the contest against the expectation.
#
# Parameters chosen here, like the surgeon's. The manuscript names no such case.

QUIET_HINT_ON_A_ROUTINE = Case(
    name="quiet hint, settled routine",
    detection=detection(automatic=0.4, conscious=0.3, prior_precision=1.6),
    acceptance=acceptance(foundation=2.0, threat=0.0),
    override=_HER_OVERRIDE,
    source="not in the manuscript; chosen here to show condition 1 binding",
)

ALL_CASES = (ABLE_NARCISSIST, STRIPPED_OF_ABILITY, SURGEON_AT_WORK, SURGEON_AT_HOME,
             QUIET_HINT_ON_A_ROUTINE)


def report() -> str:
    """A table of every case, for the command line.

    The doctest checks the numbers, not the column widths. Layout is allowed to
    change; the published values are not.

    >>> rows = report().splitlines()
    >>> "0.0368" in rows[2] and "able narcissist" in rows[2]
    True
    >>> "0.7170" in rows[4] and "0.0386" in rows[5]
    True
    >>> SURGEON_AT_WORK.binds_at
    'nothing; all three admit'
    >>> QUIET_HINT_ON_A_ROUTINE.binds_at
    'detection'
    >>> sorted({c.binds_at for c in ALL_CASES})
    ['acceptance', 'detection', 'nothing; all three admit']
    """
    header = f"{'case':<40} {'det':>6} {'acc':>6} {'ovr':>6} {'A':>8}  binds at"
    rows = [header, "-" * 84]
    for c in ALL_CASES:
        rows.append(f"{c.name:<40} {c.detection:>6.3f} {c.acceptance:>6.3f} "
                    f"{c.override:>6.3f} {c.autonomy:>8.4f}  {c.binds_at}")
    return "\n".join(rows)


if __name__ == "__main__":
    print(report())
    print()
    print("Units are arbitrary and illustrative: an ordering, not a measurement.")
