# syntax=docker/dockerfile:1 # not needed on some systems

# what to install
FROM python:3 


# install folder of image
WORKDIR /usr/src/app



COPY requirements.txt ./

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt


# copy all
COPY . . 

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"] 