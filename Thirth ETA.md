




# Tirth ETA — Implementation Plan

## Context

We are building **Tirth ETA**, a web application that serves as an API layer for the **ThirthTrack** application. Its responsibilities:

1. **Provide ETA results** — compute and return estimated arrival times
2. **Proxy API calls** — forward requests to the ThirthTrack backend
3. **Redirect users** — send users to the main ThirthTrack application

The project directory (`D:\projects and repos\ETA tirth\`) is currently empty — this is a greenfield implementation.

---

## Architecture Overview

```
Client (Browser / Mobile)
        │
        ▼
┌─────────────────────┐
│   Tirth ETA App     │  ← This project (web app / API server)
│  - ETA endpoints    │
│  - Auth (Clerk)     │
│  - Redirect routes  │
│  - Proxy to Thirth  │
└────────┬────────────┘
         │  (API calls)
         ▼
┌─────────────────────┐
│  ThirthTrack Backend │  ← Existing application (separate repo/service)
│  - Core business logic│
│  - Tracking data     │
│  - User management   │
└─────────────────────┘
```

## Tech Stack

| Layer       | Choice              | Rationale                                      |
|-------------|---------------------|------------------------------------------------|
| Runtime     | Node.js (v18+)      | Consistent with your previous Clerk/Next.js projects |
| Framework   | Next.js 14+ (App Router) | SSR for redirect pages, API routes for ETA logic |
| Auth        | Clerk               | Already in your workflow; use `@clerk/nextjs`  |
| HTTP Client | `axios` or `fetch`  | For proxying calls to ThirthTrack backend       |
| Config      | `dotenv` / env vars | Manage ThirthTrack API URL, keys, etc.         |
| Deployment  | Vercel              | Matches your previous Next.js deployment pattern |

---

## Implementation Phases

### Phase 1: Project Scaffold (1–2 hours)

- [ ] Initialize Next.js project with TypeScript
- [ ] Set up Clerk authentication (`@clerk/nextjs`)
- [ ] Configure environment variables:
  - `THIRTHTRACK_API_URL` — base URL for ThirthTrack backend
  - `CLERK_SIGN_IN_URL` / `CLERK_SIGN_UP_URL` — auth routes
  - `NEXT_PUBLIC_APP_URL` — public-facing URL
- [ ] Basic folder structure:
  ```
  app/
    layout.tsx          ← root layout with Clerk provider
    page.tsx            ← landing / redirect page
    api/
      eta/
        route.ts        ← ETA computation endpoint
        proxy/
          route.ts      ← proxy to ThirthTrack
      auth/
        [...clerk]/     ← Clerk auth routes
  lib/
    thirthtrack.ts      ← helper: call ThirthTrack API
    eta.ts              ← helper: ETA calculation logic
  ```

### Phase 2: Auth & Redirect (2–3 hours)

- [ ] Set up Clerk middleware (`middleware.ts`) — protect API routes, allow public redirect pages
- [ ] Create a landing page (`app/page.tsx`) that:
  - Shows a brief intro / status
  - Has a CTA button redirecting to `https://thirthtrack.app` (or configured URL)
- [ ] Add sign-in / sign-up pages via Clerk
- [ ] Add a `/dashboard` route (protected) that shows ETA status for authenticated users

### Phase 3: ETA API Endpoints (3–4 hours)

- [ ] **`GET /api/eta`** — accepts query params (e.g., `?origin=...&destination=...`) and returns computed ETA
  - Validate input params
  - Call ThirthTrack API if needed for tracking data
  - Return JSON: `{ etaMinutes, distance, route, status }`
- [ ] **`POST /api/eta/compute`** — for complex ETA calculations (batch or with payload)
  - Accepts body with origin, destination, optional waypoints
  - Returns detailed ETA breakdown
- [ ] **Error handling** — consistent error responses with status codes
- [ ] **Rate limiting** — basic in-memory or `upstash-redis` rate limiter for API endpoints

### Phase 4: ThirthTrack Proxy (2–3 hours)

- [ ] **`GET /api/proxy/*`** — generic proxy route that forwards requests to ThirthTrack backend
  - Strips `/api/proxy/` prefix, prepends `THIRTHTRACK_API_URL`
  - Forwards headers (including auth tokens)
  - Returns ThirthTrack response as-is
- [ ] **`POST /api/proxy/*`** — same for POST/PUT/DELETE methods
- [ ] **Request/response logging** — log proxy calls for debugging
- [ ] **Timeout handling** — set a reasonable timeout (e.g., 10s) on upstream calls

### Phase 5: UI & Polish (2–3 hours)

- [ ] Minimal dashboard page showing:
  - User info (from Clerk)
  - Last ETA query result
  - Link to ThirthTrack app
- [ ] Responsive design (Tailwind CSS)
- [ ] Loading states and error toasts
- [ ] Meta tags for SEO on the landing page

### Phase 6: Testing & Deployment (1–2 hours)

- [ ] Unit tests for `lib/eta.ts` and `lib/thirthtrack.ts` (Jest or Vitest)
- [ ] API route tests (using `@playwright/test` or `vitest` with `msw`)
- [ ] Environment validation (`@t3-oss/env-nextjs` or similar)
- [ ] Deploy to Vercel
- [ ] Configure production environment variables in Vercel dashboard

---

## Key Files to Create

| File                              | Purpose                                      |
|-----------------------------------|----------------------------------------------|
| `app/layout.tsx`                  | Root layout with Clerk `<ClerkProvider>`     |
| `app/page.tsx`                    | Landing page with redirect to ThirthTrack    |
| `app/api/eta/route.ts`            | GET/POST ETA computation                     |
| `app/api/proxy/route.ts`          | Generic proxy to ThirthTrack backend         |
| `app/dashboard/page.tsx`          | User dashboard with ETA results              |
| `lib/thirthtrack.ts`              | Helper: call ThirthTrack API                 |
| `lib/eta.ts`                      | Helper: ETA calculation logic                |
| `middleware.ts`                   | Clerk auth middleware                        |
| `.env.example`                    | Template for environment variables           |
| `next.config.ts`                  | Next.js config (if custom headers/rewrites needed) |

---

## Verification

1. **Local dev**: `npm run dev` — verify Clerk auth flow, ETA endpoint returns correct data, proxy forwards to ThirthTrack
2. **API test**: Use `curl` or Postman to hit `/api/eta` and `/api/proxy/*` endpoints
3. **Auth flow**: Sign in via Clerk, verify protected routes work, redirect to ThirthTrack functions
4. **Deploy**: Push to Vercel, confirm all env vars are set, test production endpoints
5. **Integration**: Confirm Tirth ETA can successfully proxy a request to ThirthTrack and return a valid response

---

## Open Questions (resolve before Phase 1)

1. **ThirthTrack API base URL** — what is the current URL of the ThirthTrack backend?
2. **Auth model** — does ThirthTrack use Clerk too, or a different auth system? (If different, we need a token exchange flow.)
3. **ETA computation** — is ETA calculated client-side, server-side, or by ThirthTrack? (Plan assumes server-side.)
4. **Data schema** — what parameters does the ETA endpoint need? (origin/destination coordinates, vehicle type, etc.)
5. **Rate limits / quotas** — any limits on ThirthTrack API calls we need to respect?
