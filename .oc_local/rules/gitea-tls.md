# Gitea Authentication And TLS Exception

Use this project-specific rule only for authenticated HTTPS Git or API
operations whose verified target host is exactly `git.codegeist.ai`.

## Runtime Credential

- Require `GITEA_TOKEN` from the runtime environment and verify only that it is
  present. Never print its value:

  ```bash
  test -n "${GITEA_TOKEN:-}" || {
    printf '%s\n' 'GITEA_TOKEN is required' >&2
    exit 1
  }
  ```

- For Git, clear inherited credential helpers for the invocation and provide the
  `codegeist` username plus runtime token through this ephemeral helper:

  ```bash
  git \
    -c http.https://git.codegeist.ai/.sslVerify=false \
    -c credential.helper= \
    -c 'credential.helper=!f() { if [ "$1" = get ]; then printf "%s\n" "username=codegeist" "password=$GITEA_TOKEN"; fi; }; f' \
    fetch origin main
  ```

- Keep the credential-helper value single-quoted. The parent shell must pass the
  literal `$GITEA_TOKEN` reference to Git; only the ephemeral helper subprocess
  expands it from its inherited environment. The token value therefore does not
  become a command argument.
- Use the same helper form for authenticated fetch, push, clone, and submodule
  operations. Replace only the final Git subcommand and its non-secret inputs.
- For a Gitea API request, pass the authorization header through curl's stdin
  configuration rather than a URL or command argument:

  ```bash
  printf 'header = "Authorization: token %s"\n' "$GITEA_TOKEN" |
    curl \
      --config - \
      --fail-with-body \
      --silent \
      --show-error \
      --insecure \
      https://git.codegeist.ai/api/v1/...
  ```

- Give the token only the permissions required for the operation. Rotate it
  immediately if its value reaches terminal output, logs, history, a URL, a
  tracked file, or persistent configuration.

## TLS Exception

- The user explicitly authorizes bypassing certificate verification for the
  internal Caddy certificate currently served by `git.codegeist.ai`.
- Apply the exception to one Git invocation at a time with this URL-scoped
  command-line configuration:

  ```bash
  git -c http.https://git.codegeist.ai/.sslVerify=false <command>
  ```

- For a required Gitea API call, use `curl --insecure` only with an explicit
  `https://git.codegeist.ai/...` URL and do not follow redirects to another
  host.

- Confirm the selected remote URL uses the exact `https://git.codegeist.ai/`
  origin before applying the exception.
- Never place `GITEA_TOKEN` in a URL, query parameter, command argument, tracked
  file, log, or Git configuration.

## Prohibited Scope

- Do not write the exception through `git config --global`, `git config
  --system`, repository-local Git config, or any persistent credential file.
- Do not use the broader `GIT_SSL_NO_VERIFY` environment variable or an
  unscoped `http.sslVerify=false` setting.
- Do not persist the ephemeral credential helper or allow another configured
  helper to store `GITEA_TOKEN`.
- Do not apply the exception to GitHub, Hugging Face, package registries, model
  downloads, or any host other than `git.codegeist.ai`.
- Do not treat the bypass as evidence of server identity. Keep artifact digests,
  signed release metadata, and other integrity checks independent of transport.

## Removal Trigger

Remove this exception once the development environment trusts the correct Caddy
root CA or `git.codegeist.ai` presents a certificate chaining to an already
trusted root.
