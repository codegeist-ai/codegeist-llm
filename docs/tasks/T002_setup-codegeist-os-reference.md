# Set Up Codegeist OS Reference

- **ID:** T002
- **Type:** implementation
- **Parent:** None
- **Status:** blocked

## Goal

Create or verify the first-party `codegeist-os` repository on the primary Gitea
host and attach it to this repository as the `refs/codegeist-os/` Git submodule.

## Context

Codegeist OS owns operating-system schemas, tools, policy, permissions, and
actions. Keeping its exact commit available under `refs/` will let future worker
and integration tests reference the canonical contract without moving OS
authority into this repository. No Codegeist OS tool or schema exists yet.

The expected HTTPS endpoint is
`https://git.codegeist.ai/codegeist/codegeist-os.git`. The current development
environment can reach the server but does not trust its Caddy local root CA, so
Git fails certificate verification before token authentication.

## Scope

- Obtain the Caddy root CA through a trusted administrative channel and make it
  available to Git in the development environment.
- Authenticate to Gitea with a runtime `GITEA_TOKEN` through a credential
  mechanism that does not expose the token.
- Verify the target repository and create it under the `codegeist` organization
  if it does not exist.
- Initialize the repository on `main` with minimal project documentation and a
  reference to the shared 0BSD license in `codegeist-ai/codegeist-ai` when
  creation is required.
- Add the clean HTTPS URL as the `refs/codegeist-os/` submodule, tracking
  `main`, and record the resulting gitlink.
- Update repository documentation and indexes after the submodule exists.

## Non-Goals

- Disable TLS verification or trust a certificate obtained only from the
  unverified server connection.
- Store `GITEA_TOKEN` in Git configuration, `.gitmodules`, URLs, files, logs, or
  command history.
- Define tools, observations, proposal schemas, permissions, actions, or an OS
  runtime.
- Make the identity training smoke depend on the submodule.

## Acceptance Criteria

- Git verifies `git.codegeist.ai` through an explicitly trusted Caddy root CA.
- The Gitea repository exists under the intended organization and uses `main`.
- `.gitmodules` contains `path = refs/codegeist-os`, the token-free HTTPS URL,
  and `branch = main`.
- A clean `git submodule update --init refs/codegeist-os` succeeds without
  disabling certificate verification.
- The submodule worktree is clean and its parent gitlink matches its checked-out
  commit.
- No credential appears in tracked files, Git remotes, command output captured
  as evidence, or repository history.

## Relevant Files Or Areas

- `.gitmodules`
- `refs/codegeist-os/`
- `README.md`
- `INDEX.md`
- `docs/architecture.md`
- `docs/security.md`
- Gitea repository `codegeist/codegeist-os`

## Implementation Notes

- Use HTTPS with token authentication as requested; the token cannot substitute
  for CA trust.
- Prefer environment or askpass-style credential injection with the minimum
  Gitea organization and repository scopes required for the operation.
- Keep the Codegeist OS repository independent. The submodule is a development
  and contract reference, not a runtime package dependency.

## Verification

- Run a certificate-verified `git ls-remote` against the target URL.
- Initialize and inspect the submodule through normal Git commands.
- Inspect `.gitmodules`, parent status, submodule status, and configured remotes
  for accidental credentials.
- Run `git --no-pager diff --check` in both repositories.

## Dependencies

- Trusted access to the Caddy local root CA.
- A `GITEA_TOKEN` authorized for the required organization operation.
- Confirmation that `codegeist` is the intended Gitea owner.

## Open Questions

- Whether the Gitea repository already exists once certificate trust is fixed.
- Whether Codegeist OS will use the same public GitHub mirror workflow as this
  repository.
