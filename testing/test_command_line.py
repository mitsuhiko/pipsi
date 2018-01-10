import subprocess

import pytest
import sys


def test_list_command(home):
    assert not home.listdir()
    output = subprocess.check_output([
        'pipsi', '--home', home.strpath, 'list'
    ])
    assert output.strip() == b'There are no scripts installed through pipsi'
