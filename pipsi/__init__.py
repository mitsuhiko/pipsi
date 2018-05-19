import json
import os
import pkgutil
import sys
import shutil
import subprocess
import glob
from collections import namedtuple
from os.path import join, realpath, dirname, normpath, normcase
from operator import methodcaller
try:
    subprocess.run

    def run(*args, **kw):
        kw.update(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = subprocess.run(*args, **kw)
        r.stdout, r.stderr = map(proc_output, (r.stdout, r.stderr))
        return r
except AttributeError:  # no `subprocess.run`, py < 3.5
    CompletedProcess = namedtuple('CompletedProcess',
                                  ('args', 'returncode', 'stdout', 'stderr'))

    def run(argv, **kw):
        p = subprocess.Popen(
            argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kw)
        out, err = map(proc_output, p.communicate())
        return CompletedProcess(argv, p.returncode, out, err)
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

import click
from pkg_resources import Requirement

try:
    WindowsError
except NameError:
    IS_WIN = False
    BIN_DIR = 'bin'
else:
    IS_WIN = True
    BIN_DIR = 'Scripts'

FIND_SCRIPTS_SCRIPT = pkgutil.get_data('pipsi', 'scripts/find_scripts.py').decode('utf-8')
GET_VERSION_SCRIPT = pkgutil.get_data('pipsi', 'scripts/get_version.py').decode('utf-8')

# The `click` custom context settings
CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help'],
)


def proc_output(s):
    s = s.strip()
    if not isinstance(s, str):
        s = s.decode('utf-8', 'replace')
    return s


def normalize_package(value):
    # Strips the version and normalizes name
    requirement = Requirement.parse(value)
    return requirement.project_name.lower()


def normalize(path):
    return normcase(normpath(realpath(path)))


def real_readlink(filename):
    try:
        target = os.readlink(filename)
    except (OSError, IOError, AttributeError):
        return None
    return normpath(realpath(join(dirname(filename), target)))


def publish_script(src, dst):
    if IS_WIN:
        # always copy new exe on windows
        shutil.copy(src, dst)
        click.echo('  Copied Executable ' + dst)
        return True
    else:
        old_target = real_readlink(dst)
        if old_target == src:
            return True
        try:
            os.remove(dst)
        except OSError:
            pass
        try:
            os.symlink(src, dst)
        except OSError:
            pass
        else:
            click.echo('  Linked script ' + dst)
            return True


def extract_package_version(virtualenv, package):
    prefix = normalize(join(virtualenv, BIN_DIR, ''))

    return run([
        join(prefix, 'python'), '-c', GET_VERSION_SCRIPT,
        package,
    ]).stdout.strip()


def find_scripts(virtualenv, package):
    prefix = normalize(join(virtualenv, BIN_DIR, ''))

    files = run([
        join(prefix, 'python'), '-c', FIND_SCRIPTS_SCRIPT,
        package, prefix
    ]).stdout.splitlines()

    files = map(normalize, files)
    files = filter(
        methodcaller('startswith', prefix),
        files,
    )

    def valid(filename):
        return os.path.isfile(filename) and \
            IS_WIN or os.access(filename, os.X_OK)

    result = list(filter(valid, files))

    if IS_WIN:
        for filename in files:
            globed = glob.glob(filename + '*')
            result.extend(filter(valid, globed))
    return result


class UninstallInfo(object):

    def __init__(self, package, paths=None, installed=True):
        self.package = package
        self.paths = paths or []
        self.installed = installed

    def perform(self):
        for path in self.paths:
            try:
                os.remove(path)
            except OSError:
                shutil.rmtree(path)






