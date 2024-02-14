FROM python:3.12
WORKDIR /main
COPY requirements.txt /main/
RUN pip install -r requirements.txt
COPY . /main
CMD python main.py