#!/usr/bin/env python
import os
import sys
from subprocess import call
import shutil


try:
    WindowsError
except NameError:
    IS_WIN = False
    PIP = '/bin/pip'
    PIPSI = '/bin/pipsi'
else:
    IS_WIN = True
    PIP = '/Scripts/pip.exe'
    PIPSI = '/Scripts/pipsi.exe'

DEFAULT_PIPSI_HOME = os.path.expanduser('~/.local/venvs')
DEFAULT_PIPSI_BIN_DIR = os.path.expanduser('~/.local/bin')

def echo(msg=''):
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()


def fail(msg):
    sys.stderr.write(msg + '\n')
    sys.stderr.flush()
    sys.exit(1)


def succeed(msg):
    echo(msg)
    sys.exit(0)


def command_exists(cmd):
    with open(os.devnull, 'w') as null:
        try:
            return call(
                [cmd, '--version'],
                stdout=null, stderr=null) == 0
        except OSError:
            return False


def publish_script(venv, bin_dir):
    if IS_WIN:
        for name in os.listdir(venv + '/Scripts'):
            if 'pipsi' in name.lower():
                shutil.copy(venv + '/Scripts/' + name, bin_dir)
    else:
        os.symlink(venv + '/bin/pipsi', bin_dir + '/pipsi')
    echo('Installed pipsi binary in ' + bin_dir)


def install_files(venv, bin_dir, install):
    try:
        os.makedirs(bin_dir)
    except OSError:
        pass

    def _cleanup():
        try:
            shutil.rmtree(venv)
        except (OSError, IOError):
            pass

    if call(['virtualenv', venv]) != 0:
        _cleanup()
        fail('Could not create virtualenv for pipsi :(')

    if call([venv + PIP, 'install', install]) != 0:
        _cleanup()
        fail('Could not install pipsi :(')

    publish_script(venv, bin_dir)


def main():
    if command_exists('pipsi'):
        succeed('You already have pipsi installed')
    else:
        echo('Installing pipsi')

    if not command_exists('virtualenv'):
        fail('You need to have virtualenv installed to bootstrap pipsi.')


    bin_dir = os.environ.get('PIPSI_BIN_DIR', DEFAULT_PIPSI_BIN_DIR)
    venv = os.path.join(os.environ.get('PIPSI_HOME', DEFAULT_PIPSI_HOME),
                        'pipsi')
    install_files(venv, bin_dir, 'pipsi')

    if not command_exists('pipsi') != 0:
        echo()
        echo('=' * 60)
        echo()
        echo('Warning:')
        echo('  It looks like {0} is not on your PATH so pipsi will'.format(bin_dir))
        echo('  not work out of the box.  To fix this problem make sure to')
        echo('  add this to your .bashrc / .profile file:')
        echo()
        echo('  export PATH={0}:$PATH'.format(bin_dir))
        echo()
        echo('=' * 60)
        echo()

    succeed('pipsi is now installed.')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # we are being tested
        install_files(*sys.argv[1:])
    else:
        main()
