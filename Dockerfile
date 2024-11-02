# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
FROM python:3.7

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1
ADD . /tour_management_project/
VOLUME /tour_management_project_volume
WORKDIR /tour_management_project

RUN pip install -r requirements.txt

# Expose ports
EXPOSE 9300

# define the default command to run when starting the container
CMD ["gunicorn", "--chdir", "tour_management_project", "--bind", ":9300", "tour_management_project.wsgi","--timeout","1200"]