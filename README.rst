pipsi
=====

pipsi = pip script installer

What does it do?  pipsi is a wrapper around virtualenv and pip
which installs scripts provided by python packages into separate
virtualenvs to shield them from your system and each other.

In other words: you can use pipsi to install things like
pygmentize without making your system painful.

How do I get it?

::

    curl https://raw.githubusercontent.com/mitsuhiko/pipsi/master/get-pipsi.py | python

How does it work?

pipsi installs each package into ~/.local/venvs/PKGNAME and then
symlinks all new scripts into ~/.local/bin (these can be changed
by PIPSI_HOME and PIPSI_BIN_DIR env variables respectively).

Installing scripts from a package::

      $ pipsi install Pygments

Uninstalling packages and their scripts::

      $ pipsi uninstall Pygments

Upgrading a package::

      $ pipsi upgrade Pygments

Showing what's installed::

      $ pipsi list

How do I get rid of pipsi?

::

      $ pipsi uninstall pipsi

How do I upgrade pipsi?  With 0.5 and later just do this::

      $ pipsi upgrade pipsi

On older versions just uninstall and reinstall.
