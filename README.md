# ddsu666_power_meter_notify
配合 esp32c3_mqtt_ddsu666 项目使用的耗电情况定时通知脚本, 无法单独使用. 主项目地址: https://github.com/xinjiawei/esp32c3_mqtt_ddsu666

## 特征

+ 统计每日的峰谷电耗电情况, 通知耗电度数和电费金额.
+ 使用iyuu接口做微信通知.

## 使用
1. 在 8clock_e.py 中填写 iyuu token.
2. 在 schedule.cron 中更改 mqtt broker 的地址, 端口, 账号, 密码等.
3. build docker image

## 效果

![example](https://cf.mb6.top/lib/images/github/20241221/a35ad6acecbdd4e105cad1236fd5c3e9.jpg)
![example](https://cf.mb6.top/lib/images/github/20241221/g84e56fsdg5vdgre49dg48fd9489dd51.png)
