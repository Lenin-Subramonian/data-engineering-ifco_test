
## Key Optimizations in Docker File

**Resource Management**

  ```
  ENV JUPYTER_MAX_WORKERS=4
  ENV STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
  ENV MAX_WORKERS=4
  ENV MEMORY_LIMIT="4g"
  ```

**Added Health Checks**

Monitor container health

```
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/ || exit 1
```

**Added Cleanup Processes**

- Creates a cron job that runs every 15 minutes and deletes files in /tmp older than 1 day
- Helps prevent disk space issues and automatic cleanup of temporary files

```
RUN echo "*/15 * * * * find /tmp -type f -mtime +1 -delete" >> /etc/crontab
```

**Added Cache Management**

Manage cache and temporary files

```
ENV STREAMLIT_CACHE_TTL=3600
ENV JUPYTER_CACHE_DIR="/tmp/jupyter_cache"
```
