# acceptance-gate

**A surgeon accepts a correction at nine in the morning and refuses the same kind of
correction at three in the afternoon. Nothing about her intelligence changed in
between. This is a model of what did.**

Companion code to *The Acceptance Gate: Three Necessary Conditions for the Capacity to
Act Against One's Strongest Schema*. No dependencies, one equation, and the worked
cases from the manuscript as executable tests.

```python
>>> from acceptance_gate import autonomy, sigmoid
>>> round(autonomy(sigmoid(2), sigmoid(-3), sigmoid(2)), 4)
0.0368

```

---

## The claim

Acting against your own strongest habit requires three things, and each one caps the
result on its own:

```
A = detection · acceptance · override
```

**Detection** represents the probability that an error or discrepancy is registered by monitoring
mechanisms. **Override** represents the probability that executive control successfully suppresses
the prepotent response, given the computational costs of control. Both components build on extensive
experimental literature.

**Acceptance** represents whether the registered discrepancy is integrated into self-evaluation
rather than defensively rejected or rationalised when it conflicts with contingent self-worth.

The constructs are established. What is claimed as new is the wiring: that acceptance is
a condition in its own right, that it does not reduce to understanding, and that a
surplus in one condition cannot lift the cap another one sets. Compensation stays
possible everywhere, it just becomes arbitrarily expensive near the edge.

## What this is for, and what it is not

Use it to see what the model **forbids**, and to check a claim about it against the
code. The worked cases run as tests; the equation is short enough to read in one
sitting. If you want to fit the model to data, the manuscript's appendix on
identifiability is where to start, and this repository will not do the fitting for you.

It does one thing, on purpose. The four equations of motion, describing how these
quantities change over a life, are the subject of the companion paper and are **not**
here. There is no calibration, and there will be none: units are arbitrary throughout,
and a number from this code should never be quoted as a measurement.

An interactive demonstration is available on the [explainer
page](https://realnevoevo.github.io/acceptance-gate/).

## Why a product

The multiplicative formulation specifies that each condition is strictly necessary. If empirical
evidence demonstrates continuous trade-offs or additive substitution among detection, acceptance,
and override, the proposed architecture is falsified.

**Distinguishing multiplicative from additive architectures.** In a product model, scaling the
override capacity increases autonomy by an identical relative factor regardless of the baseline
acceptance level. However, because constant multiplicative ratios are preserved under logarithmic
and monotonic transformations, relative gains alone cannot discriminate between model classes. The
discriminative empirical prediction therefore centers on the **absolute** effect.

```python
>>> from acceptance_gate import depth_effect, override
>>> weak = override(depth=0.5, habit=1.0, time_cost=0.5)
>>> strong = override(depth=4.0, habit=1.0, time_cost=0.5)
>>> for acc in (0.9, 0.1, 0.001):
...     print(acc, round(depth_effect(acc, 0.8, weak, strong), 6))
0.9 0.527191
0.1 0.058577
0.001 0.000586

```

As baseline acceptance decreases across orders of magnitude, the absolute behavioural gain from high
executive ability drops proportionally toward zero. Under an additive model, in contrast, executive
ability would provide a constant absolute boost regardless of defensive resistance.

Two honest caveats. First, the rival is not implemented here, so what you can run is one
side of the disagreement; a logistic over a weighted sum of the three conditions belongs
next to this, and it is the first thing on the list. Second, the naive rival, a plain
average of the three inputs, is not what anyone would fit: any three numbers satisfy
`abc <= min <= mean`, so beating that demonstrates arithmetic. The manuscript also
carries a two-condition rival, and it is that one, rather than the additive one, that
separates a condition of its own from a modulator of the override. Neither is in this
repository yet.

## The worked case

The following scenario illustrates an individual with high error detection and substantial modelling
capacity confronting feedback that directly threatens contingent self-worth:

```
$ python -m acceptance_gate.vignettes

case                                        det    acc    ovr        A  binds at
------------------------------------------------------------------------------------
able narcissist                           0.881  0.047  0.881   0.0368  acceptance
same man, both faculties removed          0.500  0.047  0.500   0.0119  acceptance
surgeon, 9am, operating theatre           0.881  0.881  0.924   0.7170  nothing; all three admit
surgeon, 3pm, at home                     0.881  0.047  0.924   0.0386  acceptance
quiet hint, settled routine               0.223  0.881  0.924   0.1813  detection
```

Even with strong detection and override capacities, the overall outcome is scaled by a factor of 3.1
relative to baseline ability, yet remains constrained below 0.04. Cognitive ability scales the
transmitted signal, but cannot bypass the bottleneck imposed by low acceptance.

The surgeon vignette models the same individual across two situations: detection and override
parameters remain identical, while the situation-specific threat to self-worth changes the
acceptance probability.

The first two rows are the manuscript's, to the digit. The surgeon is a scene from its
introduction, told without numbers; her parameters were chosen here so the scene could
be calculated. The last row is not in the paper at all. It exists because the other four
all bind at the same condition, which left the table making a claim about three ceilings
while only ever showing one of them do any work.

> **Units are arbitrary and illustrative.** They demonstrate an ordering, not a
> measurement, and none of them should be quoted as measured values. The manuscript
> explains at length why we decline to calibrate them.

## Install and run

```bash
git clone https://github.com/RealNevoEvo/acceptance-gate
cd acceptance-gate
pip install -e ".[test]"
pytest -q
```

**No runtime dependencies.** The model is a product of three numbers; anything more
would put someone else's code between a reader and the claim. Python 3.9 or newer,
standard library only.

## What the tests are for

They check what the model forbids. Each is named after the statement that would refute
it:

| Test | Refutes |
|---|---|
| `test_ability_multiplies_but_does_not_rescue` | that a closed gate can be compensated |
| `test_the_absolute_effect_vanishes_with_acceptance` | the additive account's prediction |
| `test_ability_does_not_enter_detection_or_acceptance` | that ability reaches the first two conditions, by argument or by call |
| `test_forecasting_depth_enters_quadratically` | a linear account of effort |
| `test_a_negative_forecast_buys_no_override` | that a square can be trusted with a sign |
| `test_a_product_is_not_a_minimum` | our own overstatement, that the smallest factor *is* the outcome |

The numbers in the prose are checked rather than promised, and the checking is narrower
than it sounds, so here is exactly what it covers. The worked example lives in doctests.
The table above is read out of this file by a test and compared with what `report()`
prints. The `>>>` blocks in this README run under pytest. On the explainer page, the
constants, the cost terms and the two printed results are read out of the JavaScript and
held against the package.

What is **not** covered: the rest of the explainer page's prose, and any number that
appears only in a sentence. An earlier version of this section claimed more than that.

## Cite

`CITATION.cff` is in the repository root; GitHub renders a "Cite this repository" button
from it. Please cite the manuscript for the model and this repository for the code.

## Sources this builds on

- **Detection:** Nieuwenhuis et al. (2001) on error monitoring without awareness;
  O'Connell et al. (2007) and Steinhauser & Yeung (2010) on the error positivity.
- **Acceptance:** Crocker & Wolfe (2001), *Contingencies of Self-Worth*, Psychological
  Review; Kernis (2003) on non-contingent self-esteem; Leary et al. (2007) on taking
  responsibility without self-blame.
- **Override:** Shenhav, Botvinick & Cohen (2013), *The Expected Value of Control*,
  Neuron. Control lapses because its value falls, not because a tank runs dry.
- **Testing a ceiling:** Dul (2016), *Necessary Condition Analysis*, Organizational
  Research Methods.

---

Nevzat Subasioglu · Independent Researcher, Switzerland · MIT licensed
