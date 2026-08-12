# H166 independent pair-conditioned operational-target challenge

Date: 2026-07-27

Disposition: `pass_with_scope`

## Independence

The challenge uses a standalone Node.js BigInt rational implementation. It
does not import the H165 Python producer or tests. It reconstructs routing and
tournament values from the constants fixed in the H165 protocol, then checks
agreement with the canonical result only after completing its own arithmetic.
It also reads the canonical H151 and H152 JSON records directly to retain the
upstream common-context boundary.

## Reconstructed result

- The edges \(3/4,1/4,3/4\) give the cycle \(0>1\), \(1>2\), \(2>0\).
- Choosing 0 on pair 01, 2 on pair 02, and 1 on pair 12 has exact value
  \(3/4\).
- Always choosing the lower-index member has value \(7/12\), for exact regret
  \(1/6\).
- All three uniform-reference tournament scores equal \(1/2\).
- H151's opposite common-context winners and \(1/3\) singleton regret floor
  remain intact, and H152 independently agrees.

## Semantic attacks

All eight attacks were rejected:

1. a tournament tie erases the pair-routing advantage;
2. a routing optimum identifies a unique global policy;
3. a comparative edge is a marginal task-success rate;
4. the future pair-specific context mechanism may change silently;
5. outcome-adaptive pair weights preserve the fixed target;
6. a routing value remains identified with a missing positive-weight edge;
7. a router may choose a policy outside the presented pair; and
8. a pair-routing comparison estimates an evaluator causal effect.

## Scope

The challenge independently supports only the target semantics for
same-mechanism pair choice and fixed-weight pair routing. It does not establish
a confidence procedure, common-context best policy, marginal success,
evaluator effect, transport, public-mechanism compliance, real-site
qualification, field authorization, or standalone paper novelty.

## Trace

- H165 protocol SHA-256:
  `c6e6821d826cb0aff5056e14e9c898d088dddda21e473db83ec743ae420c765a`
- H165 result SHA-256:
  `a3c8ab98e4779efa0372cf29b4da87537388545d54784189b957b520f9fb6a63`
- independent source SHA-256:
  `3d04bd686f1d41049303ca14a84e0e2eb6e306cde8e9c3469f5bb65a80c2b45d`
- validator SHA-256:
  `a461f4776926d23cb3e75cc7c148691fb738b3bf866246f139a7fb9050ab9a1d`
- independent result SHA-256:
  `274f08586fceb98c0f444581f543ce9694e67b4756f4aebda546310530a3dec0`

## Consequence

Use the pair-conditioned routing target as the explicit no-site fallback. Do
not translate it into a common-deployment ranking. The remaining next step is
to connect a real public assignment mechanism to the fixed routing target—or
honestly bound that applicability—while the common-context branch continues
through independent H164 challenge and real-site evidence.
