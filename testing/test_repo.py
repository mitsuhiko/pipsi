import os
import sys
import pytest
from pipsi import Repo, find_scripts


@pytest.fixture
def bin(tmpdir):
    return tmpdir.ensure('MixedCase', 'bin', dir=1)


@pytest.fixture
def home(tmpdir):
    return tmpdir.ensure('MixedCase', 'venvs', dir=1)


@pytest.fixture
def repo(home, bin):
    return Repo(str(home), str(bin))


def test_simple_install(repo, home, bin):
    assert not home.listdir()
    assert not bin.listdir()
    repo.install('grin')
    assert home.join('grin').check()
    assert bin.listdir('grin*')


def test_find_scripts():
    print('executable ' + sys.executable)
    env = os.path.dirname(
        os.path.dirname(sys.executable))
    print('env %r' % env)
    print('listdir %r' % os.listdir(env))
    scripts = list(find_scripts(env, 'pipsi'))
    print('scripts %r' % scripts)
    assert scripts
