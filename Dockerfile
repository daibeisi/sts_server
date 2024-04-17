FROM python:3.10.1

ENV TZ "Asia/Shanghai"

WORKDIR /code

COPY . /code/

RUN pip install --no-cache-dir --upgrade -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

EXPOSE 5000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
