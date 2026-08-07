# Gitea TLS Exception

Use this project-specific rule only for HTTPS operations whose verified target
host is exactly `git.codegeist.ai`.

## Rule

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
- Continue to provide `GITEA_TOKEN` through a credential or askpass mechanism;
  never place it in a URL, command argument, tracked file, log, or Git config.

## Prohibited Scope

- Do not write the exception through `git config --global`, `git config
  --system`, repository-local Git config, or any persistent credential file.
- Do not use the broader `GIT_SSL_NO_VERIFY` environment variable or an
  unscoped `http.sslVerify=false` setting.
- Do not apply the exception to GitHub, Hugging Face, package registries, model
  downloads, or any host other than `git.codegeist.ai`.
- Do not treat the bypass as evidence of server identity. Keep artifact digests,
  signed release metadata, and other integrity checks independent of transport.

## Removal Trigger

Remove this exception once the development environment trusts the correct Caddy
root CA or `git.codegeist.ai` presents a certificate chaining to an already
trusted root.
