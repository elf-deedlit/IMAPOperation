# IMAPOperation
IMAPをいろいろと操作するツール

## 使い方
```bash
$ imap_operate.py command [args [args ...]]
```

## 事前準備
* imapclientのインストール
* default.pyをconfig.pyにコピーする
* config.pyのIMAP_USERとIMAP_PASSWORDを書き換える

## コマンド一覧
* list  
フォルダ一覧を出力

* delete フォルダ名 年 月 日  
フォルダ名にある指定日以前のファイルをゴミ箱に移動する

* file ファイル名  
指定されたファイルに指定されているフォルダ一覧にある指定日数以前のファイルをゴミ箱に移動する
    * 記載例  
    メーリングリスト/いろいろ 30  
    上記フォルダのメールを30日分だけ残して消す

* trash 指定日数
ゴミ箱を指定日数分残して消す

## 仕様
* SEENフラグ(既読のメール)を削除する。未読のメールは操作しない(はず)。
* フォルダ名の指定に空白を指定したいときは%20を使う。

## TODO
* deleteコマンドの指定日数での指定
* gmail対応



