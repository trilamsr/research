# Review: H204 PhAIL achieved-first-state group balance

Date: 2026-07-28

## Disposition

**Pass as `no_material_group_mean_association_at_fixed_resolution`.**

Policy accounts for 0.00392 of remaining standardized seven-joint variance
after conditioning on UTC date, below its permutation median 0.00501
(upper-tail p=0.777). UTC date accounts for 0.01760 after conditioning on
policy, below its permutation median 0.02019 (p=0.811). The unadjusted policy
share is 0.00457 versus median 0.00489 (p=0.587). None approaches the joint
fixed requirements of p at most 0.01 and partial variance share at least
0.02.

Individual diagnostic group-mean spans were retained without post hoc
promotion. Policy mean spans range from 0.00150 to 0.01551 rad across joints.
UTC-date spans range from 0.00924 to 0.04318 rad. The prespecified
multivariate conditional date statistic places the aggregate shift below its
null median after accounting for 12 date degrees of freedom, so no individual
joint or date contrast was selected.

## Independent challenge

A separate implementation imports no producer module and uses SciPy GELSY
least squares, QR with column pivoting, and an independent Philox residual-
permutation stream. It reproduces all three observed partial variance shares
within `1.5e-16` and reaches the same classification with 9,999 permutations.
Its policy-conditional, date-conditional, and unadjusted-policy p-values are
0.782, 0.813, and 0.583. Four result/scope attacks are rejected.

Producer result SHA-256 is
`d03aba1badedfe0c64bdd03be74c6e1134c331fc496a012f38ec35a048a812aa`;
challenge result SHA-256 is
`dc93a6491d78bc0e707715ff6e926e21ba69f7a31591411ffd5029c99a9a24d4`.

## Consequence and scope

P2 may state that no material mean association is detected between achieved
first arm state and policy after UTC-date adjustment, or date after policy
adjustment, at the fixed resolution. This is not evidence of randomized
assignment, full initial-condition balance, exchangeability, RNG validity,
carryover absence, or performance validity. The tested vector excludes
commanded target, scene, object, tote, gripper, camera, calibration, robot
health, operator state, and unmeasured context.

No new public object was opened. Only H202 first joint values and fixed H187
policy/date fields were used; later state and all performance fields remained
sealed.
