# Evolution Policy

## Runtime
- Runtime proposes changes only.
- Runtime cannot self-apply identity or policy mutations.

## Learner
- Learner generates candidate patches and evaluation notes.
- Learner cannot deploy directly.

## Governor
- Governor applies changes only when eval gates pass.
- Governor records evidence and rollback checkpoint for every apply.
