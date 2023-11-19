#
# Excellent Regards, the Alveare Solutions #!/Society -x
#
# Install Tests

import pytest
import pysnooper

from tst.conftest import shell_cmd


@pysnooper.snoop()
def test_install(bc_setup_teardown, bw_install_cmd, bc_util_help_cmd):
    out, err, exit = shell_cmd(' '.join(bw_install_cmd))
    assert exit == 0
    out, err, exit = shell_cmd(' '.join(bc_util_help_cmd))
    assert exit == 0
