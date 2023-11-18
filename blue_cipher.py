#!/usr/bin/python3
#
# Excellent Regards, the Alveare Solutions #!/Society -x
#
# Blue Cipher Enryptor/Decryptor

import optparse
import os
import glob
import json
import pysnooper

SCRIPT_NAME = 'BlueCipher'
VERSION = '1.0'
VERSION_NAME = 'Orbital'
CURRENT_DIR = os.getcwd()
CONFIG = {
    'config_file': '',
    'current_dir': CURRENT_DIR,
    'keytext_dir': '%s/dta/text' % CURRENT_DIR,
    'keytext_file': '%s/bc_key.txt' % CURRENT_DIR,
    'cleartext_file': '%s/bc_clear.txt' % CURRENT_DIR,
    'ciphertext_file': '%s/bc_cipher.txt' % CURRENT_DIR,
    'report_file': '%s/bc_report.dump' % CURRENT_DIR,
    'running_mode': 'decrypt',                                                  # <decrypt|encrypt>
    'data_source': 'file',                                                      # <file|terminal>
    'keycode': '123456',                                                        # Order of concatenated keytext chapter files
    'cleanup': ['keytext_file'],                                                # CONFIG keys containing file paths
    'full_cleanup': [
        'keytext_file', 'cleartext_file', 'ciphertext_file', 'report_file'
    ],
    'report': True,
    'silent': False,
}
keytext_file_cache = []                                                         # ['line1', 'line2', ...]
keyfile_page_cache = []                                                         # [['chapter', 'lines', ...], ...]
keyfile_line_cache = {}                                                         # {'1': {'1': ['line', 'text', ...], '2': [], ...}, '2': {}, ...}
text_file_cache = {}                                                            # {'file_name': ['file', 'lines', '', ...], ...}
ciphertext_cache = {}                                                           # {'10-14-23': 'a', ...}
cleartext_cache = {}                                                            # {'a': ['10-14-23', 13-1-32, ...]}
encryption_cache = {}                                                           # {'a': {'last': '10-14-24', 'used': [1-1-1, ...]}, ...}
action_result = {'input': [], 'output': [], 'msg': '', 'exit': 0}

# FETCHERS

def fetch_running_mode_from_user(prompt='Action'):
    global CONFIG
    stdout_msg('Specify action or (.back)...', info=True)
    if CONFIG.get('running_mode'):
        prompt = prompt + '[' + CONFIG['running_mode'] + ']> '
        print(
            '[ INFO ]: Leave blank to keep current '\
            '(%s)' % CONFIG['running_mode']
        )
    stdout_msg('1) Encrypt cleartext\n2) Decrypt ciphertext\n3) Disk Cleanup')
    selection_map = {'1': 'encrypt', '2': 'decrypt', '3': 'cleanup'}
    while True:
        selection = input(prompt)
        if not selection:
            if not CONFIG.get('running_mode'):
                continue
            selection = [k for k, v in selection_map.items() \
                if v == CONFIG.get('running_mode')][0]
        if selection == '.back':
            return
        if selection not in ('1', '2', '3'):
            print('[ ERROR ]: Invalid selection (%s)' % selection)
        CONFIG['running_mode'] = selection_map[selection]
        break
    print()
    return selection_map[selection]

def fetch_data_from_user(prompt='Data'):
    stdout_msg(
        'Specify input data for action '\
        '(%s) or (.back)...' % CONFIG.get('running_mode', ''), info=True
    )
    if CONFIG.get('running_mode') in ('encrypt', 'decrypt', 'cleanup'):
        prompt = prompt + '[' + CONFIG['running_mode'] + ']'
    while True:
        data = input(prompt + '> ')
        if not data:
            continue
        if data == '.back':
            return
        break
    print()
    return data

def fetch_replay_confirmation_from_user(prompt='Replay'):
    stdout_msg(
        '[ Q/A ]: Do you want to go again?', silence=CONFIG.get('silent')
    )
    while True:
        answer = input(prompt + '[Y/N]> ')
        if not answer:
            continue
        if answer.lower() not in ('y', 'n', 'yes', 'no', 'yeah', 'nah'):
            stdout_msg(
                'Invalid answer (%s)' % answer, err=True,
                silence=CONFIG.get('silent')
            )
            continue
        break
    print()
    return True if answer in ('y', 'yes', 'yeah') else False

