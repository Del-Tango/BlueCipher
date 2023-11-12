#!/usr/bin/python3
#
# Excellent Regards, the Alveare Solutions #!/Society -x
#
# Blue Cipher Enryptor/Decryptor

# [ DESCRIPTION ]: Book Cipher Automation #####################################
#
#   Book ciphers are an old-school, slow and string style of encryption that
#   maps each character in a message with three numbers - the page number, line
#   number on that page, and character number on that line. BC uses the format
#   <page>-<line>-<character>. Example: 10-7-23,11-12-8,...
#
#   BC automates the decryption of ciphertext or encryption of cleartext from
#   both a CLI menu and using input/output files on the basis of a keytext file
#   generated by the concatonation of chapter files in a orded dictated by the
#   keycode.
#
#   Execution is optimized by using asynchronous programming and caching. As
#   with everything there are tradeoffs, but the design decession make it -
#
#       * Packaged in such a way that it can be run like a standalone script as
#       well as a installable consumable package for pip (can be build locally
#       using the Build WizZard script).
#
#       * OS agnostic - can be run on both Linux and Windows machines
#
#       * Simple to use and to understand.
#
#       * Keytext can be randomly generated or actual segments of a known book.
#
# [ ENCRYPTION ]:
#
#
#
# [ DECRYPTION ]:
#
###############################################################################

import optparse
import os
import glob
import json
import pysnooper

SCRIPT_NAME='BlueCipher'
VERSION='1.0'
VERSION_NAME='Orbital'
CONFIG = {
    'keytext_dir': 'text',
    'keytext_file': 'bc_key.txt',
    'cleartext_file': 'bc_clear.txt',
    'ciphertext_file': 'bc_cipher.txt',
    'running_mode': 'decrypt',                          # encrypt
    'data_source': 'file',                              # terminal
    'keycode': '123456',                                # order of concatenated text files
    'report_file': 'bc_report.dump',
    'report': True,
}
keyfile_chapter_cache = []                              # [['chapter', 'lines', ...], ...]
keyfile_line_cache = {}                                 # {'1': {'1': ['line', 'text', ...], '2': [], ...}, '2': {}, ...}
text_file_cache = {}                                    # {'file_name': ['file', 'lines', '', ...], ...}
ciphertext_cache = {}                                   # {'10-14-23': 'a', ...}
cleartext_cache = {}                                    # {'a': ['10-14-23', 13-1-32, ...]}
encryption_cache = {}                                   # {'a': {'last': '10-14-24',}, ...}
action_result = {'exit': 0, 'output': [], 'msg': ''}

# FETCHERS

def fetch_running_mode_from_user(prompt='Action'):
    global CONFIG
    print(
        '[ INFO ]: Specify action or (.back)...'
    )
    if CONFIG.get('running_mode'):
        prompt = prompt + '[' + CONFIG['running_mode'] + ']> '
        print(
            '[ INFO ]: Leave blank to keep current '\
            '(%s)' % CONFIG['running_mode']
        )
    print(
        '1) Encrypt cleartext',
        '2) Decrypt ciphertext', sep='\n'
    )
    selection_map = {'1': 'encrypt', '2': 'decrypt'}
    while True:
        selection = input(prompt)
        if not selection:
            if not CONFIG.get('running_mode'):
                continue
            selection = '1' if CONFIG.get('running_mode') == 'encrypt' else '2'
        if selection == '.back':
            return
        if selection not in ('1', '2'):
            print('[ ERROR ]: Invalid selection (%s)' % selection)
        break
    return selection_map[selection]

def fetch_data_from_user(prompt='Data'):
    print('[ INFO ]: Specify input data for action or (.back)...')
    while True:
        data = input(prompt + '> ')
        if not data:
            continue
        if data == '.back':
            return
        break
    return data

def fetch_replay_confirmation_from_user(prompt='Replay'):
    print('[ Q/A ]: Do you want to go again?')
    while True:
        answer = input(prompt + '[Y/N]> ')
        if not answer:
            continue
        if answer.lower() not in ('y', 'n', 'yes', 'no', 'yeah', 'nah'):
            print('[ ERROR ]: Invalid answer (%s)' % answer)
            continue
        break
    return True if answer in ('y', 'yes', 'yeah') else False

