import pytest
import os
import json

from subprocess import Popen, PIPE
from blue_cipher import load_config

CURRENT_DIR = os.getcwd()
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
    return ['1-1-1,1-2-3\n', '1-2-4,1-2-5\n']

@pytest.fixture
def encryption_data():
    return ['First line to encrypt\n', 'Second line to encrypt\n']

@pytest.fixture
def conf_json():
    return json.loads('''{
    "keytext_dir":                "dta/text",
    "keytext_file":               "bc_key.txt",
    "cleartext_file":             "bc_clear.txt",
    "ciphertext_file":            "bc_cipher.txt",
    "report_file":                "bc_report.dump",
    "running_mode":               "encrypt",
    "data_source":                "file",
    "keycode":                    "123456",
    "cleanup":                    ["keytext_file"],
    "full_cleanup":               ["keytext_file","cleartext_file","ciphertext_file","report_file"],
    "report":                     true,
    "silent":                     false
}''')

# GENERAL

#@pytest.fixture
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
        cmd = ['./blue_cipher.py', '--action', 'encrypt']
    elif context['arg'].lower() == 'short':
        cmd = ['./blue_cipher.py', '-a', 'encrypt']
    if args:
        cmd = cmd + list(args)
    return cmd

@pytest.fixture
def bc_decryption_cmd(*args, **context):
    if not context.get('arg') or context['arg'].lower() == 'long':
        cmd = ['./blue_cipher.py', '--action', 'decrypt']
    elif context['arg'].lower() == 'short':
        cmd = ['./blue_cipher.py', '-a', 'decrypt']
    if args:
        cmd = cmd + list(args)
    return cmd

@pytest.fixture
def bc_cleanup_cmd(*args, **context):
    if not context.get('arg') or context['arg'].lower() == 'long':
        cmd = ['./blue_cipher.py', '--action', 'cleanup']
    elif context['arg'].lower() == 'short':
        cmd = ['./blue_cipher.py', '-a', 'cleanup']
    if args:
        cmd = cmd + list(args)
    return cmd

@pytest.fixture
def bc_help_cmd(*args, **context):
    if not context.get('arg') or context['arg'].lower() == 'long':
        cmd = ['./blue_cipher.py', '--help']
    elif context['arg'].lower() == 'short':
        cmd = ['./blue_cipher.py', '-h']
    if args:
        cmd = cmd + list(args)
    return cmd

@pytest.fixture
def bc_konfig_cmd(*args, **context):
    if not context.get('arg') or context['arg'].lower() == 'long':
        cmd = ['./blue_cipher.py', '--konfig-file', CONFIG['config_file']]
    elif context['arg'].lower() == 'short':
        cmd = ['./blue_cipher.py', '-K', 'encrypt']
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

