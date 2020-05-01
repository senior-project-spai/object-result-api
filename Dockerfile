FROM tiangolo/uvicorn-gunicorn:python3.8-alpine3.10

RUN apk --no-cache add build-base \
                       jpeg-dev \
                       zlib-dev \
                       freetype-dev \
                       lcms2-dev \
                       openjpeg-dev \
                       tiff-dev \
                       tk-dev \
                       tcl-dev \
                       harfbuzz-dev \
                       fribidi-dev

COPY ./app /app

RUN pip install -r /app/requirements.txt