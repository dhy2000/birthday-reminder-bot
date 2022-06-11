import os
import sys
import datetime
import pandas as pd
import requests
from functools import reduce

DATASHEET = 'data.xlsx' # 数据表格
DAYS_COUNT = 7          # 提醒范围: 从今天起的 7 天
DATE_FORMAT = "{month}月{day}日"

PUSH_MESSAGE_TITLE = "生日提醒 {today}"
PUSH_MESSAGE_URL = "https://xizhi.qqoq.net/{key}.send"

# 计算日期范围
day_range = []
today, delta = datetime.date.today(), datetime.timedelta(days=1)
for i in range(DAYS_COUNT):
    day = (today + i * delta)
    day_range.append(DATE_FORMAT.format(month=day.month, day=day.day))

# 加载与筛选数据
print("Welcome to birthday reminder bot!")
print("Today is {0}.".format(today))
df = pd.read_excel(DATASHEET)
df['birthday'] = df.apply(lambda p : DATE_FORMAT.format(month=p['month'], day=p['day']), axis=1)
part = df[(df['birthday'].isin(day_range)) & ~(df['active'] == 0)].sort_values(by=['month', 'day'], ascending=[True, True])
print("Find {0} friend(s) in total, {1} friend(s)'s birthday is comming soon:".format(df.shape[0], part.shape[0]))
print(part['name'].tolist())

# 根据日期分类
dict_by_day = dict()
def insert_to_dict(loc):
    if not loc['birthday'] in dict_by_day.keys():
        dict_by_day[loc['birthday']] = []
    dict_by_day[loc['birthday']].append(loc['name'] + (' ({0})'.format(loc['tag']) if loc['tag'] else ''))
part.apply(insert_to_dict, axis=1)

# 生成提醒消息
push_message_title = PUSH_MESSAGE_TITLE.format(today=today)
push_message_content = reduce(lambda x, y : x + ';' + y, map(lambda k : '【{date}】: '.format(date=k) + ", ".join(dict_by_day[k]), dict_by_day))

print(push_message_content)

# 推送消息
push_message_key = os.getenv("PUSH_MESSAGE_KEY")
if push_message_key is None:
    print("Failed to get key, reminder message is not pushed.")
    sys.exit(0)
push_message_url = PUSH_MESSAGE_URL.format(key=push_message_key)

req = requests.post(push_message_url, params={
    "title": push_message_title,
    "content": push_message_content
})
if req.status_code == 200:
    print("push succeed!")
    print(req.text)
else:
    print("push failure: status code={0}".format(req.status_code))
    print(req.text)
