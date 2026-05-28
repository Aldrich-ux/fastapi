# Docker see each line as a layer, 
# so we can start at any line and build the image from there.

FROM python:3.10

WORKDIR /usr/src/app

# copy requirements.txt to the container working directory
COPY requirements.txt ./ 

# no cache for downloaded packages in docker container
RUN pip install --no-cache-dir -r requirements.txt

# Copy the whole application code to the container working directory
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]