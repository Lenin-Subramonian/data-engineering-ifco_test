# Base image - use Databricks minimal runtime as the base image
FROM databricksruntime/minimal:15.4-LTS

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies, upgrade pip, and clean up in a single step (Python, Supervisor, Java)
RUN apt-get update && apt-get install -y \
    python3-pip \
    supervisor \
    openjdk-11-jdk && \
    pip install --upgrade pip && \
    mkdir -p /var/log/supervisor && \
    mkdir -p /var/run && \
    chmod 777 /var/log/supervisor && \
    rm -rf /var/lib/apt/lists/*

# Add cleanup cron job - creates a cron job that runs every 15 minutes & deletes files in /tmp older than 1 day
RUN echo "*/15 * * * * find /tmp -type f -mtime +1 -delete" >> /etc/crontab

# Set environment variables for Java (JAVA_HOME for Java 11)
ENV JAVA_HOME="/usr/lib/jvm/java-1.11.0-openjdk-amd64"
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Resource management
ENV MAX_WORKERS=4
ENV MEMORY_LIMIT="4g"
ENV DB_POOL_SIZE=10
ENV DB_POOL_TIMEOUT=30
ENV STREAMLIT_CACHE_TTL=3600
ENV JUPYTER_CACHE_DIR="/tmp/jupyter_cache"

# Create Jupyter cache directory
RUN mkdir -p ${JUPYTER_CACHE_DIR}

# Copy the requirements file first (for better Docker caching)
# Install dependencies & requirements
COPY Docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files,data,Streamlit app files and notebooks into the container
COPY src/ /app/src/
COPY streamlit_app/ /streamlit_app/
COPY data/ /app/data/
COPY notebooks/ /app/notebooks

# Set Python path to include src folder
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

# Define a mountable volume for persistent data (optional)
# This can be removed if wants to mount the volume manually
VOLUME ["/app/data", "/app/logs"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/ || exit 1

# Copy the supervisord configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose both Jupyter Notebook and Streamlit ports
EXPOSE 8888 8501

# Start both Jupyter Notebook and Streamlit using supervisord
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
