import os
import sys
import pytest
from pipsi import Repo, find_scripts


@pytest.fixture
def bin(tmpdir):
    return tmpdir.ensure('bin', dir=1)


@pytest.fixture
def home(tmpdir):
    return tmpdir.ensure('venvs', dir=1)


@pytest.fixture
def repo(home, bin):
    return Repo(str(home), str(bin))


def test_simple_install(repo, home, bin):
    assert not home.listdir()
    assert not bin.listdir()
    repo.install('.')
    assert home.join('pipsi').check()
    assert bin.listdir('pipsi*')


def test_find_scripts():
    print('executable ' + sys.executable)
    env = os.path.dirname(
        os.path.dirname(sys.executable))
    print('env %r' % env)
    print('listdir %r' % os.listdir(env))
    scripts = list(find_scripts(env, 'pipsi'))
    print('scripts %r' % scripts)
    assert scripts
