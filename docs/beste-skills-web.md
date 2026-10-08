# Beste Claude-Skills für Webentwicklung (Frontend + Backend)

Stand: **2026-10-08**. Ergänzt `docs/external-resources.md` (dort stehen die allgemeinen
Sammlungen obra/superpowers, mattpocock/skills, Anthropic-Plugins, trailofbits, wshobson/agents,
planning-with-files, brooks-lint, ponytail; die werden hier nicht neu bewertet). Diese Datei deckt nur
**Web** ab: React/Next.js, TypeScript/Node, CSS/Tailwind, Barrierefreiheit, Security, Datenbank,
Testing, Performance, SEO, Deployment.

**So wurde geprüft:**
- Jedes Repo per `git clone --depth 1` geklont, `SKILL.md` und Referenzdateien gelesen, Lizenzdatei im
  Root geprüft. „Letzte Aktivität“ = Datum des letzten Commits.
- Die GitHub-API und skills.sh waren aus der Sandbox gesperrt. Sterne stammen daher aus dem Suchindex
  bzw. von Aggregatoren (Stand Juli–Oktober 2026, gerundet) und sind mit „ca.“ markiert; „k. A.“ heißt:
  keine belastbare Zahl gefunden. Ersatz-Signal: offizieller Hersteller oder bekannter Autor.
- Bewertet wurde **Inhalt**, nicht Popularität: Ist der Skill versionsspezifisch (React 19 / Next 16 /
  Tailwind v4 / Node 22+), nennt er konkrete falsch-vs-richtig-Muster, hat er Checklisten? Reine
  „You are a senior expert“-Prompts wurden abgewertet.
- Vendoring-Regeln aus `research/vendorable.md`: nur MIT / Apache-2.0 / CC0, Lizenzdatei je Skill,
  Commit-Pin in `plugins/web-dev/UPSTREAM.md`.

**Ergebnis:** 12 Skills liegen jetzt als Plugin **`web-dev`** im Repo (`plugins/web-dev/skills/`). Alles
andere ist unten mit Installationsbefehl aufgeführt.

**Cloud oder lokal?**
- Alle 12 vendorten Skills sind reines Markdown und laufen auch in **Claude Code Web**, sobald sie in
  `.claude/skills/` des Projekts liegen: `scripts/install-skills.sh ~/MeinWebProjekt web-dev`
  (bzw. `.\scripts\install-skills.ps1 -Project C:\MeinWebProjekt -Plugin web-dev`).
- Lokal: `/plugin install web-dev@gamedev-skills`.
- Ausnahmen in der Cloud: `webapp-testing` braucht Python + `pip install playwright && playwright install
  chromium` (nur mit Netz); `dependency-verification` braucht Zugriff auf `registry.npmjs.org`;
  `core-web-vitals` und `wcag-accessibility` nutzen **optional** den Chrome-DevTools-MCP (nur lokal)
  und arbeiten sonst statisch am Quellcode.
- Alles mit `/plugin install …` oder MCP (Chrome DevTools, playwright-cli, Cloudflare, Prisma) läuft
  **nur lokal**.

---

## Rangliste

