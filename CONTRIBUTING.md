# Contributing to Python Loading SDK

For local setup and test commands, see the [development guide](README.md#development).

## Publishing a release

Pushing a tag starts the release workflow. The tag must match the version in `pyproject.toml`, prefixed with `v`.

| Release | Example tag | Publishes to |
| --- | --- | --- |
| Alpha, beta, or release candidate | `v0.5.1a1`, `v0.5.1b1`, `v0.5.1rc1` | TestPyPI |
| Stable | `v0.5.1` | PyPI |

### 1. Prepare the release

Start with the release changes committed on `main`. Run these commands from the repository root. A clean working tree produces no output from `git status --short`.

```sh
git switch main
git pull --ff-only origin main
git status --short
```

Choose a new version for the target index. This example prepares a release candidate. Set `release_version=0.5.1` for the corresponding stable release.

```sh
release_version=0.5.1rc1
uv version "$release_version"
```

### 2. Review and publish

Add the release notes to `CHANGELOG.md`. Review them alongside the version and lockfile changes.

```sh
git add CHANGELOG.md pyproject.toml uv.lock
git diff --cached
```

Commit the release, tag that commit, and push both together to start publication.

```sh
git commit -m "Release $release_version"
git tag -a "v$release_version" -m "Release $release_version"
git push --atomic origin main "v$release_version"
```

### 3. Verify the release

Open the [release workflow](https://github.com/hnrkcode/python-loading-sdk/actions/workflows/pypi.yaml) and select your tag. A passing `check-index` job confirms that the published wheel and source distribution passed checksum and installation checks.

After verifying a release candidate on TestPyPI, repeat the steps with the stable version to publish to PyPI.

## One-time publisher setup

Configure a GitHub Trusted Publisher for `python-loading-sdk` on each index. Use the GitHub owner `hnrkcode`, repository `python-loading-sdk`, and workflow filename `pypi.yaml`. Set the GitHub environment to `testpypi` on TestPyPI and `pypi` on PyPI.
