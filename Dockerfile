FROM python:3.13-slim

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation and unbuffered logging
ENV UV_COMPILE_BYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy project files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies into the container's environment
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application
COPY . .

# Run the application with uv to ensure venv is active
CMD ["uv", "run", "run.py"]