def fetch_keycode_from_user(prompt='KeyCode'):
    global CONFIG
    print('[ INFO ]: Specify text keycode sequence or (.back)...')
    if CONFIG.get('keycode'):
        prompt = prompt + '[' + CONFIG['keycode'] + ']> '
        print(
            '[ INFO ]: Leave blank to keep current '\
            '(%s)' % CONFIG['keycode']
        )
    while True:
        code = input(prompt)
        if not code:
            if not CONFIG.get('keycode'):
                continue
            code = CONFIG.get('keycode')
        if code == '.back':
            return
        CONFIG.update({'keycode': code})
        break
    return code

# CHECKERS

@pysnooper.snoop()
def check_preconditions(**conf):
    errors = []
    file_paths = ['keytext_file', 'cleartext_file', 'ciphertext_file']
    dir_paths = ['keytext_dir']
    requirements = ['running_mode', 'data_source', 'keycode']
    for fl in file_paths + dir_paths + requirements:
        if not conf.get(fl):
            errors.append('Attribute (%s) not set' % fl)
    if conf.get('running_mode').lower() == 'encrypt' \
            and conf.get('data_source') != 'terminal':
        if not os.path.exists(conf.get('cleartext_file')):
            errors.append(
                'Cleartext file (%s) not found' % conf.get('ciphertext_file')
            )
    elif conf.get('running_mode').lower() == 'decrypt' \
            and conf.get('data_source') != 'terminal':
        if not os.path.exists(conf.get('ciphertext_file')):
            errors.append(
                'Ciphertext file (%s) not found' % conf.get('ciphertext_file')
            )
    if conf.get('running_mode').lower() not in ('encrypt', 'decrypt'):
        errors.append(
            'Invalid running mode specified (%s)' % conf.get('running_mode')
        )
    if conf.get('data_source') not in ('file', 'terminal'):
        errors.append(
            'Invalid data source specified (%s)' % conf.get('data_source')
        )
    action_result.update({'exit': len(errors) + 10, 'msg': '\n'.join(errors)})
    return False if errors else True

# GENERAL

@pysnooper.snoop()
def scan_directory_for_key_files(dir_path):
    directory_path = os.path.join(dir_path, '*.txt')
    text_files = [
        os.path.basename(fl) for fl in glob.glob(directory_path)
        if fl is not dir_path
    ]
    return text_files

@pysnooper.snoop()
def file2list(file_path):
    if not file_path or not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as fl:
        converted = fl.readlines()
    return converted

@pysnooper.snoop()
def write2file(*args, file_path=str(), mode='w', **kwargs):
    with open(file_path, mode, encoding='utf-8', errors='ignore') \
            as active_file:
        content = ''
        for line in args:
            content = content + str(line) + '\n'
        for line_key in kwargs:
            content = content + str(line_key) + '=' + str(kwargs[line_key]) + '\n'
        try:
            active_file.write(content)
        except UnicodeError as e:
            return False
    return True

def clear_screen():
    return os.system('cls' if os.name == 'nt' else 'clear')

@pysnooper.snoop()
def load_text_files(**context):
    key_files = scan_directory_for_key_files(context.get('keytext_dir'))
    return False if not key_files \
        else cache_text_file_content(*key_files, **context)

@pysnooper.snoop()
def build_key_file(**context):
    global key_file_cache
    build, code = [], [item for item in context.get('keycode').split() if item]
    if not code:
        return False
    for position in code:
        cache_key = [
            item for item in text_file_cache if position == item.rstrip('.txt')
        ]
        if not cache_key:
            continue
        content = text_file_cache[cache_key[0]]
        build = build + content
    key_file_cache.update({context.get('keytext_file'): build})
    return write2file(*build, file_path=context.get('keytext_file'))

# CACHERS

# TODO
def cache_keytext_file(file_path, **context):
#   keyfile_chapter_cache = []                              # [['chapter', 'lines', ...], ...]
#   keyfile_line_cache = {}                                 # {'1': {'1': ['line', 'text', ...], '2': [], ...}, '2': {}, ...}
#   cleartext_cache = {}                                    # {'a': ['10-14-23', 13-1-32, ...]}
#   ciphertext_cache = {}                                   # {'10-14-23': 'a', ...}
    pass

