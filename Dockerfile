FROM python:3-alpine

RUN apk add ffmpeg    
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
ENV PORT 80
EXPOSE 80

CMD ["python", "server.py"]