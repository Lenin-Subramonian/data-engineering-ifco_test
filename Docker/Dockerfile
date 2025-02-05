# Use Databricks minimal runtime as the base image
FROM databricksruntime/minimal:15.4-LTS

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies, upgrade pip, and clean up in a single step (Python, Supervisor, Java)
RUN apt-get update && apt-get install -y \
    python3-pip \
    supervisor \
    openjdk-11-jdk && \
    pip install --upgrade pip && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME for Java 11
ENV JAVA_HOME="/usr/lib/jvm/java-1.11.0-openjdk-amd64"
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Copy only the requirements file first (for better Docker caching)
COPY Docker/requirements.txt .

# Install dependencies before copying the full source code
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python source code files
COPY src/ /app/src/

# Set Python path to include src folder
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

# Copy the Streamlit app files into the container
COPY streamlit_app/ /streamlit_app/

# Copy all data files to /app/data inside the container
COPY data/ /app/data/

# Define a mountable volume for persistent data (optional)
# Remove this if you always mount the volume manually
VOLUME /app/data

# Copy the supervisord configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose both Jupyter Notebook and Streamlit ports
EXPOSE 8888 8501

# Start both Jupyter Notebook and Streamlit using supervisord
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

#-------------------OLD--------------------------------
# # Use Databricks minimal runtime as the base image
# FROM databricksruntime/minimal:15.4-LTS

# # Set the working directory inside the container
# WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y python3-pip supervisor && rm -rf /var/lib/apt/lists/*

# # Upgrade pip
# RUN pip install --upgrade pip

# # Copy requirements.txt and install dependencies
# COPY Docker/requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy all data files to /app/data inside the container
# COPY data/ /app/data/

# # Ensure the app/data directory exists (important for mounting)
# RUN mkdir -p /app/data

# # Define a mountable volume for persistent data
# VOLUME /app/data

# # Copy the Streamlit app files into the container
# COPY streamlit_app/ /streamlit_app/

# # Copy the supervisord configuration file
# COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# # Expose both Jupyter Notebook and Streamlit ports
# EXPOSE 8888 8501

# # Start both Jupyter Notebook and Streamlit using supervisord
# CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
