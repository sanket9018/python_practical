
# wait until MySQL is ready
until mysqladmin ping -h"$MYSQL_HOST" --user="$MYSQL_USER" --password="$MYSQL_PASSWORD" --silent; do
  echo "Waiting for MySQL to be ready..."
  sleep 2
done

echo "MySQL is up. Starting FastAPI"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
