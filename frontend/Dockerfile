FROM python:3.11-slim

WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the frontend code
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Run Streamlit frontend
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
