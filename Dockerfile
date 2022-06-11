FROM python:3.8-slim

RUN pip install --default-timeout=10000 -i https://pypi.tuna.tsinghua.edu.cn/simple pandas openpyxl requests
RUN apt-get install apt-transport-https ca-certificates
RUN echo "" > /etc/apt/sources.list; \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye main contrib non-free" >> /etc/apt/sources.list; \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye-updates main contrib non-free" >> /etc/apt/sources.list; \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye-backports main contrib non-free" >> /etc/apt/sources.list; \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security bullseye-security main contrib non-free" >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y cron
RUN echo "0 0 * * 1 . /etc/profile; . /key; cd /; python -u bot.py" | crontab

COPY bot.py /
WORKDIR /
CMD echo "export PUSH_MESSAGE_KEY='$PUSH_MESSAGE_KEY'" > /key; cron -f