| Rang | Skill / Sammlung | URL | Lizenz | Sterne / Signal | Letzte Aktivität | Welche Claude-Schwäche es behebt | Installation | Verdikt |
| :- | :- | :- | :- | :- | :- | :- | :- | :- |
| 1 | **Vercel: `vercel-react-best-practices`** (70 Regeln, 8 Kategorien) | https://github.com/vercel-labs/agent-skills | MIT (README + Frontmatter, keine LICENSE-Datei) | ca. 30k★, >680k Installs auf skills.sh; offiziell Vercel | 2026-08-28 | Sequenzielle `await`-Wasserfälle, Barrel-Imports und Bundle-Größe, Hydration-Flackern bei localStorage/Theme, unauthentifizierte Server Actions, unnötige Re-Renders, `&&`-Rendering-Fallen | **im Repo als Plugin `web-dev`**; Original: `npx skills add vercel-labs/agent-skills --skill vercel-react-best-practices` | Pflicht für jedes React/Next-Projekt. Jede Regel hat „Incorrect / Correct“-Code. |
| 2 | **pproenca/dot-skills: `react` → `react-19-best-practices`, `nextjs` → `nextjs-16-app-router`, `tailwind` → `tailwind-v4-best-practices`** (49 / 45 / 44 Regeln) | https://github.com/pproenca/dot-skills | MIT | k. A. (bei skills.sh gelistet); Einzelautor, sehr systematisch | 2026-08-15 | Claude schreibt React-18-Idiome (`forwardRef`, `<Context.Provider>`, `useFormState`, `useEffect`+`fetch`), setzt `'use client'` zu hoch, erzeugt Hydration-Mismatches; Next 15-Muster statt Next 16 (`'use cache'`, `proxy.ts` statt `middleware.ts`, `revalidateTag` mit `cacheLife`); Tailwind-v3-`tailwind.config.js` statt v4 CSS-first (`@theme`, `@import "tailwindcss"`, Dark Mode per `@custom-variant`) | **im Repo (3 Skills)**; Rest: `npx skills add pproenca/dot-skills --skill typescript` (auch `zod`, `vitest`, `react-hook-form`, `playwright`, `shadcn`, `tanstack-query`) | Die gründlichsten versionsspezifischen Regelwerke, die ich gefunden habe. Jede Regel nennt „Shapes to recognize“ (getarnte Varianten des Fehlers) und hat ein Review-Verfahren für ganze Repos. Metadaten: React 19.2 (Mai 2026), Next 16 und Tailwind v4 (Januar 2026). |
| 3 | **Addy Osmani: web-quality-skills** (`accessibility` → `wcag-accessibility`, `core-web-vitals`, dazu `performance`, `seo`, `best-practices`, `web-quality-audit`) | https://github.com/addyosmani/web-quality-skills | MIT | k. A. (221 Forks); Autor aus dem Chrome-Team | 2026-08-24 | ARIA auf `<div>` statt nativer Elemente, fehlende Tastaturbedienung und Fokus-Styles, Kontrast, Fehlermeldungen nur per Farbe, WCAG-2.2-Neuerungen (Target Size 24 px, Focus not obscured, Redundant Entry, Accessible Authentication); LCP/INP/CLS mit Mess-Workflow (Feld vs. Labor) statt Raten | **im Repo (2 Skills)**; Rest: `npx skills add addyosmani/web-quality-skills` | Beste a11y- und CWV-Skills. Tabellen, Checklisten, falsch/richtig-HTML. Nutzen Lighthouse/Chrome-MCP, wenn vorhanden, sonst statisch. |
| 4 | **Addy Osmani: agent-skills → `security-and-hardening`** (dazu `frontend-ui-engineering`, `performance-optimization`, `api-and-interface-design`, `test-driven-development`) | https://github.com/addyosmani/agent-skills | MIT | ca. 72k★ | 2026-10-03 | XSS/Injection, CSRF über Cookie-Flags, CORS `*` mit Credentials, SSRF bei nutzergesteuerten URLs, Tokens in localStorage, Secrets im Repo, fehlendes Rate Limiting, Supply-Chain (`npm audit`, Install-Scripts), LLM-Output als Input, Datenschutz/GDPR | **im Repo (1 Skill)**; ganze Sammlung: `/plugin marketplace add addyosmani/agent-skills` | Threat-Model-zuerst, Always/Ask/Never-Listen, Red Flags, Verifikations-Checkliste; `references/hardening-patterns.md` hat den Code. Deckt mehr ab als jede OWASP-Prompt-Sammlung. |
| 5 | **Anthropic: `webapp-testing`** (dazu `frontend-design`, `web-artifacts-builder`) | https://github.com/anthropics/skills | Apache-2.0 | ca. 180k★ (Repo); offiziell | 2026-10-05 | Claude sagt „fertig“, ohne die UI im Browser gesehen zu haben; DOM vor `networkidle` inspizieren | **im Repo (`webapp-testing`)**; `frontend-design`: `/plugin install frontend-design@claude-plugins-official` | Kleiner Python-Playwright-Skill mit `with_server.py` (startet Dev-Server, führt Script aus, beendet). Ideal für „prüf das wirklich“. `frontend-design` ist gegen die generische KI-Optik (lila Gradients, `rounded-2xl` überall). |
| 6 | **TestDino: playwright-skill → `playwright-core`** (47 Guides; dazu `ci`, `pom`, `migration`, `playwright-cli`) | https://github.com/testdino-hq/playwright-skill | MIT | ca. 340★ | 2026-09-06 | `page.waitForTimeout()`, CSS/XPath statt `getByRole`, nicht-retrying Assertions, geteilter Test-State, Auth-Login in jedem Test, Flaky-Tests ohne Taxonomie | **im Repo (`playwright-core`)**; Rest: `npx skills add testdino-hq/playwright-skill` | `flaky-tests.md` (Taxonomie + Diagnosebaum), `common-pitfalls.md` (20 Fehler mit Fix), `error-index.md` (Fehlermeldung → Ursache) passen genau zu unserem Repo-Format. Playwright 1.63 geprüft. |
| 7 | **Supabase: `supabase-postgres-best-practices`** (34 Regeln) | https://github.com/supabase/agent-skills | MIT | ca. 2–5k★ (Aggregatoren uneins); offiziell Supabase | 2026-10-02 | N+1-Queries, fehlende Indizes auf Fremdschlüsseln, falsche Datentypen/Primärschlüssel, Offset-Pagination, lange Transaktionen und Deadlocks, Connection-Pooling, RLS-Performance | **im Repo** | Gilt für jedes Postgres, nicht nur Supabase. SQL falsch/richtig mit EXPLAIN. Für MySQL/SQLite nur teilweise übertragbar. |
| 8 | **Matteo Collina: `node` → `nodejs-best-practices`** (dazu `fastify`, `typescript-magician`, `oauth`) | https://github.com/mcollina/skills | MIT | k. A.; Autor ist Node.js-TSC-Mitglied und Fastify-Erfinder | 2026-10-03 | Claude nutzt `ts-node`/`tsx` statt Type Stripping (Node 22.6+), `.then`-Ketten, unbegrenzte Parallelität, kein `unhandledRejection`-Handler, kein Graceful Shutdown, `.pipe()` ohne Backpressure, hängende `node --test`-Läufe | **im Repo**; Rest: `npx skills add mcollina/skills` | Kompakt (94 Zeilen + 15 Regeln), direkt aus Node-Core-Wissen. Für Express-Projekte trotzdem nützlich; Fastify-Skill separat. |
| 9 | **athola/claude-night-market: `dependency-verification`** | https://github.com/athola/claude-night-market | MIT | klein (zweistellige Installs auf skills.sh) | 2026-10-01 | **Erfundene npm/PyPI-Pakete (Slopsquatting)**: Paketname vor `npm install` gegen `registry.npmjs.org` prüfen, Typosquats (`reqeusts`) erkennen | **im Repo** (ohne den Upstream-Hook) | Einziger brauchbare Skill zu diesem Thema. Zitiert die Studie (5–22 % halluzinierte Pakete). Der Hook `guard_package_hallucination.py` hängt am ganzen `imbue`-Plugin; manuelle Prüfung reicht. |
| 10 | **Microsoft: `playwright-cli`-Skill** | https://github.com/microsoft/playwright-cli | Apache-2.0 | offiziell Microsoft | 2026-09-28 | Browser steuern, Screenshots, Traces, Request-Mocking per CLI statt MCP (spart Kontext) | `/plugin marketplace add microsoft/playwright-cli`, dann `/plugin install playwright-cli`; oder `playwright-cli install --skills` | Lokal erste Wahl, um Claude wirklich klicken zu lassen. Braucht das Binary, deshalb nicht kopiert. |
| 11 | **Google: Chrome DevTools MCP Skills** (`a11y-debugging`, `debug-optimize-lcp`, `memory-leak-debugging`, `cookie-debugging`) | https://github.com/ChromeDevTools/chrome-devtools-mcp | Apache-2.0 | offiziell Chrome-Team | 2026-10-08 | a11y-Tree statt DOM lesen, Lighthouse-Audit mit fehlgeschlagenen Knoten, LCP-Trace-Insights, Speicherlecks | `/plugin install chrome-devtools-mcp@claude-plugins-official` | Nur mit laufendem Chrome. Ergänzt Rang 3 (die Addy-Osmani-Skills rufen genau diese Tools auf). |
| 12 | **ibelick/ui-skills** (`fixing-accessibility`, `fixing-motion-performance`, `fixing-metadata`, `baseline-ui`, `improve-ui`, `create-design-md`) | https://github.com/ibelick/ui-skills | MIT | Autor von motion-primitives; in mehreren Aggregatoren übernommen | 2026-10-07 | „AI-Slop“-UI (Abstände, Hierarchie), Animations-Jank (Layout-Thrashing, `blur`, Scroll-Linked), fehlende OG/Canonical/JSON-LD | `npx skills add ibelick/ui-skills` oder `npx ui-skills` | Kurz (85–150 Zeilen), regelbasiert, gut als Review-Pass. Überlappt mit Rang 3 bei a11y, daher nicht zusätzlich kopiert. |
| 13 | **dembrandt/dembrandt-skills** (`color-mode-and-theme`, `loading-states-and-perceived-performance`, `modal-and-overlay-patterns`, `performance-and-web-vitals`, 25 Skills) | https://github.com/dembrandt/dembrandt-skills | MIT | k. A. | 2026-10-08 | **Dark Mode** falsch (reines `#000`, gesättigte Markenfarben, Flächen per Schatten statt Helligkeit, Kontrast ungeprüft), Modal/Drawer-Auswahl, Skeleton vs. Spinner | `npx skills add dembrandt/dembrandt-skills` | Inhaltlich gut und konkret, aber Design- statt Code-Skills; Frontmatter hat `retrieval`-Keys (vor claude.ai-Upload entfernen). |
| 14 | **secondsky/claude-skills** (ca. 200 Themen-Plugins: `xss-prevention`, `csrf-protection`, `session-management`, `security-headers-configuration`, `api-error-handling`, `api-pagination`, `react-hook-form-zod`, `dependency-upgrade`, `internationalization-i18n`, `tanstack-query`, `bun`, Cloudflare …) | https://github.com/secondsky/claude-skills | MIT | ca. 200★ | 2026-09-26 | Ein Plugin pro Thema, jeweils 80–700 Zeilen mit Code | `/plugin marketplace add secondsky/claude-skills`, dann z. B. `/plugin install xss-prevention@claude-skills` | Brauchbar als Nachschlagewerk, überlappt aber mit Rang 4. Gezielt einzelne Plugins installieren. |
| 15 | **Cloudflare: `web-perf`, `workers-best-practices`, `nextjs-on-cloudflare`** | https://github.com/cloudflare/skills | Apache-2.0 | offiziell | 2026-10-08 | Veraltetes Wissen: Skill zwingt zu „Retrieval over pre-training“ (Doku nachlesen statt raten) | `/plugin install cloudflare@claude-plugins-official` | Nur relevant, wenn auf Cloudflare deployt wird. |
| 16 | **Prisma: prisma/skills** (`prisma-orm-setup`, `prisma-client-api`, `prisma-upgrade-v7` …) | https://github.com/prisma/skills | MIT | offiziell | 2026-10-01 | Prisma 6/7/8 verwechselt; Versionswahl vor Setup | `npx skills add prisma/skills`; MCP: `/plugin install prisma@claude-plugins-official` | Gut, aber ORM-spezifisch. Nur bei Prisma-Einsatz. |
| 17 | **ofershap/drizzle-best-practices** | https://github.com/ofershap/drizzle-best-practices | MIT | klein | 2026-02-20 | „Agents verwechseln Drizzle mit Prisma“: Schema-Syntax, `relations()`, Migrations | `npx skills add ofershap/drizzle-best-practices` | 291 Zeilen falsch/richtig, aber seit Februar ohne Update. |
| 18 | **Jeffallan/claude-skills** (`react-expert`, `nextjs-developer`, `typescript-pro`, `playwright-expert`, `secure-code-guardian`, `postgres-pro`, `api-designer`) | https://github.com/Jeffallan/claude-skills | MIT | ca. 12k★ | 2026-10-03 | Workflow-Schritte mit Validierung (`tsc --noEmit`, `next build`) | `/plugin marketplace add jeffallan/claude-skills` | Persona-Stil („Senior React specialist“), Next.js-14-zentriert. Zweite Wahl hinter Rang 1–2. |
| 19 | **wshobson/agents** (`wcag-audit-patterns`, `typescript-advanced-types`, `nodejs-backend-patterns`, `javascript-testing-patterns`, `postgresql-table-design`, `nextjs-app-router-patterns`) | https://github.com/wshobson/agents | MIT | ca. 40k★ | 2026-10-04 | Breite Abdeckung, aber allgemein gehalten | siehe `external-resources.md` (`claude-code-workflows`) | Schon bekannt; die Web-Skills sind kürzer und älter (Next 14) als Rang 1–2. |
| 20 | **omer-metin/skills-for-antigravity** (`security-owasp`, `nextjs-app-router`, `tailwind-css`, `accessibility`, `forms-validation`, `i18n`, `error-handling`, `caching-patterns`, `database-migrations`, `docker` …) | https://github.com/omer-metin/skills-for-antigravity | Apache-2.0 | ca. 120★ | 2026-01-22 | Pro Thema `references/patterns.md`, `sharp_edges.md`, `validations.md` | `npx skills add omer-metin/skills-for-antigravity --skill i18n` | Die `SKILL.md`s sind Rollen-Prompts (30–56 Zeilen), die Substanz steckt in den Referenzen. Seit Januar inaktiv. Nur als Ideenquelle für Lücken (i18n, Forms, Docker). |

