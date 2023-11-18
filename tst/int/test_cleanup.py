import pytest

from tst.conftest import shell_cmd


def test_cleanup(bw_setup_cmd, bw_build_cmd, bw_cleanup_cmd):
    out, err, exit = shell_cmd(' '.join(bw_setup_cmd))
    out, err, exit = shell_cmd(' '.join(bw_build_cmd))
    out, err, exit = shell_cmd(' '.join(bw_cleanup_cmd))
    assert exit == 0
