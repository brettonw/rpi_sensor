FROM ubuntu:latest

# Install necessary packages
RUN apt-get update && \
    apt-get install -y python3-pip && \
    pip3 install flask

# Expose the port that the Flask server will run on
EXPOSE 5000

# Set the default command to run the Flask server
CMD ["python3", "/usvc/usvc.py"]
