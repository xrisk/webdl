FROM python:3-alpine
RUN apk add ffmpeg 
# RUN apk add coreutils  
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app
ENV PORT 80
EXPOSE 80

CMD ["python", "server.py"]