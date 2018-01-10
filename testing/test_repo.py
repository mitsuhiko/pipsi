import os
import sys
import pytest
import click
from pipsi import Repo, find_scripts


@pytest.fixture
def repo(home, bin):
    return Repo(str(home), str(bin))


@pytest.mark.resolve
def test_resolve_local_package(repo, tmpdir):
    pkgdir = tmpdir.ensure('foopkg', dir=True)
    pkgdir.join('setup.py').write_text(
        u'\n'.join([
            u'from setuptools import setup',
            u'setup(name="foopkg", version="0.0.1", py_modules=["foo"])'
        ]),
        'utf-8'
    )
    pkgdir.join('foo.py').write_text(u'print("hello world")\n', 'utf-8')

    assert repo.resolve_package(str(pkgdir)) == ('foopkg', [str(pkgdir)])


@pytest.mark.resolve
def test_resolve_local_fails_when_invalid_package(repo, tmpdir):
    pkgdir = tmpdir.ensure('foopkg', dir=True)
    pkgdir.join('setup.py').write_text(u'raise Exception("EXCMSG")', 'utf-8')
    pkgdir.join('foo.py').ensure()

    with pytest.raises(click.UsageError) as excinfo:
        repo.resolve_package(str(pkgdir))
    assert 'does not appear to be a valid package' in str(excinfo.value)
    assert 'EXCMSG' in str(excinfo.value)


@pytest.mark.resolve
def test_resolve_local_fails_when_no_package(repo, tmpdir):
    pkgdir = tmpdir.ensure('foopkg', dir=True)

    with pytest.raises(click.UsageError) as excinfo:
        repo.resolve_package(str(pkgdir))
    assert 'does not appear to be a local Python package' in str(excinfo.value)


@pytest.mark.parametrize('package, glob', [
    ('grin', 'grin*'),
    pytest.param('pipsi', 'pipsi*',
                 marks=pytest.mark.xfail(reason="Clashes with local pipsi directory")),
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
