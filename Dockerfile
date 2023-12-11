FROM python:3.11



# set environment variables for Gradio
ENV GRADIO_SERVER_PORT=7860
ENV GRADIO_SERVER_NAME=0.0.0.0


# set working directory
WORKDIR /app

# install dependencies
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# copy source code to workingdir 
COPY ./app.py /app//app.py
COPY ./mtg /app/mtg

#RUN adduser --system --no-create-home app
#USER app

# start Gradio
CMD ["python", "/app/app.py"]