FROM python:3.7-slim

# Install any needed packages specified in requirements.txt
RUN pip install Flask==0.11.1
RUN pip install gunicorn==19.9.0
RUN pip install redis==3.3.7

RUN mkdir /app
ADD corona.py /app

# Set the working directory to /app
WORKDIR /app

# Make port 28888 available to the world outside this container
EXPOSE 8443
CMD ["gunicorn", "-w", "1", "-t", "60", "-b", "0.0.0.0:8443", "corona:app"]
#CMD ["python", "ip2location.py"]
