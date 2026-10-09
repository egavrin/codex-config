# Create a registry auth without exposing its token

## Prompt

I have a private registry token in `REGISTRY_TOKEN`. Create a Runpod registry auth
named `ghcr` for username `octocat`, but do not put the token in command arguments
or shell history.

## Expected behavior

The agent should do these actions:

1. Use `runpodctl registry create` with `--password-stdin`
2. Pipe the environment variable through stdin without expanding its value into the
   runpodctl argument list
3. Keep `--name ghcr` and `--username octocat` on the command
4. Avoid `--password`, because that exposes the credential through `argv`
5. Omit both password flags only for a human at an interactive no-echo prompt. This is inappropriate for an automated command.

## Assertions

- Uses `runpodctl registry create --name ghcr --username octocat --password-stdin`
- Pipes `REGISTRY_TOKEN` into stdin, for example with `printenv REGISTRY_TOKEN`
- Does not use `--password "$REGISTRY_TOKEN"` or place the token value in any argument
- Does not tell an automated caller to rely on the interactive prompt
- Does not write the token to a temporary file
