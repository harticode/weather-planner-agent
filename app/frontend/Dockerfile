FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY streamlit_app.py .

# Streamlit config
RUN mkdir -p /root/.streamlit && \
    printf "[server]\nheadless = true\nport = 8501\n\n[browser]\ngatherUsageStats = false\n" > /root/.streamlit/config.toml

EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
