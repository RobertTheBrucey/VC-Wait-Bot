FROM python:3.8
RUN apt update && apt install -y bash git
COPY src/requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt
COPY src /src/
CMD [ "/src/start.sh" ]