class Repo(object):

    def __init__(self, home, bin_dir):
        self.home = realpath(home)
        self.bin_dir = bin_dir

    def resolve_package(self, spec, python=None):
        url = urlparse(spec)
        if url.netloc == 'file':
            location = url.path
        elif url.netloc != '':
            if not url.fragment.startswith('egg='):
                raise click.UsageError('When installing from URLs you need '
                                       'to add an egg at the end.  For '
                                       'instance git+https://.../#egg=Foo')
            return url.fragment[4:], [spec]
        elif os.path.isdir(spec):
            location = spec
        else:
            return spec, [spec]

        if not os.path.exists(join(location, 'setup.py')):
            raise click.UsageError('%s does not appear to be a local '
                                   'Python package.' % spec)

        res = run(
            [python or sys.executable, 'setup.py', '--name'],
            cwd=location)
        if res.returncode:
            raise click.UsageError(
                '%s does not appear to be a valid '
                'package. Error from setup.py: %s' % (spec, res.stderr)
            )
        name = res.stdout

        return name, [location]

    def get_package_path(self, package):
        return join(self.home, normalize_package(package))

    def find_installed_executables(self, path):
        prefix = join(realpath(normpath(path)), '')
        try:
            for filename in os.listdir(self.bin_dir):
                exe = os.path.join(self.bin_dir, filename)
                target = real_readlink(exe)
                if target is None:
                    continue
                if target.startswith(prefix):
                    yield exe
        except OSError:
            pass

    def get_package_scripts(self, path):
        """Get the scripts installed for PATH

        Looks for package metadata listing which scripts were
        installed. If there is no metadata (package was installed
         with an older version of pipsi) then fall back to the old
         find_installed_executables method.
        """
        info = self.get_package_info(path)
        if 'scripts' in info:
            return info['scripts']
        # No script metadata - fall back to older method of searching for executables
        return self.find_installed_executables(path)

    def link_scripts(self, scripts):
        rv = []
        for script in scripts:
            script_dst = os.path.join(
                self.bin_dir, os.path.basename(script))
            if publish_script(script, script_dst):
                rv.append((script, script_dst))

        return rv

    def save_package_info(self, venv_path, package, scripts):
        package_info_file_path = join(venv_path, 'package_info.json')
        package_name = Requirement.parse(package).project_name
        version = extract_package_version(venv_path, package_name)

        package_info = {
            'name': package_name,
            'version': version,
            'scripts': [script for target, script in scripts],
        }
        with open(package_info_file_path, 'w') as fh:
            json.dump(package_info, fh)

    def get_package_info(self, venv_path):
        package_info_file_path = join(venv_path, 'package_info.json')
        with open(package_info_file_path, 'r') as fh:
            return json.load(fh)

    def install(self, package, python=None, editable=False, system_site_packages=False):
        package, install_args = self.resolve_package(package, python)

        venv_path = self.get_package_path(package)
        if os.path.isdir(venv_path):
            click.echo('%s is already installed' % package)
            return

        if not os.path.exists(self.bin_dir):
            os.makedirs(self.bin_dir)

        from subprocess import Popen

        def _cleanup():
            try:
                shutil.rmtree(venv_path)
            except (OSError, IOError):
                pass
            return False

        # Install virtualenv, use the pipsi used python version by default
        args = [sys.executable, '-m', 'virtualenv', '-p', python or sys.executable, venv_path]

        if system_site_packages:
            args.append('--system-site-packages')

        try:
            if Popen(args).wait() != 0:
                click.echo('Failed to create virtualenv.  Aborting.')
                return _cleanup()

            args = [os.path.join(venv_path, BIN_DIR, 'pip'), 'install']
            if editable:
                args.append('--editable')

            if Popen(args + install_args).wait() != 0:
                click.echo('Failed to pip install.  Aborting.')
                return _cleanup()
        except Exception:
            _cleanup()
            raise

        # Find all the scripts
        scripts = find_scripts(venv_path, package)

        # And link them
        linked_scripts = self.link_scripts(scripts)

        self.save_package_info(venv_path, package, linked_scripts)

        # We did not link any, rollback.
        if not linked_scripts:
            click.echo('Did not find any scripts.  Uninstalling.')
            return _cleanup()
        return True

    def uninstall(self, package):
        path = self.get_package_path(package)
        if not os.path.isdir(path):
            return UninstallInfo(package, installed=False)
        paths = [path]
        paths.extend(self.get_package_scripts(path))
        return UninstallInfo(package, paths)

    def upgrade(self, package, editable=False):
        package, install_args = self.resolve_package(package)

        venv_path = self.get_package_path(package)
        if not os.path.isdir(venv_path):
            click.echo('%s is not installed' % package)
            return

        from subprocess import Popen

        old_scripts = set(self.get_package_scripts(venv_path))

        args = [os.path.join(venv_path, BIN_DIR, 'pip'), 'install',
                '--upgrade']
        if editable:
            args.append('--editable')

        if Popen(args + install_args).wait() != 0:
            click.echo('Failed to upgrade through pip.  Aborting.')
            return

        scripts = find_scripts(venv_path, package)
        linked_scripts = self.link_scripts(scripts)
        to_delete = old_scripts - set(script for target, script in linked_scripts)

        for script in to_delete:
            try:
                click.echo('  Removing old script %s' % script)
                os.remove(script)
            except (IOError, OSError):
                pass

        self.save_package_info(venv_path, package, linked_scripts)

        return True

    def list_everything(self, versions=False):
        venvs = {}
        python = '/Scripts/python.exe' if IS_WIN else '/bin/python'
        if os.path.isdir(self.home):
            for venv in os.listdir(self.home):
                venv_path = os.path.join(self.home, venv)
                if os.path.isdir(venv_path) and \
                   os.path.isfile(venv_path + python):
                    info = self.get_package_info(venv_path)
                    version = None
                    if versions:
                        version = info.get('version')
                    venvs[venv] = [info.get('scripts', []), version]

        return sorted(venvs.items())


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--home', type=click.Path(),envvar='PIPSI_HOME',
    default=os.path.join(os.path.expanduser('~'), '.local', 'venvs'),
    help='The folder that contains the virtualenvs.')