@pysnooper.snoop()
def cache_text_file_content(*text_file_names, **context):
    global text_file_cache
    if not text_file_names:
        return False
    for fl_name in text_file_names:
        file_path = os.path.join(context.get('keytext_dir'), fl_name)
        if not os.path.exists(file_path):
            continue
        content = file2list(file_path)
        text_file_cache.update({fl_name: content})
    return text_file_cache

# ACTIONS

# TODO
def encrypt_cleartext(*data, **context) -> list:
#   cache_keytext_file(file_path, **context)
    return []
def decrypt_ciphertext(*data, **context) -> list:
#   cache_keytext_file(file_path, **context)
    return []

# FORMATTERS

def format_header():
    header = '''
_______________________________________________________________________________

  *               *             *  %s''' % SCRIPT_NAME + '''  *              *             *
_______________________________________________________v%s%s_____________''' % (VERSION, VERSION_NAME) + '''
           Excellent Regards, the Alveare Solutions #!/Society -x
    '''
    return header

# DISPLAY

def display2terminal(*lines):
    return False if not lines else print('\n'.join(lines))

def display_header():
    return print(format_header())

# CREATORS

@pysnooper.snoop()
def create_command_line_parser():
    parser = optparse.OptionParser(
        'BlueCipher Encryption/Decryption -\n\n'
        '    [ Ex ]: Terminal based running mode\n'
        '       ~$ %prog \n\n'
        '    [ Ex ]: File based running mode decryption\n'
        '       ~$ %prog \ \n'
        '           --action=decrypt \ \n'
        '           --key-code=123456 \ \n'
        '           --ciphertext-file=bc_cipher.txt \ \n'
        '           --keytext-dir=text\n\n'
        '    [ Ex ]: File based running mode encryption\n'
        '       ~$ %prog \ \n'
        '           --action=encrypt \ \n'
        '           --key-code=123456 \ \n'
        '           --cleartext-file=bc_clear.txt \ \n'
        '           --keytext-dir=text'
    )
    return parser

# PARSERS

@pysnooper.snoop()
def process_command_line_options(parser, **context):
#   global CONFIG
    (options, args) = parser.parse_args()
    to_update = {key: val for key, val in options.__dict__.items() if val}
#   CONFIG.update(to_update)
    context.update(to_update)
    return to_update

@pysnooper.snoop()
def add_command_line_parser_options(parser):
    parser.add_option(
        '-a', '--action', dest='action', type='string',
        help='Specify the desired action - encryption or decryption.',
    )
    parser.add_option(
        '-k', '--key-code', dest='key_code', type='string',
        help='Specify password for text key.',
    )
    parser.add_option(
        '-c', '--cleartext-file', dest='cleartext_file', type='string',
        help='Path to the output or input (depends on action) cleartext file.'\
        'Default: ./bc_clear.txt'
    )
    parser.add_option(
        '-C', '--ciphertext-file', dest='ciphertext_file', type='string',
        help='Path to the output or input (depends on action) ciphertext file.'\
        'Default: ./bc_cipher.txt'
    )
    parser.add_option(
        '-d', '--text-dir', dest='text_dir', type='string',
        help='Path to the directory containing key text files.'
    )
    parser.add_option(
        '-s', '--data-src', dest='data_src', type='string',
        help='Specify if the input data source should be from a file or a terminal.'
    )
    return parser

@pysnooper.snoop()
def parse_cli_args(**context):
    parser = create_command_line_parser()
    add_command_line_parser_options(parser)
    return process_command_line_options(parser, **context)

# REPORTERS

def report_action_result(result, **context):
    print(
        '[ OUTPUT ]: %s' % str(action_result.get('output')),
        '[ MSG ]: %s' % str(action_result.get('msg')),
        '[ EXIT ]: %s' % str(action_result.get('exit')), sep='\n'
    )
    return write2file(
        json.dumps(action_result, indent=4),
        file_path=context.get('report_file')
    )

# INIT

