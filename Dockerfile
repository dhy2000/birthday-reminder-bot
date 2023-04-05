FROM python:3.8-slim

RUN apt-get install apt-transport-https ca-certificates
RUN echo "" > /etc/apt/sources.list; \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye main contrib non-free" >> /etc/apt/sources.list; \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye-updates main contrib non-free" >> /etc/apt/sources.list; \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bullseye-backports main contrib non-free" >> /etc/apt/sources.list; \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security bullseye-security main contrib non-free" >> /etc/apt/sources.list
RUN apt-get update && apt-get install -y cron

WORKDIR /app
COPY requirements.txt .
RUN pip install --default-timeout=10000 -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

RUN echo "0 0 * * 0-6 . /etc/profile; cd /app; python -u main.py -f data.xlsx -k key" | crontab
COPY main.py .
ENTRYPOINT ["cron", "-f"]
# CMD cron -f
