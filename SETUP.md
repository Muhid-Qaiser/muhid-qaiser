# Setup

Upload the contents of this folder into the root of your GitHub profile repository:

`Muhid-Qaiser/muhid-qaiser`

The repository should end up looking like:

```text
README.md
assets/
  hero.svg
  field-lab.svg
  breach.svg
  attack-prompt.svg
  attack-tool.svg
  attack-artifact.svg
  telemetry.svg
data/
  breach.json
scripts/
  update_telemetry.py
  process_breach.py
.github/
  workflows/
    telemetry.yml
    breach.yml
```

## After uploading

1. Open the repository's **Actions** tab and allow workflows if GitHub asks.
2. Run **Refresh profile telemetry** once, or wait for the push trigger.
3. Make sure repository **Issues** are enabled so `BREACH // AGENT-01` can work.
4. The mini-game automatically closes its generated issues after resolving them.

No personal access token is required. Both workflows use the repository's built-in `GITHUB_TOKEN`.

If the repo has branch protection that prevents Actions from pushing to `main`, allow GitHub Actions to write to the branch or remove that restriction for this profile repository.
