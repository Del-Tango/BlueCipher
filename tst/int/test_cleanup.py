#
# Excellent Regards, the Alveare Solutions #!/Society -x
#
# Cleanup Tests

import pytest
import pysnooper

from tst.conftest import shell_cmd


@pysnooper.snoop()
def test_cleanup(bw_setup_cmd, bw_build_cmd, bw_cleanup_cmd, bc_cleanup_cmd):
    out, err, exit = shell_cmd(' '.join(bw_setup_cmd))
    out, err, exit = shell_cmd(' '.join(bw_build_cmd))
    out, err, exit = shell_cmd(' '.join(bw_cleanup_cmd))
    assert exit == 0
    out, err, exit = shell_cmd(' '.join(bc_cleanup_cmd))
    assert exit == 0