# SentinelPR Demo — Proving LLM Agents Catch What Static Analyzers Can't

This repository is an empirical test of a single claim:

> **Pattern-matching static analyzers (Semgrep, Bandit) cannot detect intent-level security vulnerabilities. An LLM agent can.**

It contains a small Flask app with a consistent, correct authorization pattern — then five pull requests, each introducing one *intent-level* ("Bucket 2") vulnerability. Each PR was reviewed by three tools: **Bandit**, **Semgrep**, and **[SentinelPR](https://github.com/Aryan2659/sentinelpr-)** (an agentic LLM security reviewer).

## Results

| PR | Vulnerability | OWASP | Bandit | Semgrep | SentinelPR |
|----|--------------|-------|--------|---------|------------|
| 1 | Admin endpoint missing authorization check | A01 Broken Access Control | ❌ | ❌ | ✅ |
| 2 | IDOR — order fetched without ownership check | A01 Broken Access Control | ❌ | ❌ | ✅ |
| 3 | Privilege escalation — `role` accepted from request body | A01 Broken Access Control | ❌ | ❌ | ✅ |
| 4 | Authentication bypass via flawed boolean logic | A07 Identification & Authentication Failures | ❌ | ❌ | ✅ |
| 5 | Business logic flaw — coupon redeemable unlimited times | A04 Insecure Design | ❌ | ❌ | ✅ |

**SentinelPR: 5/5. Bandit: 0/5. Semgrep: 0/5.**

Bandit and Semgrep were not silent — on every PR they correctly flagged the same two *pattern-level* ("Bucket 1") issues: a hardcoded `secret_key` and `debug=True`. That is exactly the point. They do what they are designed to do — match known-dangerous patterns — and the intent-level bug in each PR has no pattern to match.

## Why these bugs are invisible to pattern matching

Every vulnerability here shares one property: **the bug is the absence of code, or the wrong intent behind code that is individually valid.**

- A missing `@require_admin` decorator is not a pattern — it's a *gap*. There is nothing to match.
- An endpoint that fetches `order_id` without checking ownership uses entirely normal database calls. The vulnerability is the missing comparison, not any line that's present.
- `if role == "admin" or role != "banned"` is syntactically perfect. Only by reasoning about *what the check is supposed to do* can you see it grants access to everyone.

Static analyzers ask "does this code match a known-bad shape?" Intent-level review asks "does this code do what it should?" Only the second question catches these bugs.

## How SentinelPR caught them

SentinelPR is an agentic reviewer. For each PR it:

1. Reads the diff
2. **Investigates the rest of the repo with tools** (`read_file`, `search_code`, `list_directory`) — e.g. on PR 1 it searched for `require_admin`, found it on every other admin route, and flagged the new one for breaking the pattern
3. Passes each finding to a **verification agent** that tries to refute it using codebase evidence
4. Runs a **cross-file impact agent** to check for second-order effects

The multi-file investigation is what makes intent-level detection possible — the bug in PR 1 is only visible if you compare the new endpoint to its siblings.

---

## PR-by-PR detail

### PR 1 — Broken Access Control
A new `POST /admin/users/<id>/delete` endpoint was added with no `@require_admin` decorator, while every other admin route in the file has one.

**SentinelPR finding:**

<img width="1628" height="1666" alt="Screenshot 2026-05-14 191148" src="https://github.com/user-attachments/assets/bec5239d-b7a9-4f87-aca6-96d11869c7d1" />



**Bandit + Semgrep output** (flag only `secret_key` / `debug=True`, miss the access control bug):
<img width="2988" height="1750" alt="Screenshot 2026-05-14 184735" src="https://github.com/user-attachments/assets/4f4746c0-f402-411c-a3e2-698dab6f26b9" />
<img width="1982" height="1584" alt="Screenshot 2026-05-14 184802" src="https://github.com/user-attachments/assets/caba35d9-30b0-447c-a69a-8f3186f4b051" />




### PR 2 — IDOR
`GET /orders/<id>` is gated by `@login_required` but never checks that the order belongs to the requesting user. Any logged-in user can read any order.

**SentinelPR finding:**
<img width="1589" height="1660" alt="Screenshot 2026-05-14 191212" src="https://github.com/user-attachments/assets/8731af0b-1aee-428f-ab0a-e00b271405bc" />


**Bandit + Semgrep output:**
<img width="1824" height="1740" alt="Screenshot 2026-05-14 185214" src="https://github.com/user-attachments/assets/f8e706a7-4515-4997-af3d-1ddb039f6d49" />
<img width="3044" height="1744" alt="Screenshot 2026-05-14 184833" src="https://github.com/user-attachments/assets/e262fe8c-0fed-4bfd-a34b-17efeee0a4bc" />


### PR 3 — Privilege Escalation via Input
`POST /users/<id>/update` passes the entire request body into `update_user(**data)`. A regular user can send `{"role": "admin"}` and promote themselves — and update any user, not just their own account.

**SentinelPR finding:**
<img width="1587" height="1654" alt="Screenshot 2026-05-14 191236" src="https://github.com/user-attachments/assets/5c3528b9-722c-4fe9-8bc4-949661b3da97" />


**Bandit + Semgrep output:**
<img width="3066" height="1492" alt="Screenshot 2026-05-14 185334" src="https://github.com/user-attachments/assets/99293421-ef1d-4491-806a-7845a0be7101" />
<img width="3054" height="1622" alt="Screenshot 2026-05-14 185417" src="https://github.com/user-attachments/assets/9c355c36-9a42-4464-8223-c45530d08794" />


### PR 4 — Authentication Bypass via Logic Error
`GET /admin/revenue` contains a role check whose boolean logic does not match its stated intent — the condition is structured so that non-admin users pass it.

**SentinelPR finding:**
<img width="1581" height="1652" alt="Screenshot 2026-05-14 191301" src="https://github.com/user-attachments/assets/e2daa634-eeb3-4eb6-8cc2-78f51fbabc30" />




**Bandit + Semgrep output:**
<img width="3060" height="1492" alt="Screenshot 2026-05-14 185439" src="https://github.com/user-attachments/assets/d18f72d7-1c57-4509-a1e1-1ffb53d120d0" />
<img width="2488" height="1632" alt="Screenshot 2026-05-14 185454" src="https://github.com/user-attachments/assets/e66d4808-7e0a-44b0-995e-78d9bdd7ec2a" />


### PR 5 — Business Logic Flaw
`POST /coupons/<code>/redeem` adds the user to the coupon's `redeemed_by` set but never checks whether they're already in it. The same user can redeem one coupon unlimited times.

**SentinelPR finding:**
<img width="1601" height="1650" alt="Screenshot 2026-05-14 191322" src="https://github.com/user-attachments/assets/6fbb9be2-0e02-433b-80dd-711b18e88268" />


**Bandit + Semgrep output:**
<img width="3050" height="1498" alt="Screenshot 2026-05-14 185536" src="https://github.com/user-attachments/assets/5722fde9-8b78-49fb-8590-e7dacfe65c8f" />
<img width="3028" height="1590" alt="Screenshot 2026-05-14 185550" src="https://github.com/user-attachments/assets/bb127c28-5a5e-48e6-924b-5a6eb2620b4a" />

---

## Reproducing this

Each vulnerability lives on its own branch (`pr1-missing-admin-check`, `pr2-idor-order-access`, etc.), branched from a clean `main`.

```bash
git clone https://github.com/Aryan2659/sentinelpr-demo.git
cd sentinelpr-demo
git checkout pr1-missing-admin-check
bandit routes.py
semgrep --config=auto routes.py
```

SentinelPR's reviews are visible as inline comments on each pull request in this repository.

## Honest limitations

- This is a small, deliberately constructed test set — not a statistical benchmark. It demonstrates a capability gap; it does not quantify it.
- LLM review is non-deterministic and can hallucinate. SentinelPR mitigates this with a verification agent, but it is not eliminated.
- Static analyzers and SentinelPR are **complementary, not competitors.** Bandit and Semgrep catch Bucket 1 issues faster, cheaper, and more reliably than any LLM. The right setup runs both.

## What this is part of

SentinelPR — an agentic GitHub App that reviews pull requests for intent-level security vulnerabilities. Code and architecture: **https://github.com/Aryan2659/sentinelpr-**
