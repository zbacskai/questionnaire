FROM python:3.9.0-slim
COPY . /root
RUN pip install -r /root/requirements.txt
CMD cd /root && python /root/run_server.py
