
# Start from a lightweight Python 3.11 image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the dependency file
COPY requirements.txt .

# Install the required frontend packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit application into the container
COPY . .

# Document Streamlit's application port
EXPOSE 8501

# Start the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
