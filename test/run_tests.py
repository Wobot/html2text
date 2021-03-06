import codecs
import glob
import os
import re
import subprocess
import sys

sys.path.insert(0, '..')
import html2text


def test_module(fn, unicode_snob=False, google_doc=False):
    print_conditions('module', unicode_snob, google_doc)

    h = html2text.HTML2Text()

    if unicode_snob:
        h.unicode_snob = True

    if google_doc:
        h.google_doc = True
        h.ul_item_mark = '-'
        h.body_width = 0
        h.hide_strikethrough = True

    result = get_baseline(fn, unicode_snob)
    actual = h.handle(file(fn).read())
    return print_result(fn, 'module', result, actual)


def test_command(fn, google_doc=False):
    print_conditions('command', False, google_doc)

    cmd = [sys.executable or 'python', '../html2text.py']
    if fn.lower().startswith('google'):
        cmd += ['-g', '-d', '-b', '0', '-s']
    cmd += [fn]

    result = get_baseline(fn)
    actual = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read()

    if os.name == 'nt':
        # Fix the unwanted CR to CRCRLF replacement
        # during text pipelining on Windows/cygwin
        actual = re.sub(r'\r+', '\r', actual)
        actual = actual.replace('\r\n', '\n')

    return print_result(fn, 'command', result, actual)


def print_conditions(mode, unicode_snob, google_doc):
    format = " * %s, unicode_snob=%d, google_doc=%d: "
    sys.stdout.write(format % (mode, int(unicode_snob), int(google_doc)))


def print_result(fn, mode, result, actual):
    if result == actual:
        print('PASS')
        return True
    else:
        print('FAIL')

        if mode == 'command':
            print(len(result), len(actual))

        dump_name = get_dump_name(fn, mode)

        f = codecs.open(dump_name, encoding='utf-8', mode='w+')
        f.write(actual)

        print("  Use: diff -u %s %s" % (get_baseline_name(fn), dump_name))
        return False


def get_dump_name(fn, suffix):
    return '%s-%s_output.md' % (os.path.splitext(fn)[0], suffix)


def get_baseline_name(fn):
    return os.path.splitext(fn)[0] + '.md'


def get_baseline(fn, unicode_snob=False):
    name = get_baseline_name(fn)
    if unicode_snob:
        f = codecs.open(name, mode='r', encoding='utf8')
        return f.read()
    else:
        return unicode(open(name).read())


def run_all_tests():
    html_files = glob.glob("*.html")
    passing = True
    for fn in html_files:
        google_doc = fn.lower().startswith('google')
        unicode_snob = fn.lower().find('unicode') > 0

        print('\n' + fn + ':')
        passing = passing and test_module(fn, unicode_snob, google_doc)

        if not unicode_snob:
            # (Because there is no command-line option to control unicode_snob)
            passing = passing and test_command(fn, google_doc=google_doc)
    if passing:
        print("ALL TESTS PASSED")
    else:
        print("Fail.")
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()