def fetch_keycode_from_user(prompt='KeyCode'):
    global CONFIG
    stdout_msg(
        'Specify text keycode sequence or (.back)...', info=True,
        silence=CONFIG.get('silent')
    )
    if CONFIG.get('keycode'):
        prompt = prompt + '[' + CONFIG['keycode'] + ']> '
        stdout_msg(
            'Leave blank to keep current '\
            '(%s)' % CONFIG['keycode'], info=True, silence=CONFIG.get('silent')
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
    print()
    return code

# CHECKERS

#@pysnooper.snoop()
def check_preconditions(**conf):
    errors = []
    file_paths = ['keytext_file', 'cleartext_file', 'ciphertext_file']
    dir_paths = ['keytext_dir']
    requirements = ['running_mode', 'data_source', 'keycode']
    for fl in file_paths + dir_paths + requirements:
        if not conf.get(fl):
            errors.append('Attribute (%s) not set' % fl)
    if conf.get('running_mode', '').lower() == 'encrypt' \
            and conf.get('data_source') != 'terminal':
        if not os.path.exists(conf.get('cleartext_file')):
            errors.append(
                'Cleartext file (%s) not found' % conf.get('ciphertext_file')
            )
    elif conf.get('running_mode', '').lower() == 'decrypt' \
            and conf.get('data_source') != 'terminal':
        if not os.path.exists(conf.get('ciphertext_file')):
            errors.append(
                'Ciphertext file (%s) not found' % conf.get('ciphertext_file')
            )
    if conf.get('running_mode', '').lower() not in ('encrypt', 'decrypt', 'cleanup'):
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

#@pysnooper.snoop()
def load_config(file_path):
    global CONFIG
    if not file_path or not os.path.exists(file_path):
        return
    with open(file_path, 'r') as fl:
        CONFIG.update(json.load(fl))
    return CONFIG

#@pysnooper.snoop()
def scan_directory_for_key_files(dir_path):
    if not dir_path:
        return False
    directory_path = os.path.join(dir_path, '*.txt')
    text_files = [
        os.path.basename(fl) for fl in glob.glob(directory_path)
        if fl is not dir_path
    ]
    return text_files

#@pysnooper.snoop()
def file2list(file_path):
    if not file_path or not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as fl:
        converted = fl.readlines()
    return converted

#@pysnooper.snoop()
def write2file(*args, file_path=str(), mode='w', **kwargs):
    with open(file_path, mode, encoding='utf-8', errors='ignore') \
            as active_file:
        content = ''
        for line in args:
            content = content + (
                str(line) if '\n' in line else str(line) + '\n'
            )
        for line_key in kwargs:
            content = content + \
                str(line_key) + '=' + str(kwargs[line_key]) + '\n'
        try:
            active_file.write(content)
        except UnicodeError as e:
            return False
    return True

def clear_screen():
    return os.system('cls' if os.name == 'nt' else 'clear')

def stdout_msg(message, silence=False, red=False, info=False, warn=False,
               err=False, done=False, bold=False, green=False, ok=False, nok=False):
    if red:
        display_line = '\033[91m' + str(message) + '\033[0m'
    elif green:
        display_line = '\033[1;32m' + str(message) + '\033[0m'
    elif ok:
        display_line = '[ ' + '\033[1;32m' + 'OK' + '\033[0m' + ' ]: ' \
            + '\033[92m' + str(message) + '\033[0m'
    elif nok:
        display_line = '[ ' + '\033[91m' + 'NOK' + '\033[0m' + ' ]: ' \
            + '\033[91m' + str(message) + '\033[0m'
    elif info:
        display_line = '[ INFO ]: ' + str(message)
    elif warn:
        display_line = '[ ' + '\033[91m' + 'WARNING' + '\033[0m' + ' ]: ' \
            + '\033[91m' + str(message) + '\x1b[0m'
    elif err:
        display_line = '[ ' + '\033[91m' + 'ERROR' + '\033[0m' + ' ]: ' \
            + '\033[91m' + str(message) + '\033[0m'
    elif done:
        display_line = '[ ' + '\x1b[1;34m' + 'DONE' + '\033[0m' + ' ]: ' \
            + str(message)
    elif bold:
        display_line = '\x1b[1;37m' + str(message) + '\x1b[0m'
    else:
        display_line = message
    if silence:
        return False
    print(display_line)
    return True

#@pysnooper.snoop()
def load_text_files(**context):
    key_files = scan_directory_for_key_files(context.get('keytext_dir'))
    return False if not key_files \
        else cache_chaptertext_file_content(*key_files, **context)

#@pysnooper.snoop()
def build_key_file(**context):
    global keytext_file_cache                                                   # ['line1', 'line2', ...]
    global text_file_cache                                                      # {'file_name': ['file', 'lines', '', ...], ...}
    build, code = [], [item for item in list(context.get('keycode', '')) if item]
    if not code:
        return False
    for position in code:
        cache_key = [
            item for item in text_file_cache if position == item.rstrip('.txt')
        ]
        if not cache_key:
            continue
        content = text_file_cache[cache_key[0]]
        build = build + content + ['\n']
    build = [item.rstrip('\n') if item != '\n' else item for item in build[:-1]]
    text_file_cache.update({context.get('keytext_file'): build})
    keytext_file_cache = build
    return write2file(*build, file_path=context.get('keytext_file'))

# CACHERS

#@pysnooper.snoop()
def cache_page_characters(**context):
    global keyfile_line_cache                                                   # {'1': {'1': ['line', 'text', ...], '2': [], ...}, '2': {}, ...}
    global cleartext_cache
    global ciphertext_cache
    cleartext_cache, ciphertext_cache, line_characters = {}, {}, {}
    for page in keyfile_line_cache:
        for line in keyfile_line_cache[page]:
            for index in range(len(keyfile_line_cache[page][line])):
                character = keyfile_line_cache[page][line][index].lower()
                if character in ('\n'):
                    continue
                code = f'{page}-{line}-''%s' % str(index + 1)
                if character not in line_characters:
                    line_characters.update({character: [code]})
                else:
                    line_characters[character].append(code)
            keyfile_line_cache[page].update({line: line_characters})
            line_characters = {}
    clear_cache = cache_cleartext(**context)
    cipher_cache = cache_ciphertext(**context)
    return keyfile_line_cache

#@pysnooper.snoop()
def cache_cleartext(**context):
    global keyfile_line_cache                                                   # {'1': {'1': ['line', 'text', ...], '2': [], ...}, '2': {}, ...}
    global cleartext_cache                                                      # {'a': ['10-14-23', 13-1-32, ...]}
    for page in keyfile_line_cache:
        for line in keyfile_line_cache[page]:
            for character in keyfile_line_cache[page][line]:
                if character in cleartext_cache:
                    cleartext_cache[character] = cleartext_cache[character] \
                        + keyfile_line_cache[page][line][character]
                    continue
                cleartext_cache[character] = keyfile_line_cache[page][line][character]
    return cleartext_cache

#@pysnooper.snoop()
def cache_ciphertext(**context):
    global ciphertext_cache                                                     # {'10-14-23': 'a', ...}
    for character in cleartext_cache:
        if not cleartext_cache[character]:
            continue
        ciphertext_cache.update({
            code: character for code in cleartext_cache[character]
        })
    return ciphertext_cache

#@pysnooper.snoop()
def cache_page_lines(**context):
    global keyfile_line_cache                                                   # {'1': {'1': ['line', 'text', ...], '2': [], ...}, '2': {}, ...}
    page_lines = {}
    for page in keyfile_line_cache:
        for i in range(len(keyfile_line_cache[page])):
            page_lines.update({str(i + 1): keyfile_line_cache[page][i]})
        keyfile_line_cache.update({page: page_lines})
        page_lines = {}
    return keyfile_line_cache

#@pysnooper.snoop()
def cache_keytext_pages(**context):
    global keyfile_page_cache                                                   # [['chapter', 'lines', ...], ...]
    global keyfile_line_cache                                                   # {'1': {'1': ['line', 'text', ...], '2': [], ...}, '2': {}, ...}
    keyfile_page_cache, keyfile_line_cache, page_builder = [], {}, []
    for line in keytext_file_cache:
        if line == '\n':
            keyfile_page_cache.append(page_builder)
            page_builder = []
            continue
        page_builder.append(line)
    for i in range(len(keyfile_page_cache)):
        keyfile_line_cache.update({str(i + 1): keyfile_page_cache[i]})
    return keyfile_line_cache

#@pysnooper.snoop()
def cache_keytext_file(file_path, **context):
    if not keytext_file_cache:
        build = build_key_file(**context)
        if not build:
            return False
    page_cache = cache_keytext_pages(**context)
    if not page_cache:
        return False
    line_cache = cache_page_lines(**context)
    if not line_cache:
        return False
    char_cache = cache_page_characters(**context)
    return line_cache if char_cache else False

#@pysnooper.snoop()
def cache_chaptertext_file_content(*text_file_names, **context):
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

#@pysnooper.snoop()
def encrypt_cleartext(*data, **context) -> list:
    '''
    [ INPUT  ]: data = ['first clear text', 'second clear text', ...]
    [ RETURN ]: ['1-1-1,1-2-3,..', '11-12-13,21-22-23,...', ...]
    '''
    global action_result
    global encryption_cache                                                     # {'a': {'last': '10-14-24', 'used': [1-1-1, ...]}, ...}
    cache = cache_keytext_file(context.get('keytext_file'), **context)
    ciphertext, failures = [], 0
    for line in data:
        encrypted_cipher = []
        for character in list(line):
            if character not in cleartext_cache:
                encrypted_cipher.append(character)
                failures += 1
                continue
            if character not in encryption_cache:
                encryption_cache.update({character: {'last': '', 'used': []}})
            for code in cleartext_cache[character]:
                if code in encryption_cache[character]['used']:
                    continue
                encryption_cache[character]['last'] = code
                encryption_cache[character]['used'].append(code)
                encrypted_cipher.append(code)
                break
        ciphertext.append(','.join(encrypted_cipher))
    action_result = {
        'input': data,
        'output': ciphertext,
        'msg': 'OK: Encryption successful' if ciphertext and not failures \
            else 'NOK: Encryption failures detected (%s)' % failures,
        'exit': 0 if ciphertext and not failures else 9,
    }
    return ciphertext

#@pysnooper.snoop()
def decrypt_ciphertext(*data, **context) -> list:
    '''
    [ INPUT  ]: data = ['1-1-1,1-2-3,..', '11-12-13,21-22-23,...', ...]
    [ RETURN ]: ['first decrypted text', 'second decrypted text', ...]
    '''
    global action_result
    cache = cache_keytext_file(context.get('keytext_file'), **context)
    cleartext, failures = [], 0
    for cipher in data:
        decrypted_cipher = []
        character_set = [item for item in cipher.split(',') if item]
        for char_code in character_set:
            if char_code not in ciphertext_cache:
                decrypted_cipher.append(char_code)
                failures += 1
                continue
            decrypted_cipher.append(ciphertext_cache[char_code])
        cleartext.append(''.join(decrypted_cipher))
    action_result = {
        'input': data,
        'output': cleartext,
        'msg': 'OK: Decryption successful' if cleartext and not failures \
            else 'NOK: Decryption failures detected (%s)' % failures,
        'exit': 0 if cleartext and not failures else 9,
    }
    return cleartext

# FORMATTERS

def format_header():
    header = '''
_______________________________________________________________________________

  *               *             *  %s''' % SCRIPT_NAME + '''  *              *             *
________________________________________________________v%s%s____________''' % (VERSION, VERSION_NAME) + '''
              Excellent Regards, the Alveare Solutions #!/Society -x
    '''
    return header

# DISPLAY

#@pysnooper.snoop()
def display2terminal(*lines, result=False, **context):
    if (not lines and not result) or context.get('silent'):
        return True
    if result:
        stdout_msg(
            '[ %s ]: %s Action Result' % (
                CONFIG.get('running_mode', '').upper(), SCRIPT_NAME
            ), silence=context.get('silent')
        )
        stdout_msg(
            json.dumps(action_result, indent=4), silence=context.get('silent')
        )
    else:
        stdout_msg('\n'.join(lines) + '\n', silence=context.get('silent'))
    print()
    return True

#@pysnooper.snoop()
def display_header(**context):
    if context.get('silent'):
        return False
    stdout_msg(format_header())
    return True

# CREATORS

#@pysnooper.snoop()
def create_command_line_parser():
    parser = optparse.OptionParser(
        format_header() + '\n[ DESCRIPTION ]: BlueCipher Encryption/Decryption -\n\n'
        '    [ Ex ]: Terminal based running mode\n'
        '       ~$ %prog \n\n'
        '    [ Ex ]: File based running mode decryption\n'
        '       ~$ %prog \ \n'
        '           --action decrypt \ \n'
        '           --key-code 123456 \ \n'
        '           --ciphertext-file bc_cipher.txt \ \n'
        '           --keytext-dir text\n\n'
        '    [ Ex ]: File based running mode encryption with no STDOUT\n'
        '       ~$ %prog \ \n'
        '           --action encrypt \ \n'
        '           --key-code 123456 \ \n'
        '           --cleartext-file bc_clear.txt \ \n'
        '           --keytext-dir text \ \n'
        '           --silent\n\n'
        '   [ Ex ]: Run with context data from JSON config file\n'
        '       ~$ %prog \ \n'
        '           --konfig-file conf/blue_cipher.conf.json\n\n'
        '   [ Ex ]: Cleanup all generated files from disk\n'
        '       ~$ %prog \ \n'
        '           --action cleanup'
    )
    return parser

# PARSERS

#@pysnooper.snoop()
def process_command_line_options(parser, **context):
    global CONFIG
    (options, args) = parser.parse_args()
    if options.config_file:
        return load_config(options.config_file)
    to_update = {key: val for key, val in options.__dict__.items() if val}
    CONFIG.update(to_update)
    return to_update

#@pysnooper.snoop()
def add_command_line_parser_options(parser):
    parser.add_option(
        '-a', '--action', dest='running_mode', type='string',
        help='Specify the desired action. Options: <encrypt|decrypt|cleanup>',
    )
    parser.add_option(
        '-k', '--key-code', dest='keycode', type='string',
        help='Specify password for text key.',
    )
    parser.add_option(
        '-c', '--cleartext-file', dest='cleartext_file', type='string',
        help='Path to the output or input (depends on action) cleartext file. '
            'Default: ./bc_clear.txt'
    )
    parser.add_option(
        '-C', '--ciphertext-file', dest='ciphertext_file', type='string',
        help='Path to the output or input (depends on action) ciphertext file. '
            'Default: ./bc_cipher.txt'
    )
    parser.add_option(
        '-d', '--keytext-dir', dest='keytext_dir', type='string',
        help='Path to the directory containing key text files. Default: ./text'
    )
    parser.add_option(
        '-s', '--data-src', dest='data_source', type='string',
        help='Specify if the input data source. Options: <file|terminal>, '
            'Default: file'
    )
    parser.add_option(
        '-K', '--konfig-file', dest='config_file', type=str,
        help='Path to the %s configuration file.' % SCRIPT_NAME
    )
    parser.add_option(
        '-S', '--silent', dest='silent', action='store_true',
        help='Run with no STDOUT output. Implies a file data source.'
    )
    return parser

#@pysnooper.snoop()
def parse_cli_args(**context):
    parser = create_command_line_parser()
    add_command_line_parser_options(parser)
    return process_command_line_options(parser, **context)

# REPORTERS

def report_action_result(result, **context):
    return write2file(
        json.dumps(action_result, indent=4),
        file_path=context.get('report_file')
    )

# CLEANERS

#@pysnooper.snoop()
def cleanup(full=False, **context):
    global CONFIG
    global action_result
    to_remove = [
        context.get(label, '')
        for label in context['cleanup' if not full else 'full_cleanup']
    ]
    try:
        for file_path in to_remove:
            if not os.path.exists(file_path):
                continue
            os.remove(file_path)
        if full:
            CONFIG.update({'report': False})
    except OSError as e:
        action_result.update({
            'msg': 'Cleanup error! Details: %s' % str(e),
            'exit': 8,
        })
        return False
    return True

# SETUP

#@pysnooper.snoop()
def setup(**context):
    global action_result
    file_paths = ['keytext_file', 'cleartext_file', 'ciphertext_file']
    dir_paths = ['keytext_dir']
    errors = []
    for fl_path in file_paths:
        if fl_path not in context or os.path.exists(context[fl_path]):
            continue
        try:
            create = write2file('', mode='a', file_path=context[fl_path])
        except Exception as e:
            errors.append(str(e))
    for dir_path in dir_paths:
        if dir_path not in context or os.path.exists(context[dir_path]):
            continue
        try:
            create = os.makedirs(context[dir_path], exist_ok=True)
        except Exception as e:
            errors.append(str(e))
    if errors:
        action_result.update({
            'msg': '%s Setup failed ' % SCRIPT_NAME +
                'with (%d) errors! Details: ' % len(errors) + ','.join(errors),
            'exit': 11,
        })
    return True if not errors else False

# INIT

#@pysnooper.snoop()
def init_terminal_running_mode(**conf):
    global action_result
    while True:
        action = fetch_running_mode_from_user()
        if not action:
            action_result.update({
                'exit': 0,
                'msg': 'Action aborted at running mode prompt'
            })
            break
        if action == 'cleanup':
            clean = cleanup(full=True, **conf)
            clear = clear_screen()
            display_header(**conf)
            continue
        keycode = fetch_keycode_from_user()
        if not keycode:
            action_result.update({
                'exit': 0,
                'msg': 'Action aborted at keycode prompt'
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
        action = handlers[CONFIG['running_mode']](data, **conf)
        if not action:
            action_result.update({
                'exit': 5,
                'msg': 'Action %s failed' % conf.get('running_mode')
            })
        display = display2terminal(result=True, **conf)
        if not display:
            action_result.update({
                'exit': 7,
                'msg': 'Could not display action result'
            })
        replay = fetch_replay_confirmation_from_user()
        if not replay:
            break
        clear = clear_screen()
        display_header(**conf)
    return action_result['exit']

#@pysnooper.snoop()
def init_file_running_mode(**conf):
    global action_result
    if not conf.get('keycode'):
        keycode = fetch_keycode_from_user()
    src_file = conf.get('ciphertext_file') if conf.get('running_mode') \
        == 'decrypt' else conf.get('cleartext_file')
    data = [
        item.rstrip('\n') if item != '\n' else item for item in file2list(src_file)
    ]
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
    if not action:
        action_result.update({
            'exit': 5,
            'msg': 'Action %s failed' % conf.get('running_mode')
        })
    else:
        action_result.update({'output': action})
    out_file = conf.get('cleartext_file') if conf.get('running_mode') \
        == 'decrypt' else conf.get('ciphertext_file')
    write = write2file(*action, file_path=out_file)
    if not write:
        action_result.update({
            'exit': 6,
            'msg': 'Could not write to out file %s' % out_file
        })
    display = display2terminal(result=True, **conf)
    if not display:
        action_result.update({
            'exit': 7,
            'msg': 'Could not display action result'
        })
    return action_result['exit']

#@pysnooper.snoop()
def init():
    global CONFIG
    global action_result
    cli_parse = parse_cli_args(**CONFIG)
    CONFIG['data_source'] = 'terminal' if not cli_parse \
        and not CONFIG['data_source'] else 'file'
    display_header(**CONFIG)
    stdout_msg(
        '[ INIT ]: %s v%s %s' % (SCRIPT_NAME, VERSION, VERSION_NAME),
        silence=CONFIG.get('silent')
    )
    try:
        if CONFIG.get('running_mode', '').lower() == 'cleanup':
            stdout_msg(
                '[ ACTION ]: Cleaning up files from disk...',
                silence=CONFIG.get('silent')
            )
            clean = cleanup(full=True, **CONFIG)
            stdout_msg(
                'Terminating with exit code (%s)' % str(action_result['exit']),
                silence=CONFIG.get('silent'), done=True
            )
            exit(action_result['exit'])
        load = load_text_files(**CONFIG)
        lock_n_load = setup(**CONFIG)
        check = check_preconditions(**CONFIG)
        if not check:
            details = action_result.get('msg', '')
            action_result.update({
                'msg': 'Action preconditions check failed for running mode '\
                    '%s. Details: %s' % (CONFIG.get('running_mode'), details),
                'exit': 1,
            })
            exit(action_result['exit'])
        if not cli_parse or CONFIG.get('data_source').lower() == 'terminal':
            run = init_terminal_running_mode(**CONFIG)
        else:
            run = init_file_running_mode(**CONFIG)
    except Exception as e:
        action_result.update({'msg': str(e), 'exit': 10})
    finally:
        if CONFIG.get('cleanup'):
            clean = cleanup(**CONFIG)
        if CONFIG.get('report'):
            report = report_action_result(action_result, **CONFIG)
            if not report:
                action_result.update({
                    'msg': 'Failed to generate report %s'
                        % CONFIG.get('report_file'),
                    'exit': 20,
                })
    print(); stdout_msg(
        'Terminating with exit code (%s)' % str(action_result['exit']),
        silence=CONFIG.get('silent'), done=True
    )
    exit(action_result['exit'])


if __name__ == '__main__':
    init()

