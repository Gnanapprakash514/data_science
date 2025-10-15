FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy rest of the backend code
COPY . .

# Expose backend port (adjust if using Flask/FastAPI default)
EXPOSE 5000

# Run backend app
CMD ["python", "main.py"]
