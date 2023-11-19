#
# Excellent Regards, the Alveare Solutions #!/Society -x
#
# Pytest Config

import pytest
import os
import json

from subprocess import Popen, PIPE
from blue_cipher import load_config

CURRENT_DIR = os.getcwd()
PYTHON3 = './.venv/bin/python3'
CONFIG = {
    'config_file': '%s/conf/blue_cipher.conf.json' % CURRENT_DIR,
    'current_dir': CURRENT_DIR,
    'keytext_dir': '%s/dta/text' % CURRENT_DIR,
    'keytext_file': '%s/bc_key.txt' % CURRENT_DIR,
    'cleartext_file': '%s/bc_clear.txt' % CURRENT_DIR,
    'ciphertext_file': '%s/bc_cipher.txt' % CURRENT_DIR,
    'report_file': '%s/bc_report.dump' % CURRENT_DIR,
    'running_mode': 'decrypt',
    'data_source': 'file',
    'keycode': '123456',
    'cleanup': ['keytext_file'],
    'full_cleanup': [
        'keytext_file', 'cleartext_file', 'ciphertext_file', 'report_file'
    ],
    'report': True,
    'silent': False,
}

# DATA

@pytest.fixture
def decryption_data():
    return ['1-1-1,1-2-1,1-3-1,2-1-1,\n', '1-1-3,1-1-12,1-2-3,1-2-12,\n']

@pytest.fixture
def encryption_data():
    return ['cccc\n', 'aaaa\n']

@pytest.fixture
def conf_json():
    return CONFIG.copy()

# GENERAL

def sanitize_line(line_data):
    return line_data.rstrip('\n').rstrip(',')

def shell_cmd(command, user=None):
    if user:
        command = "su {} -c \'{}\'".format(user, command)
    process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    output, errors = process.communicate()
    return str(output).rstrip('\n'), str(errors).rstrip('\n'), process.returncode

# COMMANDS

@pytest.fixture
def bc_encryption_cmd(*args, **context):
    if not context.get('arg') or context['arg'].lower() == 'long':
        cmd = [PYTHON3, './blue_cipher.py', '--action', 'encrypt']
    elif context['arg'].lower() == 'short':
        cmd = [PYTHON3, './blue_cipher.py', '-a', 'encrypt']
    if args:
        cmd = cmd + list(args)
    return cmd

@pytest.fixture
def bc_decryption_cmd(*args, **context):
    if not context.get('arg') or context['arg'].lower() == 'long':
        cmd = [PYTHON3, './blue_cipher.py', '--action', 'decrypt']
    elif context['arg'].lower() == 'short':
        cmd = [PYTHON3, './blue_cipher.py', '-a', 'decrypt']
    if args:
        cmd = cmd + list(args)
    return cmd

@pytest.fixture
def bc_cleanup_cmd(*args, **context):
    if not context.get('arg') or context['arg'].lower() == 'long':
        cmd = [PYTHON3, './blue_cipher.py', '--action', 'cleanup']
    elif context['arg'].lower() == 'short':
        cmd = [PYTHON3, './blue_cipher.py', '-a', 'cleanup']
    if args:
        cmd = cmd + list(args)
    return cmd

@pytest.fixture
def bc_help_cmd(*args, **context):
    if not context.get('arg') or context['arg'].lower() == 'long':
        cmd = [PYTHON3, './blue_cipher.py', '--help']
    elif context['arg'].lower() == 'short':
        cmd = [PYTHON3, './blue_cipher.py', '-h']
    if args:
        cmd = cmd + list(args)
    return cmd

@pytest.fixture
def bc_util_help_cmd(*args, **context):
    if not context.get('arg') or context['arg'].lower() == 'long':
        cmd = ['bluecipher', '--help']
    elif context['arg'].lower() == 'short':
        cmd = ['bluecipher', '-h']
    if args:
        cmd = cmd + list(args)
    return cmd

@pytest.fixture
def bc_konfig_cmd(*args, **context):
    if not context.get('arg') or context['arg'].lower() == 'long':
        cmd = [PYTHON3, './blue_cipher.py', '--konfig-file', CONFIG['config_file']]
    elif context['arg'].lower() == 'short':
        cmd = [PYTHON3, './blue_cipher.py', '-K', 'encrypt']
    if args:
        cmd = cmd + list(args)
    return cmd

@pytest.fixture
def bw_build_cmd(*args, **context):
    cmd = ['./build.sh', 'BUILD']
    if args:
        cmd = cmd + list(args)
    return cmd

@pytest.fixture
def bw_install_cmd(*args, **context):
    cmd = ['./build.sh', 'INSTALL']
    if args:
        cmd = cmd + list(args)
    return cmd

@pytest.fixture
def bw_cleanup_cmd(*args, **context):
    if not context.get('arg') or context['arg'].lower() == 'long':
        cmd = ['./build.sh', '--cleanup', '-y']
    elif context['arg'].lower() == 'short':
        cmd = ['./build.sh', '-c', '-y']
    if args:
        cmd = cmd + list(args)
    return cmd

@pytest.fixture
def bw_setup_cmd(*args, **context):
    if not context.get('arg') or context['arg'].lower() == 'long':
        cmd = ['./build.sh', '--setup']
    elif context['arg'].lower() == 'short':
        cmd = ['./build.sh', '-s']
    if args:
        cmd = cmd + list(args)
    return cmd

# SETUP/TEARDOWN

@pytest.fixture
def bc_setup_teardown(bw_setup_cmd, bw_build_cmd, bw_install_cmd, bc_cleanup_cmd):
    out, err, exit = shell_cmd(' '.join(bw_setup_cmd))
    out, err, exit = shell_cmd(' '.join(bw_build_cmd))
    out, err, exit = shell_cmd(' '.join(bw_install_cmd))
    yield exit
    out, err, exit = shell_cmd(' '.join(bc_cleanup_cmd))

@pytest.fixture
def bw_setup_teardown(bw_setup_cmd, bw_cleanup_cmd):
    out, err, exit = shell_cmd(' '.join(bw_setup_cmd))
    yield exit
    out, err, exit = shell_cmd(' '.join(bw_cleanup_cmd))

# CODE DUMP

