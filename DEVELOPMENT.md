# Plox python development guidelines

## Common python project pattern requirements

1. GNU utils (`make`, `sed`, `find`, etc.)
1. [`direnv`](https://github.com/direnv/direnv/blob/master/docs/installation.md)
1. [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
    * **NOTE**: must also manually add `layout uv` support as of May 2025:

    ```bash
    # from root of this repo
    cat temp/direnv_support  > ${XDG_CONFIG_HOME:-${HOME}/.config}/direnv/direnvrc
    ```

> [!WARNING]
> `sed` shipped with macOS by default _is not_ the same as GNU sed!!! Be sure to install
> the GNU coreutils/make/sed etc and then that they occur earlier appropriately in your
> system's `$PATH`.

## 0. Get project

```bash
git clone --recurse-submodules <git URL ...>

cd <project_repo>
```

## 1. Configured uv/direnv managed project based venv

```bash
direnv allow .
```

To validate, run

```bash
which python
```

and be sure that the Python it points to is based under a `.venv/` folder in the current
project's directory.

## 2. Install project's deps

```bash
make install-deps
```

## 3. Validate pre-commit hooks

```bash
pre-commit run --all-files
```

## 4. Do development

Do your work.

## 5. Update secrets baseline

```bash
pip install git+https://github.com/ibm/detect-secrets.git@0.13.1+ibm.62.dss
detect-secrets scan --update .secrets.baseline  .
detect-secrets audit .secrets.baseline
```

Work through the interactive menu answering the prompts as appropriate.

Them,

```bash
git add .secrets.baseline
```


## 5. Ensure code conformity

```bash
make check
```

Iterate and fix any issues that may arise.

## 6. Push code to branch, open PR

```bash
git checkout -b my-feature-branch
git add <files>
git commit -m "<type>: <description>"
git push -u origin my-feature-branch
```

Navigate to github.com and open a pull request. Make the title the same as the initial
conventional commit that was first pushed.

## Misc

### Updating standard python version

By default, it is expected that all development of this library is done
leveraging the version of Python in the `.python-version` file. This
is defined _in addition to_ the range based `requires-python` in the
`pyproject.toml` to ensure consistent dev experience.

To update the expected standardized version, update the `.python-version`
file. The `layout_uv` function above has support for watching this
file (via `watch_file`) and should automatically re-create the venv
for you with the right version, fetching it if needed.

### Updating package versions

```bash
rm uv.lock
uv sync --all-groups
```
