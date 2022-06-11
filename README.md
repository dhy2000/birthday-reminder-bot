# 生日提醒 bot

## 使用说明

构建 docker 镜像:

    docker build -t "birthday-bot" .

运行 docker 镜像:

    docker run -d --restart=unless-stopped --name=birthday-bot \
        -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro \
        -v /path/to/birthday/data:/data.xlsx \
        -e PUSH_MESSAGE_KEY="YOUR_PUSH_MESSAGE_KEY" \
        birthday-bot:latest

其中环境变量 `PUSH_MESSAGE_KEY` 需设置为自己的口令以调用 API。生日数据以 `.xlsx` 格式的 Excel 表格存储，并需将其映射到容器根目录下的 `/data.xlsx`。

## 数据存储

bot 从当前目录的 `data.xlsx` 中读取生日数据。

Excel 格式示例:

| name | month | day | tag | active | comment |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 张三 | 1 | 1 | 大学同学 | 1 | |
| 李四 | 2 | 28 | 中学同学 | 0 | 已被删除好友 |

其中表头各字段含义:

| 字段名 | 数据类型 | 数据范围 | 含义 |
| :---: | :---: | :---: | :---: |
| name | 文本 | 非空 | 姓名 |
| month | 整数 | 1\-12 | 月 |
| day | 整数 | 1\-本月天数 | 日 |
| tag | 文本 | 允许空值 | 标签 |
| active | 布尔 | 0 或 1 | 有效标志 |
| comment | 文本 | 允许空值 | 备注 |

其中:

- `tag` 字段可以包含这个人的身份标签(例如学校、年级)或与自己的关系(例如中学/大学同学、老师等)
- `active` 字段为该条生日信息的有效标志，通常取值 1，如有被删好友等情况则条目失效，标记为 0
- `comment` 为对该条生日信息的备注，该字段留做备用，可以为空值。

**TODO**: 通过 API 从腾讯/金山等在线文档服务拉取数据（目前 bot 仅支持从本地读取数据，数据表仍需定期人工维护）

## 消息推送

使用 [息知](https://xz.qqoq.net) 服务进行微信推送。调用该服务提供的消息 API 并关注公众号即可收到微信提醒。

调用 API 需传入的用于身份识别的口令需置于环境变量 `PUSH_MESSAGE_KEY` 中。

## 定时提醒

采用 `crontab` 进行定时任务管理，每周一零点提醒一次。