**Hinweis zu Next.js:** Vercels frühere Skills `next-best-practices` und `next-upgrade` (Repo
`vercel-labs/next-skills`) gibt es **nicht mehr**. Seit Next.js 16.3 erzeugt `next dev` eine
`AGENTS.md`/`CLAUDE.md` mit versionsgenauen Docs (`next/dist/docs/`); bei älteren Versionen
`npx @next/codemod@canary agents-md`. Die verbleibenden Workflow-Skills liegen in
https://github.com/vercel/next.js/tree/canary/skills (`npx skills add vercel/next.js`). Deshalb ist
der dot-skills-Next-16-Skill (Rang 2) unsere Next-Quelle im Repo.

---

## Was ich bewusst nicht aufgenommen habe

- **Vercel `web-design-guidelines`**: lädt die Regeln zur Laufzeit per WebFetch von GitHub
  (`vercel-labs/web-interface-guidelines`); in Cloud-Sessions oft gesperrt, Inhalt nicht im Skill.
  **`vercel-optimize`** braucht Vercel-Metriken und Scripts. **`composition-patterns`** und
  **`react-view-transitions`** sind gut, überlappen aber mit Rang 2 bzw. sind Nische
  (`npx skills add vercel-labs/agent-skills --skill vercel-composition-patterns`).
