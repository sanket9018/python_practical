# FastAPI Practical Task

This project is a FastAPI-based application with MySQL as the database. It provides user management features, including user creation, login, and CRUD operations, with role-based access control.

## Prerequisites

Before running the project, ensure you have the following installed:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Python 3.11](https://www.python.org/downloads/) (if running locally without Docker)

## Project Structure

    ├── app/
    │   ├── apis/
    │   ├── schema/
    │   ├── __init__.py
    │   ├── main.py
    │   └── ...
    ├── mysql/
    │   └── init.sql
    ├── docker-compose.yml
    ├── Dockerfile
    ├── requirements.txt
    └── README.md

## Setup and Run

### Using Docker (Recommended)

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/sanket9018/python_practical.git
   cd python_practical
   ```

2. **Build and Start the Docker Containers**:
   ```bash
   docker-compose up --build
   ```

   The required tables and database will be created automatically during the container initialization.

3. **Start the FastAPI Server**:
   The server will start at [http://127.0.0.1:8000](http://127.0.0.1:8000).

4. **Access the Swagger UI (API Documentation)**:
   Open your browser and navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