@pysnooper.snoop()
def init_terminal_running_mode(**conf):
    global action_result
    while True:
        keycode = fetch_keycode_from_user()
        if not keycode:
            action_result.update({
                'exit': 0,
                'msg': 'Action aborted at keycode prompt'
            })
            break
        action = fetch_running_mode_from_user()
        if not action:
            action_result.update({
                'exit': 0,
                'msg': 'Action aborted at running mode prompt'
            })
            break
        data = fetch_data_from_user()
        if not data:
            action_result.update({
                'exit': 0,
                'msg': 'Action aborted at data input prompt'
            })
            break
        build = build_key_file(**conf)
        if not build:
            action_result.update({
                'exit': 3,
                'msg': 'Could not build key file %s' % conf.get('keytext_file')
            })
        handlers = {
            'encrypt': encrypt_cleartext,
            'decrypt': decrypt_ciphertext,
        }
        if conf.get('running_mode') not in handlers:
            action_result.update({
                'exit': 4,
                'msg': 'Invalid running mode %s' % conf.get('running_mode')
            })
            return action_result['exit']
        action = handlers[CONFIG['running_mode']](*data, **conf)
        action_result.update({'output': action})
        if not action:
            action_result.update({
                'exit': 5,
                'msg': 'Action %s failed' % conf.get('running_mode')
            })
        display = display2terminal(*action)
        if not display:
            action_result.update({
                'exit': 7,
                'msg': 'Could not display action result'
            })
        replay = fetch_replay_confirmation_from_user()
        if not replay:
            break
        clear = clear_screen()
    return action_result['exit']

@pysnooper.snoop()
def init_file_running_mode(**conf):
    global action_result
    if not conf.get('keycode'):
        keycode = fetch_keycode_from_user()
    src_file = conf.get('ciphertext_file') if conf.get('running_mode') \
        is 'decrypt' else conf.get('cleartext_file')
    data = file2list(src_file)
    if not data:
        action_result.update({
            'exit': 2,
            'msg': 'Could not fetch source data from file %s' % src_file
        })
        return action_result['exit']
    build = build_key_file(**conf)
    if not build:
        action_result.update({
            'exit': 3,
            'msg': 'Could not build key file %s' % conf.get('keytext_file')
        })
        return action_result['exit']
    handlers = {
        'encrypt': encrypt_cleartext,
        'decrypt': decrypt_ciphertext,
    }
    if conf.get('running_mode') not in handlers:
        action_result.update({
            'exit': 4,
            'msg': 'Invalid running mode %s' % conf.get('running_mode')
        })
        return action_result['exit']
    action = handlers[CONFIG['running_mode']](*data, **conf)
    action_result.update({'output': action})
    if not action:
        action_result.update({
            'exit': 5,
            'msg': 'Action %s failed' % conf.get('running_mode')
        })
    else:
        action_result.update({'output': action})
    out_file = conf.get('cleartext_file') if conf.get('running_mode') \
        is 'decrypt' else conf.get('ciphertext_file')
    write = write2file(**action, file_path=out_file)
    if not write:
        action_result.update({
            'exit': 6,
            'msg': 'Could not write to out file %s' % out_file
        })
    display = display2terminal(*action)
    if not display:
        action_result.update({
            'exit': 7,
            'msg': 'Could not display action result'
        })
    return action_result['exit']

@pysnooper.snoop()
def init(**conf):
    global action_result
    cli_parse = parse_cli_args(**conf)
    conf['data_source'] = 'terminal' if not cli_parse else 'file'
    load = load_text_files(**conf)
    check = check_preconditions(**conf)
    if not check:
        details = action_result.get('msg', '')
        action_result.update({
            'exit': 1,
            'msg': 'Action preconditions check failed for running mode '\
                '%s. Details: %s' % (conf.get('running_mode'), details)
        })
        return action_result['exit']
    if not cli_parse or conf.get('data_source').lower() == 'terminal':
        run = init_terminal_running_mode(**conf)
    else:
        run = init_file_running_mode(**conf)
    return action_result['exit']

if __name__ == '__main__':
    display_header()
    try:
        EXIT_CODE = init(**CONFIG)
    except Exception as e:
        EXIT_CODE = 10
        action_result.update({'exit': EXIT_CODE, 'msg': str(e)})
    if CONFIG.get('report'):
        print('[ REPORT ]: Generating (%s)...' % CONFIG.get('report_file'))
        report = report_action_result(action_result, **CONFIG)
        if not report:
            EXIT_CODE = 20
    print('[ DONE ]: Terminating with exit code (%s)' % str(EXIT_CODE))
    exit(EXIT_CODE)

