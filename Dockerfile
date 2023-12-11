FROM python:3.11

ARG GRADIO_SERVER_PORT=7860
ARG GRADIO_SERVER_NAME=0.0.0.0



ENV GRADIO_SERVER_PORT=${GRADIO_SERVER_PORT}
ENV GRADIO_SERVER_NAME=${GRADIO_SERVER_NAME}



WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

#RUN adduser --system --no-create-home app
#USER app

CMD ["python", "/app/app.py"]