- **dot-skills `typescript`, `zod`, `vitest`, `react-hook-form`, `playwright`**: gleiche Qualität wie die
  drei übernommenen, aber Platzlimit (8–12 Skills). Bei Bedarf nachziehen; `playwright` dort ist
  Next.js-spezifisch, `playwright-core` (Rang 6) allgemeiner.
- **sickn33/antigravity-awesome-skills** (ca. 44k★) und **tech-leads-club/agent-skills**: Aggregatoren.
  Viele Skills sind Kopien (Vercel, ibelick, Addy Osmani, OpenAI). Bei sickn33 stehen Inhalte unter
  **CC BY 4.0** (`LICENSE-CONTENT`). Immer zur Originalquelle gehen.
- **Chrome DevTools MCP, playwright-cli, Cloudflare, Prisma-MCP**: brauchen Binary/MCP/laufenden
  Browser, deshalb installieren statt kopieren.
- **lackeyjb/playwright-skill** (MIT): Executor `run.js` + eigene `node_modules`; `webapp-testing` ist
  schlanker. **garrytan/gstack** (`cso`, `benchmark`, `canary`, MIT): Framework mit eigenem
  Browser-Tool, nur komplett sinnvoll.
- **ehmo/platform-design-skills `web`** (MIT, WCAG 2.2 + MDN, 300+ Regeln): 1.454 Zeilen in einer
  `SKILL.md`, verstößt gegen unser 500-Zeilen-Limit; Rang 3 deckt das Thema kompakter ab.
