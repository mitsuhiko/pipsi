import sys
import subprocess
from pipsi import IS_WIN


def test_create_env(tmpdir):
    subprocess.check_call([
        sys.executable, 'get-pipsi.py',
        str(tmpdir.join('venv')),
        str(tmpdir.join('test_bin')),
        '.'
    ])
    if IS_WIN:
        subprocess.check_call([
            str(tmpdir.join('test_bin/pipsi.exe'))
        ])
    else:
        subprocess.check_call([
            str(tmpdir.join('test_bin/pipsi'))
        ])
