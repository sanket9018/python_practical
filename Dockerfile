FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install MySQL client
RUN apt-get update && apt-get install -y default-mysql-client

COPY . .

RUN chmod +x wait-for-mysql.sh

CMD ["./wait-for-mysql.sh"]
