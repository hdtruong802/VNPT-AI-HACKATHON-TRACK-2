# BASE IMAGE
# ------------------------------------------------------------
# Using python:3.13-slim as the solution is API-based and does not require CUDA
FROM python:3.13-slim

# ------------------------------------------------------------
# SYSTEM DEPENDENCIES
# ------------------------------------------------------------
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# PROJECT SETUP
# ------------------------------------------------------------
WORKDIR /code

# Copy source code
COPY . /code

# ------------------------------------------------------------
# INSTALL LIBRARIES
# ------------------------------------------------------------
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------
# QDRANT SETUP (EMBEDDED)
# ------------------------------------------------------------
# Set Qdrant to use local storage
ENV QDRANT_URL=/code/qdrant_storage
# Initialize the database during build
RUN python setup_qdrant.py

# ------------------------------------------------------------
# EXECUTION
# ------------------------------------------------------------
CMD ["bash", "inference.sh"]
