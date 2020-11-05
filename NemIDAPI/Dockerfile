FROM python:3.7-alpine
ADD . /app
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5555
COPY . .
CMD ["python", "run.py"]


