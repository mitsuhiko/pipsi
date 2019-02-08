# pipsi

**⚠️ pipsi is no longer maintained. See [pipx](https://github.com/pipxproject/pipx) for an actively maintained alternative. https://github.com/pipxproject/pipx**

---

pipsi = **pip** **s**cript **i**nstaller

## What does it do?
**pipsi** makes installing python packages with global entry points painless. These are Python packages that expose an entry point through the command line such as [Pygments](https://pypi.org/project/Pygments/).

If you are installing Python packages globally for cli access, you almost certainly want to use pipsi instead of running `sudo pip ...`. so that you get
* Isolated dependencies to guarantee no version conflicts
* The ability to install packages globally without using sudo
* The ability to uninstall a package and its dependencies without affecting other globally installed Python programs

pipsi is not meant for installing libraries that will be imported by other Python modules.

## How do I get it?

```bash
curl https://raw.githubusercontent.com/mitsuhiko/pipsi/master/get-pipsi.py | python
```

to see installation options, including not automatically modifying the PATH environment variable

```bash
curl https://raw.githubusercontent.com/mitsuhiko/pipsi/master/get-pipsi.py | python - --help
```

## How does it work?

pipsi is a wrapper around virtualenv and pip which installs scripts provided by python packages into isolated virtualenvs so they do not pollute your system's Python packages.

pipsi installs each package into `~/.local/venvs/PKGNAME` and then symlinks all new scripts into `~/.local/bin` (these can be changed by `PIPSI_HOME` and `PIPSI_BIN_DIR` environment variables respectively).

Here is a tree view into the directory structure created by pipsi after installing pipsi and running `pipsi install Pygments`.

```
/Users/user/.local
├── bin
│   ├── pipsi -> /Users/user/.local/venvs/pipsi/bin/pipsi
│   └── pygmentize -> /Users/user/.local/venvs/pygments/bin/pygmentize
├── share
│   └── virtualenvs
└── venvs
    ├── pipsi
    └── pygments
```

Compared to `pip install --user` each `PKGNAME` is installed into its own virtualenv, so you don't have to worry about different packages having conflicting dependencies. As long as `~/.local/bin` is on your PATH, you can run any of these scripts directly.

### Installing scripts from a package:

```bash
$ pipsi install Pygments
```

### Installing scripts from a package using a particular version of python:

```bash
$ pipsi install --python /usr/bin/python3.5 hovercraft
```

### Uninstalling packages and their scripts:

```bash
$ pipsi uninstall Pygments
```

### Upgrading a package:

```bash
$ pipsi upgrade Pygments
```

### Showing what's installed:

```bash
$ pipsi list
```

### How do I get rid of pipsi?

```bash
$ pipsi uninstall pipsi
```

### How do I upgrade pipsi?

With 0.5 and later just do this:

```bash
$ pipsi upgrade pipsi
```

On older versions just uninstall and reinstall.
