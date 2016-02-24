import pytest


@pytest.fixture(params=['normal', 'MixedCase'])
def mix(request):
    return request.param


@pytest.fixture
def bin(tmpdir, mix):
    return tmpdir.ensure(mix, 'bin', dir=1)


@pytest.fixture
def home(tmpdir, mix):
    return tmpdir.ensure(mix, 'venvs', dir=1)
