FROM python:3.11

# set environment variables for Gradio
ARG GRADIO_SERVER_PORT=7860
ARG GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860
ENV GRADIO_SERVER_NAME=0.0.0.0

# set working directory
WORKDIR /app

# install dependencies
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# copy source code to workingdir 
COPY ./mtg /app/mtg
COPY ./app.py /app/app.py

#create non-root user and change /app permissions
RUN chmod -R 555 /app
RUN adduser --system --no-create-home app
USER app

# start Gradio
CMD ["python", "/app/app.py"]