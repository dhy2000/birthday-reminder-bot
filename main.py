import os, sys
from datetime import date, timedelta
import pandas as pd
import requests
import argparse
from lunardate import LunarDate

today: date
date_range: list        # [date object]
month_day_range: list   # [(month, day)]
people_by_date: dict    # {(month, day): [(name, tag, calendar, comment)]}

# 解析命令行参数
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Birthday remainder.")
    parser.add_argument('-k',
                        help='path to key',
                        metavar='key', dest='key')
    parser.add_argument('-f',
                        help='path to data file',
                        metavar='birthday.xlsx', required=True, dest='file')
    return parser.parse_args()

# 生成日期范围
def generate_date_range():
    global today, date_range, month_day_range, people_by_date
    range_length = 7
    one_day = timedelta(days=1)
    date_range = [today + i * one_day for i in range(range_length)]
    month_day_range = [(dt.month, dt.day) for dt in date_range]
    people_by_date = dict()
    for month, day in month_day_range:
        people_by_date[(month, day)] = list()

# 筛选阳历生日
def process_solar_birthday(people: pd.Series):
    global month_day_range
    month, day = people['month'], people['day']
    if people['active'] and (month, day) in month_day_range:
        people_by_date[(month, day)].append((people['name'], people['tag'], '阳历'))

# 筛选阴历生日
def process_lunar_birthday(people: pd.Series):
    global date_range, month_day_range
    lunar_month, lunar_day = people['month'], people['day']
    if not people['active']:
        return
    # 阳历的今年包含阴历的今年和上一年（春节前）
    lunar_last_year = LunarDate(year=today.year - 1, month=lunar_month, day=lunar_day).toSolarDate()
    lunar_current_year = LunarDate(year=today.year, month=lunar_month, day=lunar_day).toSolarDate()
    print(people['name'], lunar_last_year, lunar_current_year)
    if lunar_last_year in date_range:       # 阴历生日在春节前
        solar_date = lunar_last_year
    elif lunar_current_year in date_range:  # 阴历生日在春节后
        solar_date = lunar_current_year
    else:
        return
    # 换算为阳历加入名单
    people_by_date[(solar_date.month, solar_date.day)].append((people['name'], people['tag'], '阴历'))

# 判断今日是否推送
def should_push_today() -> bool:
    global people_by_date
    # 条件1: 今日有人过生日
    has_today = len(people_by_date[(today.month, today.day)]) > 0
    # 条件2: 筛选范围的最后一日有人即将过生日
    has_coming = len(people_by_date[month_day_range[-1]]) > 0
    return has_today or has_coming

# 按指定格式生成消息内容
def render_message_content() -> str:
    # Markdown Table
    table_head = '| 日期 | 姓名 | 标签 | 类型 |'
    table_line = '| :---: | :---: | :---: | :---: |'
    table_items = []
    for month, day in month_day_range:
        assert (month, day) in people_by_date.keys()
        for people in people_by_date[(month, day)]:
            table_items.append('| {month}月{day}日 | {name} | {tag} | {calendar} |'.format(
                month=month, day=day, name=people[0], tag=people[1], calendar=people[2]
            ))
    return "\n".join([table_head, table_line] + table_items)

# 调用 API 推送提醒
def push_message(key: str, content: str) -> bool:
    title = '生日提醒 ' + today.strftime("%Y年%m月%d日")
    url = "https://xizhi.qqoq.net/{key}.send".format(key=key)
    req = requests.post(url, params={
        'title': title,
        'content': content,
    })
    print(req.text)
    if req.status_code == 200:
        print("push message succeed!")
        return True
    else:
        print("push message failed, code={0}".format(req.status_code))
        return False

if __name__ == '__main__':
    args = parse_args()

    today = date.today()
    print("Today is", today.strftime("%Y.%m.%d"))

    generate_date_range()
    
    # 阳历
    df_solar = pd.read_excel(args.file, sheet_name='Solar')
    df_solar.apply(process_solar_birthday, axis=1)

    # 阴历
    df_lunar = pd.read_excel(args.file, sheet_name='Lunar')
    df_lunar.apply(process_lunar_birthday, axis=1)

    # 生成消息内容并预览
    content = render_message_content()
    print(content)  # Preview message

    # 检查今日是否需要推送
    if not should_push_today():
        print("No need to push today.")
        sys.exit(0)

    # 读取 API Key 并推送
    if args.key is None:
        print("Warning: no api key, message is not pushed.")
        sys.exit(0)
    
    keyfile = args.key
    with open(keyfile, "r") as fp:
        keytexts = fp.readlines()
    for k in keytexts:
        key = k.strip()
        if len(key) == 0:
            continue
        push_message(k.strip(), content)



