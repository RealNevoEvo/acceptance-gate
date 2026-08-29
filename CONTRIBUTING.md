# Contributing

This is a small repository with one job, and most of what it needs is people trying
to break the claim rather than extend the code.

## Reporting a problem, asking a question

Open an issue at <https://github.com/RealNevoEvo/acceptance-gate/issues>. Two kinds
are especially welcome:

- **A number that does not match the manuscript.** Say which one, where it appears in
  the paper, and what the code returns. The tests are meant to catch this before you
  do; if they did not, that is a second bug.
- **A case the model gets wrong.** Describe the person and the situation in plain
  words first, then, if you can, as arguments to `detection`, `acceptance` and
  `override`. A case that the product handles badly and an additive account handles
  well is exactly what the manuscript says would count against it.

Questions about the model itself are fine as issues too. There is no mailing list.

## Changing the code

```bash
git clone https://github.com/RealNevoEvo/acceptance-gate
cd acceptance-gate
pip install -e ".[test]"
pytest -q
```

Pull requests should keep the test suite green and, if they touch a number, keep the
README and the explainer page in step; two tests will tell you if they are not.
Anything that changes what the model *says* needs a pointer to the sentence in the
manuscript it follows from. This code is a translation of the paper, not a place to
extend it.

Things that are welcome: a proper implementation of the additive rival, so the
discrimination test stops being one-sided; parameter-recovery checks; more worked
cases with their sources marked.

Things that will not be merged: the equations of motion (they belong to the companion
paper), any calibration of the units, and dependencies. The package is standard
library on purpose.

## Conduct

Be direct about the model and decent to the people. Disagreement with the claim is
the point of the repository; disagreement with a person is not.
