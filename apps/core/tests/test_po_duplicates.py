"""Catalogs must compile: duplicate msgid entries, including obsolete ones, break msgfmt."""
import ast
from pathlib import Path

from django.test import SimpleTestCase

LOCALE_DIR = Path(__file__).resolve().parents[3] / 'locale'


def _unquote(token):
    return ast.literal_eval(token)


def _read_string(lines, index, obsolete):
    """Read a PO string that starts on lines[index], including continuation quotes."""
    prefix = '#~ ' if obsolete else ''
    line = lines[index]
    body = line[len(prefix):] if obsolete else line
    field, quoted = body.split(' ', 1)
    parts = [_unquote(quoted.strip())]
    index += 1
    while index < len(lines):
        nxt = lines[index]
        cont = nxt.startswith('#~ "') if obsolete else nxt.startswith('"')
        if not cont:
            break
        chunk = nxt[3:] if obsolete else nxt
        parts.append(_unquote(chunk.strip()))
        index += 1
    return field, ''.join(parts), index


def duplicate_message_keys(text):
    """Return (msgctxt, msgid) pairs that occur more than once, obsolete entries included."""
    lines = text.splitlines()
    seen = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        obsolete = line.startswith('#~ ')
        bare = line[3:] if obsolete else line
        if bare.startswith('msgctxt ') or bare.startswith('msgid '):
            context = ''
            if bare.startswith('msgctxt '):
                _, context, index = _read_string(lines, index, obsolete)
                if index >= len(lines):
                    break
                bare = lines[index][3:] if lines[index].startswith('#~ ') else lines[index]
                obsolete = lines[index].startswith('#~ ')
            if not bare.startswith('msgid '):
                index += 1
                continue
            _, msgid, index = _read_string(lines, index, obsolete)
            if index < len(lines):
                nxt = lines[index][3:] if lines[index].startswith('#~ ') else lines[index]
                if nxt.startswith('msgid_plural '):
                    _, _, index = _read_string(lines, index, lines[index].startswith('#~ '))
            key = (context, msgid)
            seen.setdefault(key, 0)
            seen[key] += 1
            continue
        index += 1
    return sorted(key for key, count in seen.items() if count > 1 and key[1] != '')


class PoDuplicateTests(SimpleTestCase):
    def test_parser_flags_obsolete_duplicate(self):
        sample = '\n'.join([
            'msgid "Hello"',
            'msgstr "Hi"',
            '',
            '#~ msgid "Hello"',
            '#~ msgstr "Hi"',
        ])
        self.assertEqual(duplicate_message_keys(sample), [('', 'Hello')])

    def test_parser_keeps_msgctxt_apart(self):
        sample = '\n'.join([
            'msgid "Hello"',
            'msgstr "Hi"',
            '',
            'msgctxt "corp"',
            'msgid "Hello"',
            'msgstr "Hey"',
        ])
        self.assertEqual(duplicate_message_keys(sample), [])

    def test_catalogs_have_no_duplicate_messages(self):
        paths = sorted(LOCALE_DIR.glob('*/LC_MESSAGES/django.po'))
        self.assertGreaterEqual(len(paths), 3)
        for path in paths:
            with self.subTest(catalog=path.parent.parent.name):
                dupes = duplicate_message_keys(path.read_text(encoding='utf-8'))
                self.assertEqual(dupes, [], path)
