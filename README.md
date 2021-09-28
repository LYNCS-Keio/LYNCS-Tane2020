# LYNCS-Tane2020
[![Build Status](https://travis-ci.org/LYNCS-Keio/LYNCS-Tane2020.svg?branch=master)](https://travis-ci.org/LYNCS-Keio/LYNCS-Tane2020)

2020種子島宇宙ロケットコンテストヘ向けたローバーのプログラム

## Building the Environment

`git clone`した後ターミナルで以下を実行すると必要な環境を構築します。Debian系OSでのみ利用可能です。

```
$ bash bin/install_dependencies.sh
$ password : パスワードを入力
```

## Requirement

- pip3
- pyenv
- pipenv

## やること
- [x] pigpioを用いたi2c library
- [x] DPS310動作確認
- [x] DPS310コーディング
- [x] ICM20948動作確認
- [x] ICM20948コーディング
- [x] INA260動作確認
- [ ] INA260コーディング
- [ ] VL53L1X動作確認
- [ ] VL53L1Xコーディング
- [x] TWE-LITE動作確認
- [ ] TWE-LITEコーディング
- [ ] GNSSのpigpio化
- [ ] 落下判定
- [ ] パラ分離
- [ ] 直進＆指定角回転
- [ ] GNSS誘導
- [ ] 画像誘導
- [ ] 自立ゴール