- **openai/skills** (`security-best-practices`, `playwright`, `frontend-skill`): Lizenz je Skill in
  `LICENSE.txt`, auf Codex zugeschnitten; nicht geprüft, ob Claude-Code-Tools passen.
- **Ohne Lizenzdatei, daher nicht kopierbar:** mrgoonie/claudekit-skills (`web-frameworks`),
  neversight/learn-skills.dev, bg-szy/TOP-SKILLS (`accessibility-auditor`), ranbot-ai.
  **trailofbits/skills** bleibt CC BY-SA (nur installieren).
- **Registry-Skills** wie claudskills.com `nextjs-web`, `senior-frontend`, `wcag`, `accessibility-mode`:
  meist „You are an expert“-Prompts ohne Versionsbezug oder Code.

---

## Bekannte Schwächen ohne guten Skill (zum Selberschreiben)

Für diese Punkte habe ich keinen Skill gefunden, der unserem Format entspricht (Fehler → Ursache →
Fix, falsch/richtig-Code, versionsgenau). Teilabdeckung in Klammern.

1. **Datum, Zeitzonen, DST**: UTC speichern, `Intl.DateTimeFormat`/`Temporal`, `date-fns-tz`,
   Server/Client-Zeitzonen-Mismatch als Hydration-Fehler, `new Date('2026-03-01')`-Fallen. Gefunden
   wurden nur „führe `date` aus“-Skills (hodgesmr/temporal-awareness) und ein .NET-Skill.
