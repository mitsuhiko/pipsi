import os.path
import sys
import subprocess
from pipsi import IS_WIN


def test_create_env(tmpdir):
    subprocess.check_call([
        sys.executable, 'get-pipsi.py',
        '--home', str(tmpdir.join('venv')),
        '--bin-dir', str(tmpdir.join('test_bin')),
        '--src', '.',
        '--ignore-existing',
    ])
    pipsi_bin = str(tmpdir.join('test_bin/pipsi' + ('.exe' if IS_WIN else '')))

    subprocess.check_call([pipsi_bin])
