# EC2 Safe Cleanup (Dry Run)

This lab focuses on safely identifying EC2 instances that have been **stopped for more than 7 days**, without relying on AWS-provided stop timestamps or destructive automation.

The solution is intentionally conservative and designed to be run repeatedly without side effects.

---

## Problem Statement

AWS does **not** provide a reliable timestamp for when an EC2 instance was stopped.

The task is to:
- Detect EC2 instances that have been in the `stopped` state for more than 7 days
- Avoid relying on CloudTrail or parsing unreliable state transition strings
- Ensure protected instances are never acted upon
- Prevent accidental termination or modification of production workloads

---

## Constraints & Assumptions

- No destructive actions should occur (dry-run only)
- Instances tagged with `protected=true` must be skipped
- The script may be executed multiple times per day
- The solution must be idempotent
- Historical state must be tracked explicitly

---

## Design Approach

### Why AWS timestamps are insufficient

EC2 provides:
- `launch_time` — creation timestamp
- `state` — current state only

EC2 does **not** persist:
- When an instance was last stopped
- How long it has been stopped

Because of this, the system must record this information itself.

---

### Tag-Based State Tracking

When an instance is detected in the `stopped` state **without a tracking tag**:
- A `stopped_at` tag is added with the current UTC timestamp

When the instance transitions back to `running`:
- The `stopped_at` tag is removed

This makes the instance self-describing and allows accurate duration calculations.

---

## Safety Guardrails

- **Dry-run mode enabled by default**
- **Protected instances skipped**
- **No termination or stop actions performed**
- Safe to run repeatedly

---

## Tags Used

| Tag Key      | Description                                  |
|--------------|----------------------------------------------|
| `stopped_at` | ISO-8601 timestamp when stop was detected    |
| `protected`  | If set to `true`, instance is ignored        |

---

## Logic Overview

1. Fetch all EC2 instances
2. Skip instances tagged `protected=true`
3. If instance is `running`
   - Remove `stopped_at` tag if present
4. If instance is `stopped` and no `stopped_at` tag exists
   - Add `stopped_at` tag
5. If instance is `stopped` and `stopped_at` exists
   - Compare timestamp to current time
   - Flag if stopped for ≥ 7 days

---

## Example Output

```text
Instance i-0abc123 | state=stopped
  -> Stopped detected, tagged stopped_at

Instance i-0def456 | state=stopped
  -> DRY RUN: would delete (stopped 8 days)

Instance i-0xyz789 | state=running
  -> Running again, removed stopped_at tag