2. **i18n**: next-intl / react-i18next, ICU-Pluralisierung, RTL, `lang`-Attribut, Routing per Locale.
   (omer-metin `i18n` 32 Zeilen + Referenzen; secondsky `internationalization-i18n` 101 Zeilen, beide
   ungeprüft.)
3. **Async/Race Conditions im Frontend**: Stale Closures, `AbortController` bei Suchfeldern,
   Doppel-Submits, Out-of-order-Responses, Optimistic-Update-Konflikte. (Einzelne Regeln in Rang 1–2.)
4. **Formulare Ende-zu-Ende**: Server- und Client-Validierung mit Zod, Fehler barrierefrei anzeigen
   (`aria-describedby`, Fokus auf ersten Fehler), progressive Enhancement, Datei-Uploads. (Teile in
   `react-19-best-practices` 3.x, `wcag-accessibility` 3.3, dot-skills `react-hook-form`/`zod`.)
5. **REST-API-Design und Fehler-Contracts**: Statuscodes, einheitliches Error-Shape, Idempotency-Keys,
   Cursor-Pagination, Versionierung. (Addy Osmani `api-and-interface-design` 367 Zeilen wäre der
   Kandidat; secondsky `api-error-handling`/`api-pagination`.)
6. **Datenbank-Migrationen**: Expand/Contract ohne Downtime, Backfills, Migrationen mit Drizzle/Prisma
   in CI. (Supabase deckt Schema/Indizes, nicht die Migrationsstrategie.)
7. **HTTP-Caching**: `Cache-Control`, `ETag`, `stale-while-revalidate`, CDN vs. Next-`'use cache'`,
   Cache-Invalidierung. (Nur Next-Cache in Rang 2.)
8. **Deployment, Env-Config, Docker für Node/Next**: Multi-Stage-Dockerfile, non-root, `output:
   'standalone'`, `NEXT_PUBLIC_*`-Leaks, Env-Validierung mit Zod beim Start, Health-Checks. (omer-metin
   `docker`, dot-skills `dockerfile-optimise` experimental, secondsky `health-check-endpoints`,
   ungeprüft.)
9. **Reines CSS (ohne Tailwind)**: Grid/Flex-Fallen, Container Queries, logische Properties,
   `prefers-color-scheme` ohne Theme-Flash, Scroll-Lock bei Modals, Safe-Area. (Tailwind-Skill deckt
   die v4-Seite, dembrandt `color-mode-and-theme` die Design-Seite.)
