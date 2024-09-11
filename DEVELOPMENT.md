# Plox python development guidelines

## Common python project pattern requirements

1. [`direnv`](https://github.com/direnv/direnv/blob/master/docs/installation.md)
2. Python and `pip`. Download via w.e package manger you want/use, or via distributed download packages: [see here](https://www.python.org/downloads/)
    * `pre-commit` installed via `pip install --upgrade pre-commit`
3. GNU utils (`make`, `sed`, `find`, etc.)

> [!WARNING]
> `sed` shipped with macOS by default _is not_ the same as GNU sed!!! Be sure to install
> the GNU coreutils/make/sed etc and then that they occur earlier appropriately in your
> system's `$PATH`.

## 0. Get project

```bash
git clone --recurse-submodules <git URL ...>

cd <project_repo>
```

## 1. Configured direnv managed project based venv

```bash
cd <project_repo>

direnv allow .
```

To validate, run

```bash
which python
```

and be sure that the Python it points to is based under a `.direnv/` folder in the current
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
