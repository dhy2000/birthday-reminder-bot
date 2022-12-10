# 生日提醒 bot

## 使用说明

### 本地运行

安装依赖：

```shell
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

生日数据以 Excel 表格存储，命名为 `data.xlsx` 放置于本项目目录，执行：

```shell
python3 -u bot.py
```

### 部署到服务器

构建 docker 镜像:

    docker build -t "birthday-bot" .

运行 docker 镜像:

    docker run -d --restart=unless-stopped --name=birthday-bot \
        -v /etc/timezone:/etc/timezone:ro -v /etc/localtime:/etc/localtime:ro \
        -v /path/to/data:/app/data.xlsx \
        -v /path/to/key:/app/key \
        birthday-bot:latest

数据表格用 `-v` 选项挂载到 `/app/data.xlsx`。

消息通知 API 的口令按如下格式保存为 key 文件，并挂载到 `/app/key`。

```shell
export PUSH_MESSAGE_KEY="YOUR_PUSH_MESSAGE_KEY"
```

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

采用 `crontab` 进行定时任务管理，每日零点整运行一次，如当天或往后第 7 天有人过生日，则推送提醒消息。