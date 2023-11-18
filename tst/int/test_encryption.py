import pytest
import json
import os

from tst.conftest import shell_cmd, CONFIG
from blue_cipher import write2file


def test_file_base_encryption_from_cli(bc_setup_teardown, bc_encryption_cmd,
                                       encryption_data, conf_json):
    conf_json.update({'running_mode': 'encrypt', 'report': False})
    write2file(
        json.dumps(conf_json, indent=4), file_path=CONFIG['config_file'], mode='w'
    )
    cmd = bc_encryption_cmd + [
        '--key-code', CONFIG['keycode'],
        '--ciphertext-file', CONFIG['ciphertext_file'],
        '--cleartext-file', CONFIG['cleartext_file'],
        '--keytext-dir', CONFIG['keytext_dir']
    ]
    write2file(
        *encryption_data, file_path=CONFIG['cleartext_file'], mode='w'
    )
    out, err, exit = shell_cmd(' '.join(cmd))
    assert exit == 0

def test_file_base_encryption_from_cli_silently(bc_setup_teardown, bc_encryption_cmd,
                                                encryption_data, conf_json):
    conf_json.update({'running_mode': 'encrypt', 'report': False})
    write2file(
        json.dumps(conf_json, indent=4), file_path=CONFIG['config_file'], mode='w'
    )
    cmd = bc_encryption_cmd + [
        '--key-code', CONFIG['keycode'],
        '--ciphertext-file', CONFIG['ciphertext_file'],
        '--cleartext-file', CONFIG['cleartext_file'],
        '--keytext-dir', CONFIG['keytext_dir'],
        '--silent'
    ]
    write2file(
        *encryption_data, file_path=CONFIG['cleartext_file'], mode='w'
    )
    out, err, exit = shell_cmd(' '.join(cmd))
    assert exit == 0

def test_file_base_encryption_from_cli_reported(bc_setup_teardown, bc_encryption_cmd,
                                                encryption_data, conf_json):
    conf_json.update({'running_mode': 'encrypt', 'report': True})
    write2file(
        json.dumps(conf_json, indent=4), file_path=CONFIG['config_file'], mode='w'
    )
    cmd = bc_encryption_cmd + [
        '--key-code', CONFIG['keycode'],
        '--ciphertext-file', CONFIG['ciphertext_file'],
        '--cleartext-file', CONFIG['cleartext_file'],
        '--keytext-dir', CONFIG['keytext_dir'],
        '--silent'
    ]
    write2file(
        *encryption_data, file_path=CONFIG['cleartext_file'], mode='w'
    )
    out, err, exit = shell_cmd(' '.join(cmd))
    assert exit == 0
    assert os.path.exists(CONFIG['report_file'])

def test_file_base_encryption_from_config(bc_setup_teardown, bc_konfig_cmd,
                                          encryption_data, conf_json):
    conf_json.update({'running_mode': 'encrypt'})
    write2file(
        json.dumps(conf_json, indent=4), file_path=CONFIG['config_file'], mode='w'
    )
    write2file(
        *encryption_data, file_path=CONFIG['cleartext_file'], mode='w'
    )
    out, err, exit = shell_cmd(' '.join(bc_konfig_cmd))
    assert exit == 0

