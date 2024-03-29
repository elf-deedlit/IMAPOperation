# IMAPOperation
IMAPをいろいろと操作するツール

## 使い方
```bash
$ imap_operate.py [--force] command [args [args ...]]
```

## 事前準備
* imapclientのインストール
* default.iniをconfig.iniにコピーする
* config.iniにサーバセクションを作り、以下の設定を行う
    * server  
    サーバIPもしくはホスト名
    * user  
    サーバにアクセスするときのユーザ名
    * password  
    サーバにアクセスするときのパスワード
    * ssl  
    サーバにアクセスするときSSLを使うかどうか
    * trash  
    ゴミ箱のフォルダ名

## コマンド一覧
* list  
フォルダ一覧を出力

* delete フォルダ名 年 月 日 または delete フォルダ名 相対日時  
フォルダ名にある指定日以前のファイルをゴミ箱に移動する

* file ファイル名  
指定されたファイルに指定されているフォルダ一覧にある指定日数以前のファイルをゴミ箱に移動する
    * 記載例  
    メーリングリスト/いろいろ 30  
    上記フォルダのメールを30日分だけ残して消す

* trash 指定日数  
ゴミ箱を指定日数分残して消す

## オプション
* --force  
deleteやfile指定時、FLAGを見ないよう[^1]にする
* --server  
設定ファイルのセクションを指定する

[^1]: 指定がない場合FLAGがついているメールを削除しない

## 仕様
* SEENフラグ(既読のメール)を削除する。未読のメールは操作しない(はず)
* フォルダ名のパスは/で区切る
* フォルダ名の指定に空白を指定したいときは%20を使う

## 変更点
* 1.0.3
    * 設定ファイルをiniファイルに変更
    * サーバごとに設定ファイルに記載出来るようにした
* 1.0.2
    * MOVE処理を少しだけ効率が良いように変更
* 1.0.1
    * メールのFLAGを見るようにした
    * 上記追加に伴い、メールのFLAGを無視するオプションを追加
    * deleteコマンドの相対日指定を追加
    * IMAPのコマンドテスト関数を追加
    * 関数のアノテーションを追加
* 1.0
    * ひとまず作成

## TODO
 - [x] deleteコマンドの指定日数での指定
 - [ ] gmail対応
