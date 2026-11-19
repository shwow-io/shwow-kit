# Reading other repos

Evidence about a repo comes from its latest code: the remote's default branch, fetched now. Local checkouts, notes, docs, earlier answers and package caches are leads, because they go stale. Check each one against the latest code before relying on it.

## Find

1. Collect what names the related repos: the brief's repos, the user's words, package references, API clients, service URLs, config, and contract names (endpoint paths, event and message types, package names).
2. Search the code host for those names across the whole org. The current repo's remote URL gives the host and org. Use a CLI, the host's REST API, or an MCP server:
   - GitHub: `gh search code`.
   - Azure DevOps: `az devops invoke --area search --resource codesearchresults --http-method POST --in-file <body.json>` with `{"searchText": "...", "$top": 100}`. `az repos` has no code search.
   - GitLab: `glab api "projects/:id/search?scope=blobs&search=..."` or the group search endpoint.
   - No search available: list the org's repos (`gh repo list`, `az repos list`) and shallow-clone the ones whose name or description could relate.
3. Done when every repo the work touches is named (`name@sha`, plus the remote URL when the host or org differs), and every contract it touches has its producer and consumers named, or a search showed there are none.

## Read

1. The repo being changed is read at the change (the landing branch, or the plan's base). Every other repo is read at its latest, as below.
2. Default branch: `git ls-remote --symref <url> HEAD`.
3. Local clone, matched by remote URL, not folder name: `git fetch <remote> <branch>`, then read that commit (`git rev-parse FETCH_HEAD`, `git show <sha>:<path>`, `git grep <pattern> <sha>`). Leave its checkout and branch as they are; the user may be mid-work there.
4. Not cloned: one or two files through the host's API. More than that: `git clone --depth 1` into a temp directory outside every repo.
5. What runs can lag what's merged. For a deployed service, read the deployed version or tag when tooling shows it. For client apps (mobile, desktop, SDKs), read every version still installed, found from release tags and telemetry. Say which versions you read.

## Cite

- Reads as `<repo>@<short sha>:<path>`.
- A repo you can't reach (no access, tool missing, signed out): name it, say why, and ask the user. Suggest the sign-in command. Leave its contents unclaimed.