@click.option(
    '--bin-dir', type=click.Path(),
    envvar='PIPSI_BIN_DIR',
    default=os.path.join(os.path.expanduser('~'), '.local', 'bin'),
    help='The path where the scripts are symlinked to.')

@click.version_option(
    message='%(prog)s, version %(version)s, python ' + str(sys.executable))
@click.pass_context
def cli(ctx, home, bin_dir):
    """pipsi is a tool that uses virtualenv and pip to install shell
    tools that are separated from each other.
    """
    ctx.obj = Repo(home, bin_dir)


@cli.command()
@click.argument('package')
@click.option('--python', default=None,
              help='The python interpreter to use.')
@click.option('--editable', '-e', is_flag=True,
              help='Enable editable installation.  This only works for '
                   'locally installed packages.')
@click.option('--system-site-packages', is_flag=True,
              help='Give the virtual environment access to the global '
                   'site-packages.')
@click.pass_obj
def install(repo, package, python, editable, system_site_packages):
    """Installs scripts from a Python package.

    Given a package this will install all the scripts and their dependencies
    of the given Python package into a new virtualenv and symlinks the
    discovered scripts into BIN_DIR (defaults to ~/.local/bin).
    """
    if repo.install(package, python, editable, system_site_packages):
        click.echo('Done.')
    else:
        sys.exit(1)



@cli.command()
@click.argument('package')
@click.option('--editable', '-e', is_flag=True,
              help='Enable editable installation.  This only works for '
                   'locally installed packages.')
@click.pass_obj
def upgrade(repo, package, editable):
    """Upgrades an already installed package."""
    if repo.upgrade(package, editable):
        click.echo('Done.')
    else:
        sys.exit(1)


@cli.command(short_help='Uninstalls scripts of a package.')
@click.argument('package')
@click.option('--yes', is_flag=True, help='Skips all prompts.')
@click.pass_obj
def uninstall(repo, package, yes):
    """Uninstalls all scripts of a Python package and cleans up the
    virtualenv.
    """
    uinfo = repo.uninstall(package)
    if not uinfo.installed:
        click.echo('%s is not installed' % package)
    else:
        click.echo('The following paths will be removed:')
        for path in uinfo.paths:
            click.echo('  %s' % click.format_filename(path))
        click.echo()
        if yes or click.confirm('Do you want to uninstall %s?' % package):
            uinfo.perform()
            click.echo('Done!')
        else:
            click.echo('Aborted!')
            sys.exit(1)


@cli.command('list')
@click.option('--versions', is_flag=True,
              help='Show packages version')
@click.pass_obj
def list_cmd(repo, versions):
    """Lists all scripts installed through pipsi."""
    list_of_non_empty_venv = [(venv, scripts)
                              for venv, scripts in repo.list_everything()
                              if scripts]
    if list_of_non_empty_venv:
        click.echo('Packages and scripts installed through pipsi:')
        for venv, (scripts, version) in repo.list_everything(versions):
            if versions:
                click.echo('  Package "%s" (%s):' % (venv, version or 'unknown'))
            else:
                click.echo('  Package "%s":' % venv)
                for script in scripts:
                    click.echo('    ' + script)
    else:
        click.echo('There are no scripts installed through pipsi')

if __name__ == '__main__':
    cli()
