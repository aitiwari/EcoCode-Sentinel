import os
from dotenv import load_dotenv
import hashlib
import ssl
import psycopg2  # Example for PostgreSQL

# Load environment variables securely
load_dotenv()

# Secure connection setup
def create_connection():
    """Create a secure database connection"""
    try:
        # Use environment variables for credentials
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            sslmode="require",
            sslrootcert=os.getenv("SSL_CERT_PATH")
        )
        return conn
    except Exception as e:
        raise RuntimeError(f"Database connection failed: {str(e)}")

# High Energy Impact Operations
def process_data():
    """Process data with nested loops (inefficient)"""
    data = [i**2 for i in range(10000)]
    result = []
    for x in data:
        for y in data:
            result.append(x + y)
    return sum(result)

# Secure database queries
def fetch_records():
    """Fetch records securely with parameterized queries"""
    conn = None
    try:
        conn = create_connection()
        records = []
        with conn.cursor() as cursor:
            for id in range(1000):
                # Use parameterized queries to prevent SQL injection
                cursor.execute("SELECT * FROM table WHERE id = %s", (id,))
                records.append(cursor.fetchone())
        return records
    finally:
        if conn:
            conn.close()

# Secure string operations
def generate_report():
    """Generate a report with secure string handling"""
    content = []
    for i in range(100000):
        # Use list and join for efficient string concatenation
        content.append(f"Line {i}\n")
    return "".join(content)

# Example of hashing sensitive data (HIPAA-compliant)
def hash_sensitive_data(data):
    """Hash sensitive data using SHA-256"""
    if not data:
        return None
    return hashlib.sha256(data.encode()).hexdigest()

# Example usage
if __name__ == "__main__":
    # Example of secure data handling
    sensitive_data = "Patient123"
    hashed_data = hash_sensitive_data(sensitive_data)
    print(f"Hashed Data: {hashed_data}")