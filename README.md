# 功能簡介

## 主要功能

- 實作短網址服務，將任意網址轉成固定長度(不超過 5)的短網址
- 可支援超過 1000 萬個網址
- 有短網址預覽功能: 顯示原本網址但不轉跳

## 補充

- 假設網址數量上限為 1 億
- 短網址預覽功能僅支援標準 [open graph protocol](https://ogp.me/) 的規範

## 其他

- 測試覆蓋率: 98%
- 限定創造短網址 API 的 rate limit: 5 / min

# 環境設定

## 安裝所需的套件
- require python 3.7+

- virtaulenv (記得保持啟動狀態)

    `virtualenv -p $(which python3) venv`

    `. venv/bin/activate`

- python related

    `pip install -r requirements.txt`

- redis (cache)

    ```
    wget http://download.redis.io/redis-stable.tar.gz
    tar xvzf redis-stable.tar.gz
    cd redis-stable
    make

    # test
    sudo yum install tcl
    make test

    # run redis server
    cd src
    ./redis-server
    ```


## 同步資料庫 schema

 -  `python manage.py migrate`


## static files

-  `python manage.py collectstatic`


## run server

- `python manage.py runserver [ip:port]`


## unit test
- run test

    `python manage.py test`

- 單元測試覆蓋率

    `coverage run --source='.' manage.py test`

    `coverage report`
