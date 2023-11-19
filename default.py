#!/usr/bin/env python3
# vim: set ts=4 sw=4 et smartindent ignorecase fileencoding=utf8:

# 下記項目を埋めてconfig.pyにコピーする
IMAP_SERVER = 'localhost'
IMAP_USER = None
IMAP_PASSWORD = None

# データが16kbyteを超えると「max atom size too small」エラーで落ちる
# 一つの数字を10桁ぐらいとして1300個ぐらいが上限？だと思われるので1000個ずつに分ける
IMAP_MAX_DATA = 1000

INBOX_NAME = 'INBOX'
TRASH_NAME = 'Trash'
TRASH_PATH = '.'.join([INBOX_NAME, TRASH_NAME])

DEBUG = False