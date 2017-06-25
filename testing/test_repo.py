import os
import sys
import pytest
from pipsi import Repo, find_scripts


@pytest.fixture
def repo(home, bin):
    return Repo(str(home), str(bin))


@pytest.mark.parametrize('package, glob', [
    ('grin', 'grin*'),
    ('pipsi', 'pipsi*'),
])
def test_simple_install(repo, home, bin, package, glob):
    assert not home.listdir()
    assert not bin.listdir()
    repo.install(package)
    assert home.join(package).check()
    assert bin.listdir(glob)
    assert repo.upgrade(package)


@pytest.mark.xfail(
    sys.version_info[0] != 3,
    reason='attic is python3 only', run=False)
@pytest.mark.xfail(
    'TRAVIS' in os.environ,
    reason='attic won\'t build on travis', run=False)
def test_simple_install_attic(repo, home, bin):
    test_simple_install(repo, home, bin, 'attic', 'attic*')


def test_list_everything(repo, home, bin):
    assert not home.listdir()
    assert not bin.listdir()
    assert repo.list_everything() == []


def test_find_scripts():
    print('executable ' + sys.executable)
    env = os.path.dirname(
        os.path.dirname(sys.executable))
    print('env %r' % env)
    print('listdir %r' % os.listdir(env))
    scripts = list(find_scripts(env, 'pipsi'))
    print('scripts %r' % scripts)
    assert scripts
