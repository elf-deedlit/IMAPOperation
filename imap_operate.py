#!/usr/bin/env python3
# vim: set ts=4 sw=4 et smartindent ignorecase fileencoding=utf8:
import argparse
# https://imapclient.readthedocs.io/en/3.0.0/api.html
# pip install imapclient
import imapclient
import sys

from urllib.parse import unquote
from datetime import date, timedelta
try:
    from config import *
except ImportError:
    print('default.pyの項目を埋めてconfig.pyにコピーしてください')
    sys.exit(1)

if (IMAP_USER is None) or (IMAP_PASSWORD is None):
    print('config.pyのIMAP_USERとIMAP_PASSWORDを設定してください')
    sys.exit(1)

def trash_cleanup(imap, args: list) -> None:
    '''指定日以前のゴミ箱を消す'''
    try:
        days = int(args[0])
    except (IndexError, ValueError) as err:
        print('ゴミ箱の日にちが指定されていない')
        print(args)
        print(err)
        return
    dt = date.today() - timedelta(days = days)
    if DEBUG:
        print(f'{TRASH_PATH}: before {dt.year:04d}/{dt.month:02d}/{dt.day:02d}')
    imap.select_folder(TRASH_PATH)
    data = imap.search(['SEEN', 'BEFORE', dt])
    if len(data) < 1:
        if DEBUG:
            print(f'{dt.year:04d}/{dt.month:02d}/{dt.day:02d}以前のメールはゴミ箱にありません')
        return
    # 1000個ずつに分ける            
    if DEBUG:
        num = len(data)
        print(f'delete trash {num}')
    s = 0
    while s < len(data):
        datas = data[s:s + IMAP_MAX_DATA]
        if DEBUG:
            e = s + len(datas)
            print(f'start delete trash: {s}-{e}')
        imap.delete_messages(datas)
        s += IMAP_MAX_DATA
    imap.close_folder()

def delete_mail(imap, name: str, dt: date) -> bool:
    '''nameフォルダのdt以前のメールを削除する'''
    try:
        imap.select_folder(name)
        if DEBUG:
            print(f'{name}: delete folder before {dt.year:04d}/{dt.month:02d}/{dt.day:02d}')
        data = imap.search(['SEEN', 'BEFORE', dt])
        if len(data) < 1:
            if DEBUG:
                print(f'{dt.year:04d}/{dt.month:02d}/{dt.day:02d}以前のメールはありません')
            return
        if DEBUG:
            num = len(data)
            print(f'delete {num}')
        # 1000個ずつに分ける            
        s = 0
        while s < len(data):
            datas = data[s:s + IMAP_MAX_DATA]
            if DEBUG:
                print(f'start delete: {s}')
            try:
                imap.move(datas, TRASH_PATH)
            except imapclient.exceptions.CapabilityError:
                '''moveコマンドがサポートされていない'''
                imap.copy(datas, TRASH_PATH)
                imap.delete_messages(datas)
            s += IMAP_MAX_DATA
    except imapclient.exceptions.IMAPClientError as err:
        print(f'{name}: フォルダがありません')
        print(len(data))
        print(err)
        return False
    imap.close_folder()
    return True

def convert_folder_to_imap(name: str) -> str:
    '''フォルダ名をIMAPのフォルダ名に変更する'''
    name = unquote(name)    # %20を空白に置換させる
    fs = name.split('/')
    fs = [INBOX_NAME,] + fs
    return '.'.join(fs)

def file_delete(imap, args: list):
    '''ファイルで指定されたフォルダの指定日以前のファイルを消す
フォルダ名(/区切り) 何日前以前を消すか
例)
メーリングリスト/いろいろ 30
    '''
    if len(args) < 1:
        print('ファイル名を指定してください')
        return
    file = args[0]
    with open(file, 'r') as fp:
        for v in fp:
            v = v.strip()
            if len(v) < 1 or v[0] == '#':
                continue
            vs = v.split()
            if len(vs) < 2:
                continue
            name, days = vs
            name = convert_folder_to_imap(name)
            try:
                days = int(days)
            except ValueError:
                print(f'{name},{days}: 数値を指定してください')
                continue
            dt = date.today() - timedelta(days=days)
            if delete_mail(imap, name, dt) is False:
                break

def imap_delete(imap, args: list):
    '''指定されたフォルダの指定日以前を削除する'''
    def usage():
        print('delete foldername year month day')

    name = None
    dt = None
    try:
        name = args[0]
        year = int(args[1])
        month = int(args[2])
        day = int(args[3])
        dt = date(year, month, day)
    except IndexError:
        print('deleteコマンドの引数が足りません')
        usage()
        return
    except ValueError:
        print('deleteコマンドの日付指定が違います')
        usage()
        return
    if name is None:
        print('フォルダ名が指定されていない')
        usage()
        return
    name = convert_folder_to_imap(name)
    delete_mail(imap, name, dt)

def imap_list(imap, _: list):
    '''フォルダ名一覧を出力する'''
    fs = []

    folders = imap.list_folders()
    # 戻り値: (flags, delimiter, name)
    for _, sep, name in folders:
        sep = sep.decode('utf-8')
        names = name.split(sep)
        if names[0] == INBOX_NAME:
            names = names[1:]
        fs.append('/'.join(names))

    fs.sort(key=str.lower)
    for v in fs:
        print(v)

cmdlist = {
    'list': imap_list,
    'delete': imap_delete,
    'file': file_delete,
    'trash': trash_cleanup,
}

def parse_option():
    parser = argparse.ArgumentParser(description='imapの操作')
    parser.add_argument('cmd', choices=cmdlist.keys(), help='コマンド')
    parser.add_argument('args', nargs='*', help='コマンド引数')

    return parser.parse_args()

def main():
    args = parse_option()
    cmd = args.cmd
    if cmd not in cmdlist.keys():
        print(f'{cmd}はわかりません')
        return
    with imapclient.IMAPClient(IMAP_SERVER, ssl=False) as imap:
        try:
            imap.login(IMAP_USER, IMAP_PASSWORD)
            cmdlist[cmd](imap, args.args)
        except imapclient.exceptions.LoginError as err:
            print('ログイン失敗')
            print(err)
    return 0

if __name__ == '__main__':
    main()
