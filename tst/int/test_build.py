import pytest

from tst.conftest import shell_cmd


def test_build(bw_setup_teardown, bw_build_cmd):
    out, err, exit = shell_cmd(' '.join(bw_build_cmd))
    assert exit == 0
