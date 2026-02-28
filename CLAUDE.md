# QB7 Modern — GitHub Pages

Private family posting board (Facebook-style social media page).

**Live URL**: https://leida-archer.github.io/QB7-MODERN/arc/index.htm

## Architecture

- **Single-page app**: All UI logic in `arc/index.htm` (HTML + inline JS)
- **Styling**: `arc/style.css` with CSS custom properties (`--border`, `--text-secondary`, etc.)
- **Service worker**: `arc/sw.js` — network-first strategy, caches static assets only
- **Data storage**: `localStorage` for family tree data, `sessionStorage` for logged-in user
- **No backend on GitHub Pages**: CGI/PHP endpoints (`msg_up.cgi`, `pic_up.php`, `del_posts.cgi`, `save_profile_pic.php`) exist but only function on the primary hosted server. Posts come from `epa.js` (not cached by SW).

## Key Files

| File | Purpose |
|------|---------|
| `arc/index.htm` | Main app — login, posts, profiles, family tree, sidebar |
| `arc/style.css` | All styles (v124) |
| `arc/sw.js` | Service worker (cache `qb7-v124`) |
| `arc/manifest.json` | PWA manifest (`start_url: "index.htm"`) |
| `arc/epa.js` | Post data (dynamic, not cached) |
| `arc/FacePics/` | Member profile photos |
| `MBG.jpg` | Background image (one level up from `arc/`) |

## GitHub Pages vs Local Dev

This repo is a **separate copy** from the local dev project (`/Users/archer/Desktop/QB7 Rework/site/`). The two have diverged — do NOT sync changes between them without explicit user instruction. Key differences:

| Feature | GitHub (`/tmp/QB7-MODERN/arc/`) | Local (`QB7 Rework/site/`) |
|---------|-------------------------------|---------------------------|
| Cache version | v124 | v122 |
| SW/manifest paths | Relative (`index.htm`, `style.css`) | Absolute (`/arc/index.htm`) |
| Family tree seeding | 9 default relationships seeded | No seeded relationships |
| SVG line CSS | Both `<path>` and `<line>` styled | Only `<path>` styled |
| Tree root | Always Joe (consistent layout) | Logged-in user as ego |
| Editor mini-tree | Direct family only (filtered) | Full connected graph |
| Logo href | `index.htm` | `/arc/index.htm` |

**Rule**: When user asks for GitHub-specific fixes, only edit `/tmp/QB7-MODERN/` — never touch the local project folder.

## Changes Made (GitHub Copy Only)

### 1. Path fixes for GitHub Pages (commit `4753549`)
GitHub Pages serves from `https://leida-archer.github.io/QB7-MODERN/arc/` — absolute paths like `/arc/index.htm` break because the repo name is part of the URL path.
- **sw.js**: Changed `STATIC_ASSETS` from absolute (`/arc/index.htm`) to relative (`index.htm`)
- **manifest.json**: Changed `start_url` from `"/arc/index.htm"` to `"index.htm"`
- **index.htm**: Changed logo `href` from `"/arc/index.htm"` to `"index.htm"`

### 2. Seeded default family relationships (commit `4753549`)
Family tree data lives in `localStorage` which is per-browser. New visitors saw an empty tree.
- `ftEnsureSeeded()` now creates 9 default relationships:
  - Jay & Alyson partnered
  - Jay & Alyson → Vivian (child)
  - Jay & Alyson → Colin (child)
  - Dad & Mom → Joe (child)
  - Dad & Mom → Jay (child)
- People are seeded from `_members` array + two non-member parents (Dad, Mom)
- IDs: `p_0`=Alyson, `p_5`=Colin, `p_20`=Jay, `p_22`=Joe, `p_31`=Vivian, `p_dad`=Dad, `p_mom`=Mom

### 3. SVG connector line visibility (commit `82ea2ae`)
The readonly tree CSS had a rule for `<path>` elements (parent→child curves) but was **missing the rule for `<line>` elements** (partner dashes). Both were nearly invisible on the light background.
- Added `.ft-readonly-tree .ft-tree-svg line` CSS rule
- Increased opacity from 0.4 to 0.55 for both `path` and `line`

### 4. Consistent tree root across all users (commit `1875849`)
Previously, the tree was built from the logged-in user as ego, producing different layouts for different users.
- Tree now always builds from Joe (`p_22`) as root for consistent layout
- Logged-in user is passed separately as `highlightId` for the card-box highlight
- Viewport centers on the highlighted user, not the root
- Functions modified: `ftRenderMiniTree`, `ftRenderAbsoluteTree`, `ftAbsTreeNode`, `ftRenderReadOnlyTree`

### 5. Direct family filter for editor mini-tree (commit `417f2f5`)
In Joe's family tree manager, selecting a member now shows only their direct family — not the entire connected graph.
- New function `ftGetDirectFamilySet(personId)` computes allowed IDs: grandparents, parents, siblings, children, grandchildren + all their partners
- `ftBuildClusters` accepts optional `allowedSet` — BFS only traverses allowed people
- `ftCalcTreeLayout` threads `allowedSet` through to cluster builder
- Phase 6 (disconnected people) skipped when filtering is active

## Family Tree Architecture

### Data Model
- **People**: `localStorage['qb7_ftree_people']` — JSON array of `{id, name, member, gender}`
- **Relationships**: `localStorage['qb7_ftree_rels']` — JSON array of `{id, type, a, b}`
  - Types: `parent_of` (a is parent of b), `partnered_with` (a & b are partners)
  - Siblings are inferred (shared parents), not stored directly

### Rendering Pipeline
1. `ftBuildClusters(egoId, allowedSet)` — BFS traversal, generation assignment, recursive tree building
2. `ftCalcClusterWidth()` — bottom-up width calculation
3. `ftPositionCluster()` — top-down coordinate assignment
4. `ftCalcTreeLayout()` — orchestrates above, centers on ego
5. `ftBuildSVGLines()` — cubic Bezier curves for parent→child, dashed lines for partners
6. `ftRenderAbsoluteTree()` — DOM assembly with SVG overlay + drag interaction

### Two Views
- **Readonly tree** (`ftRenderReadOnlyTree`): Visible to all users in the Tree tab. Full graph, rooted from Joe, highlights logged-in user. Clicking a node navigates to that member's profile.
- **Editor** (`ftRenderEditor`): Only accessible by Joe (admin). Shows relationship groups with add/remove buttons + a filtered mini-tree showing direct family only.

## Service Worker Notes
- Cache name: `qb7-v124` — bump version to force cache refresh
- `epa.js` is intentionally NOT cached (changes on every new post)
- CGI/PHP endpoints are excluded from fetch interception
- POST requests pass through unintercepted
- Network-first strategy: always tries server, falls back to cache on failure
