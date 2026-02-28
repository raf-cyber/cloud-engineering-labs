# S3 Public Exposure Detector (Logic-Only / Dry Run)

This lab focuses on **detecting potential public exposure of S3 buckets** using AWS best practices.  
The goal is to identify misconfigurations in a **safe, read-only, dry-run manner**, without modifying any buckets.

---

## Problem Statement

Publicly exposed S3 buckets can lead to **data leaks, compliance violations, and security incidents**.

The task is to:

- Detect S3 buckets that may be publicly accessible
- Evaluate all layers of AWS controls (Public Access Block, ACLs, bucket policies)
- Provide a **clear explanation** of the reason for potential exposure
- Avoid destructive operations entirely

---

## Constraints & Assumptions

- No bucket modifications or deletions
- Script must handle missing configurations gracefully
- Must produce **human-readable output**
- Designed for repeated execution without side effects
- Dry-run only; no actual network exposure testing

---

## Design Approach

S3 bucket exposure is evaluated in **three layers**:

1. **Public Access Block (BPA)**  
   AWS control to globally restrict public access.
   - Fully restrictive: bucket considered private
   - Partially restrictive / missing: possible exposure

2. **Bucket ACLs**  
   Legacy mechanism controlling access per grantee.
   - Grants to `AllUsers` or `AuthenticatedUsers` indicate public access

3. **Bucket Policy**  
   Policies can override ACLs and BPA.
   - Existence of a policy is flagged for manual inspection

> A bucket is considered potentially public if **any layer allows access**.

---

## Implementation Overview

### Functions

| Function                                 | Purpose                                                   |
| ---------------------------------------- | --------------------------------------------------------- |
| `check_public_access_block(bucket_name)` | Detects if BPA fully restricts public access              |
| `check_bucket_acl(bucket_name)`          | Detects ACL grants that allow public access               |
| `check_bucket_policy(bucket_name)`       | Checks if a bucket policy exists (requires manual review) |

### Evaluation Flow

1. List all S3 buckets
2. Evaluate Public Access Block
3. Evaluate ACLs
4. Evaluate Bucket Policy
5. Aggregate results and report **why** each bucket is flagged

---

## Example Output

```text
Bucket: my-company-data
Potential public exposure
 - Public Access Block is not fully restrictive
 - Public ACL detected
 - Bucket policy exists (manual inspection required)

Bucket: internal-logs
Bucket is not publicly accessible
```
