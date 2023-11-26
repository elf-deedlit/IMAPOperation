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

def trash_cleanup(imap: imapclient.imapclient.IMAPClient, args: list, force: bool) -> None:
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

def imap_copy_delete(imap: imapclient.imapclient.IMAPClient, datas: list) -> bool:
    '''IMAPのmoveコマンドの代わりにcopy→deleteにする'''
    imap.copy(datas, TRASH_PATH)
    imap.delete_messages(datas)
    return True

def imap_move(imap: imapclient.imapclient.IMAPClient, datas: list) -> bool:
    '''IMAPのmoveコマンドを試す'''
    try:
        imap.move(datas, TRASH_PATH)
        return True
    except imapclient.exceptions.CapabilityError:
        imap_copy_delete(imap, datas)
        return False

def delete_mail(imap: imapclient.imapclient.IMAPClient, name: str, dt: date, force: bool) -> bool:
    '''nameフォルダのdt以前のメールを削除する'''
    try:
        imap.select_folder(name)
        if DEBUG:
            print(f'{name}: delete folder before {dt.year:04d}/{dt.month:02d}/{dt.day:02d}')
        if force:
            data = imap.search(['SEEN', 'BEFORE', dt])
        else:
            data = imap.search(['UNFLAGGED', 'SEEN', 'BEFORE', dt])
        if len(data) < 1:
            if DEBUG:
                print(f'{dt.year:04d}/{dt.month:02d}/{dt.day:02d}以前のメールはありません')
            return
        if DEBUG:
            num = len(data)
            print(f'delete {num}')
        # 1000個ずつに分ける            
        s = 0
        move_func = imap_move
        while s < len(data):
            datas = data[s:s + IMAP_MAX_DATA]
            if DEBUG:
                print(f'start delete: {s}')
            if move_func(imap, datas) is False:
                # 本当はimap.capabilitiesの結果で判断するのが正しい
                move_func = imap_copy_delete
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

def file_delete(imap: imapclient.imapclient.IMAPClient, args: list, force: bool) -> None:
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
            if delete_mail(imap, name, dt, force) is False:
                break

def imap_delete(imap: imapclient.imapclient.IMAPClient, args: list, force: bool) -> None:
    '''指定されたフォルダの指定日以前を削除する'''
    def usage():
        print('delete foldername (year month day) or (timedelta)')

    name = None
    dt = None
    try:
        name = args[0]
        if len(args) == 4:
            year = int(args[1])
            month = int(args[2])
            day = int(args[3])
            dt = date(year, month, day)
        elif len(args) == 2:
            day = int(args[1])
            dt = date.today() - timedelta(days=day)
        else:
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
    delete_mail(imap, name, dt, force)

def imap_list(imap: imapclient.imapclient.IMAPClient, args: list, f: bool) -> None:
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

def imap_debug(imap: imapclient.imapclient.IMAPClient, args: list, force: bool) -> None:
    '''IMAPコマンドテスト用'''
    name = convert_folder_to_imap(args[0])
    day = int(args[1])
    imap.select_folder(name)
    dt = date.today() - timedelta(days=day)
    if force:
        data = imap.search(['SEEN', 'BEFORE', dt])
    else:
        data = imap.search(['UNFLAGGED', 'SEEN', 'BEFORE', dt])
    data = data[:2]
    for msgid, fetchdata in imap.fetch(data, ['FLAGS', 'BODY.PEEK[HEADER.FIELDS (Date Subject)]']).items():
        v = fetchdata[b'BODY[HEADER.FIELDS ("DATE" "SUBJECT")]']
        flag = fetchdata[b'FLAGS']
        print(f'{msgid}[{flag}]: {v}')

cmdlist = {
    'list': imap_list,
    'delete': imap_delete,
    'file': file_delete,
    'trash': trash_cleanup,
    'debug': imap_debug,
}

def parse_option():
    parser = argparse.ArgumentParser(description='imapの操作')
    parser.add_argument('--force', action='store_true', help='フラグがついているものも操作する')
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
            cmdlist[cmd](imap, args.args, args.force)
        except imapclient.exceptions.LoginError as err:
            print('ログイン失敗')
            print(err)
    return 0

if __name__ == '__main__':
    main()
