#!/usr/bin/env python3
# vim: set ts=4 sw=4 et smartindent ignorecase fileencoding=utf8:

# データが16kbyteを超えると「max atom size too small」エラーで落ちる
# 一つの数字を10桁ぐらいとして1300個ぐらいが上限？だと思われるので1000個ずつに分ける
IMAP_MAX_DATA = 1000
INI_FILE = 'config.ini'

DEBUG = False