10. **Hydration-Fehlertabelle**: „Text content does not match server-rendered HTML“, „Hydration failed
    because the initial UI…“, `useLayoutEffect`-Warnung → Ursache → Fix. Regeln existieren (Rang 1–2),
    aber keine Fehlermeldungs-Tabelle wie in unseren Gamedev-Skills.
11. **Vite-spezifisch**: `import.meta.env`, Bundle-Analyse (`rollup-plugin-visualizer`), Chunking,
    Env-Prefix `VITE_`. (dot-skills `vite` nur experimental.)
12. **Auth/Session für SPAs vs. SSR**: Cookie- vs. Bearer-Token, Refresh-Rotation, CSRF bei SameSite,
    Better Auth / Auth.js-Fallen. (Teile in Rang 4; Better-Auth-Skills nur über das UI-Companion-Projekt.)
13. **Performance in Cloud-Sessions**: ohne Browser lassen sich Core Web Vitals nur statisch schätzen;
    ein Skill, der Lighthouse-CI (`@lhci/cli`) headless in der VM fährt, fehlt.

---

## Vendorte Skills im Überblick (`plugins/web-dev`)

| Skill | Quelle | Lizenz | Kerninhalt |
| :- | :- | :- | :- |
| `vercel-react-best-practices` | vercel-labs/agent-skills | MIT | 70 Performance-Regeln React/Next (Wasserfälle, Bundle, Server, Re-Render, Hydration) |
| `react-19-best-practices` | pproenca/dot-skills `react` | MIT | 49 Regeln React 19.2: RSC-Grenzen, Actions/Forms, `use()`, Effects, Compiler, Repo-Review-Verfahren |
| `nextjs-16-app-router` | pproenca/dot-skills `nextjs` | MIT | 45 Regeln Next 16: `'use cache'`, `proxy.ts`, Server Actions, Streaming, Metadata, `'use client'` |
| `tailwind-v4-best-practices` | pproenca/dot-skills `tailwind` | MIT | 44 Regeln Tailwind v4: CSS-first, `@theme`, Dark Mode, Container Queries, Bundle |
| `wcag-accessibility` | addyosmani/web-quality-skills `accessibility` | MIT | WCAG 2.2 POUR, ARIA, Tastatur, Fokus, Formulare, Testing-Checkliste |
| `core-web-vitals` | addyosmani/web-quality-skills | MIT | LCP/INP/CLS mit Mess-Workflow (CrUX, Trace, RUM) und Fixes |
| `security-and-hardening` | addyosmani/agent-skills | MIT | OWASP-Härtung: Threat Model, Injection/XSS/CSRF/SSRF, Sessions, Headers, Supply-Chain, LLM, Privacy |
| `webapp-testing` | anthropics/skills | Apache-2.0 | Lokale Web-App mit Python-Playwright prüfen, Server-Lifecycle-Script |
| `playwright-core` | testdino-hq/playwright-skill `core` | MIT | 47 Playwright-Guides: Locators, Assertions, Fixtures, Auth, Mocking, Flaky-Tests, Fehlerindex |
| `dependency-verification` | athola/claude-night-market | MIT | Paketnamen vor Installation gegen Registry prüfen (Slopsquatting) |
| `supabase-postgres-best-practices` | supabase/agent-skills | MIT | 34 Postgres-Regeln: Indizes, N+1, Pooling, Locks, RLS, Schema |
| `nodejs-best-practices` | mcollina/skills `node` | MIT | Node 22+ Type Stripping, Async, Fehler, Streams, Shutdown, Tests, Profiling |

Nicht alle zwölf in jedes Projekt laden: für ein Vite-React-SPA reichen z. B.
`vercel-react-best-practices`, `react-19-best-practices`, `tailwind-v4-best-practices`,
`wcag-accessibility`, `security-and-hardening`, `playwright-core`; `nextjs-16-app-router`,
`supabase-postgres-best-practices` und `nodejs-best-practices` nur bei Bedarf. Quellen und Commit-Pins:
`plugins/web-dev/UPSTREAM.md`.
