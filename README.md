
# FastAPI Template

## Features

- **[FastAPI](https://fastapi.tiangolo.com)**: High-performance web framework for building the Python backend API.
- **[Pydantic](https://docs.pydantic.dev)**: Used by FastAPI for data validation and settings management, providing clear, error-checked data handling.
- **[SQLAlchemy](https://www.sqlalchemy.org)**: Python ORM for database interactions, making it easier to work with PostgreSQL.
- **[PostgreSQL](https://www.postgresql.org)**: Reliable SQL database for structured data storage.
- **[pgcrypto](https://www.postgresql.org/docs/current/pgcrypto.html)**: PostgreSQL extension for column-specific encryption.
- **[Docker Compose](https://www.docker.com)**: Simplifies both development and production setups with container orchestration.
- **[bcrypt](https://github.com/pyca/bcrypt)**: For secure password hashing using the BCrypt SHA256 algorithm.
- **[JWT (JSON Web Token)](https://jwt.io)**: Provides secure, stateless user authentication.
- **[uv](https://docs.astral.sh/uv)**: Python package and environment management.
- **[setuptools](https://setuptools.pypa.io) and [Cython](https://cython.org/)**: Tools used to compile and optimize Python code, generating platform-specific binary files for better performance.

## Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/kishorninawe/fastapi-template.git
   cd fastapi-template
   ```

2. **Configure environment variables**:  
   Update configurations in the `.env` file to customize settings such as database connection, secret keys, and other environment-specific configurations.

### Using Docker Compose

3. **Build and run the application with Docker**:

   ```bash
   docker-compose up --build
   ```

### Running Locally (Without Docker)

3. **Set up environment and install dependencies**:

   - **Create virtual environment & install dependencies**:

     - Using `pip`:
       ```bash
       python -m venv .venv
       pip install -e .
       ```

     - Using `uv`:
       ```bash
       pip install uv
       uv sync
       ```

   - **Activate virtual environment**:

     - On **Linux/macOS**:
       ```bash
       source .venv/bin/activate
       ```

     - On **Windows**:
       ```bash
       .venv\Scripts\activate
       ```

   - **Check database accessibility and create `pgcrypto` if not exists**:

     - On **Linux/macOS**:
       ```bash
       PYTHONPATH=$(pwd):$PYTHONPATH python app/backend_pre_start.py
       ```

     - On **Windows**:
       ```bash
       set PYTHONPATH=%cd%;%PYTHONPATH% && python app\backend_pre_start.py
       ```

   - **Run migrations**:
     ```bash
     alembic upgrade head
     ```

   - **Add initial data to the database**:

     - On **Linux/macOS**:
       ```bash
       PYTHONPATH=$(pwd):$PYTHONPATH python app/initial_data.py
       ```

     - On **Windows**:
       ```bash
       set PYTHONPATH=%cd%;%PYTHONPATH% && python app\initial_data.py
       ```

   - **Start the FastAPI server**:
     ```bash
     uvicorn app.main:app --port 8000 --reload
     ```

4. **Access the application**:  
   Once the server is running, access the API documentation at:  
   `http://localhost:8000/docs`

## Tests

To run tests, use:

```bash
pytest
```

Tests are managed with **pytest**. You can modify or add new tests in the `./app/tests/` directory.

## Linting

To check code style and quality, use:

```bash
ruff check .
```

Code style is managed with **Ruff**. You can configure or extend linting rules in the `pyproject.toml` file.

## Type Checking

To check for type errors, use:

```bash
mypy .
```

Type checking is managed with **mypy**. You can configure or customize type-checking rules in the `pyproject.toml` file.

## Database Migrations

**Alembic** is used for managing database migrations. If you haven't set up Alembic yet, initialize it with:

- **Initialize Alembic**:

  ```bash
  alembic init app/alembic
  ```

Once initialized, to add or modify models, edit the `./app/models.py` file and then use the following commands:

- **Create a new migration** (after modifying models or tables):

  ```bash
  alembic revision --autogenerate -m "Description of migration"
  ```

- **Apply the latest migrations**:

  ```bash
  alembic upgrade head
  ```

- **Rollback the last migration**:

  ```bash
  alembic downgrade -1
  ```

Migration configurations can be customized in the `alembic.ini` file.

## License

The FastAPI Template is licensed under the terms of the MIT license.

## Acknowledgments

This project is based on the [Full Stack FastAPI Template](https://github.com/fastapi/full-stack-fastapi-template) and the [Uvicorn-Gunicorn Docker](https://github.com/tiangolo/uvicorn-gunicorn-docker) by [Sebastián Ramírez](https://github.com/tiangolo), both of which are licensed under the MIT License.

The original code and project structure were adapted to fit the needs of this project.
