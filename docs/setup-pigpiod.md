# pigpiodのインストール・設定・自動起動設定

本ライブラリは`pigpio`デーモンが動作している必要があります。

## == **`pigpio`のインストールと起動**

以下の設定をすると、次回再起動時に、`pigpiod`が自動起動されるようになります。

```bash
# Raspberry Pi OSにはプリインストールされていることが多いです
sudo apt update
sudo apt install pigpio

# pigpioデーモンの起動と自動起動設定
sudo systemctl start pigpiod
sudo systemctl enable pigpiod
```


## == **トラブルシューティング**: `pigpiod`が自動起動されない

OSのバージョン(bookworm?)によっては、上記設定をしても、
`pigpiod`が再起動されないことがあります。

その場合には、以下の設定も追加で行ってください。

### 1. 一旦、pigpiodサービスを無効にする

``` bash
sudo systemctl disable pigpiod.socket
sudo systemctl stop pigpiod.socket
sudo systemctl disable pigpiod.service
sudo systemctl stop pigpiod.service
```


### 2. 以下のコマンドで、追加設定を行う

``` bash
sudo systemctl edit pigpiod.service
```

エディタが開くので、以下の内容を記入して保存してください。

(ネットワークが起動してから、pigpiodを起動する設定です。)

``` ini
[Unit]
After=network-online.target
Wants=network-online.target
```


### 3. pigpiodサービスを有効に戻す

``` bash
sudo systemctl daemon-reload
sudo systemctl enable pigpiod.service
sudo systemctl start pigpiod.service
```

これで、次回再起動時から、`pigpiod`が自動起動されるようになります！
