FROM ubuntu:22.04
WORKDIR /app
USER root
COPY . .
ENV TZ=Asia/Shanghai
ENV DEBIAN_FRONTEND=noninteractive
RUN cp /etc/apt/sources.list /etc/apt/sources.list.bak && sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list && sed -i 's/deb.debian.org/mirrors.163.com/g' /etc/apt/sources.list && apt-get update
RUN apt-get -y install --assume-yes dialog apt-utils nano cron curl htop iputils-ping
RUN echo "${TZ}" > /etc/timezone && ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime && apt-get -y install --assume-yes tzdata
# base config end
RUN apt-get -y install --assume-yes python3 pip && pip install -r requirements.txt
RUN chmod u+x /app/* && crontab /app/cron/schedule.cron
ENTRYPOINT ["./stup.sh"]

# docker build --no-cache -t harbor.mb6.top:32570/xinjiawei1/power_notify:1.1 .