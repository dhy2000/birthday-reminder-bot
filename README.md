# Birthday Remainder Bot

一个简易的生日提醒工具，从 Excel 表格读取生日列表，整理当天及近期过生日的朋友名单并给自己的微信推送提醒消息。

现在已支持阳历和阴历生日。

## 数据格式

以 Excel 表格（XLSX 格式）存储生日列表，表格文件包含 "Solar" 和 "Lunar" 两个 Sheet，分别存储阳历和阴历的生日列表。两个 Sheet 内部格式相同，第一行为表头而后一行为一条记录。

生日列表示例：

| name | month | day | tag | active | comment |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 张三 | 2 | 1 | 大学X级Y系 | 1 | |
| 李四 | 3 | 2 | 高中X班 | 1 | |
| 张三 | 9 | 1 | 大学X级Y系 | 1 | |
| 王五 | 10 | 9 | 大学学生会 | 0 | |

表头字段意义：

| 字段名 | 数据类型 | 数据范围 | 含义 |
| :---: | :---: | :---: | :---: |
| name | 文本 | 非空 | 姓名 |
| month | 整数 | 1\-12 | 月 |
| day | 整数 | 1\-本月天数 | 日 |
| tag | 文本 | 非空 | 标签 |
| active | 布尔 | 0 或 1 | 是否有效 |
| comment | 文本 | 允许空值 | 备注 |

其中:

- `tag` 为身份标签，可以为学校、年级、院系等信息或与自己的关系(同学/老师/...)，可借此字段区分重名
- `active` 为有效标志，一般取值 1，如有被删好友、日期记录错误等异常情况则置为 0，置 0 后此人被过滤掉
- `comment` 为补充的备注说明，可不填

阴历和阳历的格式相同，月份和日期均使用阿拉伯数字表示，例如 "正月初一" 的 `month` 和 `day` 字段均填入数字 `1` ，"腊月廿五" 的 `month` 和 `day` 分别填入 `12` 和 `25` 。

目前本工具仅支持从本地读取 Excel 表格文件。如果用在线文档平台（腾讯文档、金山文档等）存储数据，需下载到本地供本工具读取。

## 消息推送

使用 [息知](https://xz.qqoq.net) 服务向自己的微信推送提醒消息，该平台免费且使用方法简单。微信关注息知公众号后，使用自己的口令调用其 API 即可向自己推送提醒。

将口令存储在文本文件中供本工具读取，如有多个口令则每行一个口令，无多余空行。

口令文件格式示例：

```
XXXXXXXXXXXXXXX
YYYYYYYYYYYYYYY
```

2023 年 3 月底息知平台更新后，推送消息正文支持 Markdown 格式，近期生日名单以 Markdown 表格呈现。

## 定时提醒

采用 `crontab` 管理定时任务，每日零点整运行一次。每次运行程序将整理出相对今日往后 7 天范围内过生日的名单并进行推送。

为了减少打扰，本工具设定了判断条件，仅当推送当天有人过生日，以及当天往后的第 7 日有人过生日时才发出推送，如不满足此要求则当日不会收到推送。

定时任务仅在 docker 容器中启动，如直接用 Python 执行则仅读取并推送一次，不能定时自动运行。

## 运行方法

### 本地临时运行

建立并激活虚拟环境（可选）：

```shell
python3 -m virtualenv .venv
source .venv/bin/activate
```

安装依赖：

```shell
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

准备生日列表文件和消息推送口令文件，例如生日列表为 `birthday.xlsx`，推送口令文件为 `key` 则执行以下命令：

```shell
python3 -u main.py -f birthday.xlsx -k key
```

用 `-f` 选项指定数据文件路径，用 `-k` 选项指定口令文件路径。如口令文件不存在或 `-k` 选项缺省，则执行本程序仅在命令行中预览近期过生日的名单，而不会发送提醒消息。

### 使用 Docker 容器

构建 docker 镜像:

```shell
docker build -t "birthday-remainder:latest" .
```

要运行 docker 容器，将 `docker-run.example.sh` 复制一份为 `docker-run.sh` 并将表格文件和口令文件的 **绝对路径** 填入其中，而后执行 `bash docker-run.sh` 启动容器，容器名称为 `birthday-remainder` 。
