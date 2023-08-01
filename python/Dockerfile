# 使用Python官方的镜像作为基础镜像
FROM python:3.10-slim

# 将工作目录设置为/app
WORKDIR /app


# 安装requests库
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates

RUN pip install requests pyyaml

# 将当前目录下的所有文件复制到容器的/app目录下
COPY dukou/checkin.py /app/checkin.py
# 运行Python程序
CMD ["python", "app/checkin.py"]
