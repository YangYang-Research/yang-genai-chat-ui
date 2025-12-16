FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    nginx \
    openssl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip3 install -r requirements.txt

# Generate self-signed certificate
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/nginx-selfsigned.key \
    -out /etc/ssl/certs/nginx-selfsigned.crt \
    -subj "/C=US/ST=State/L=City/O=YangYang/CN=localhost"

# Copy nginx configuration
COPY nginx.conf /etc/nginx/sites-available/default

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
# Start nginx\n\
nginx\n\
# Start streamlit in foreground\n\
exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 80 443

HEALTHCHECK CMD curl --fail --insecure https://localhost/_stcore/health

ENTRYPOINT ["/app/start.sh"]