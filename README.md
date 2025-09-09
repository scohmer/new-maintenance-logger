# Maintenance Logger

A maintenance logging system with client-server architecture for tracking IT maintenance activities.

## Features

- **FastAPI Backend**: RESTful API with SQLite database
- **Desktop Client**: Tkinter GUI with LDAP integration
- **Web Interface**: Responsive HTML interface for viewing logs
- **Export Functionality**: CSV export with filtering options
- **Docker Support**: Containerized deployment ready

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- SSL certificates (optional, for HTTPS)

### Deploy with Docker

1. **Default deployment (HTTP with nginx reverse proxy):**
```bash
docker-compose up -d
```

2. **Direct deployment (without nginx):**
```bash
docker-compose --profile direct up -d
```

3. **Access the application:**
- With nginx: http://localhost:80
- Direct access: http://localhost:8000 (when using --profile direct)

### Adding HTTPS Later

To enable HTTPS, place your SSL certificates in `./tls/` directory and update the nginx.conf to uncomment the HTTPS server block.

### Manual Setup

Create a .env file with the following variables:

```bash
# API server (your FastAPI backend)  
API_SERVER_IP = "server.domain.com"                  # Replace with your server IP or hostname  
API_SERVER_PORT = 8000  

# LDAP connection details  
LDAP_SERVER = "ldap://dc01.seancohmer.com"           # Replace with your AD server  
LDAP_USER = "SEANCOHMER\\ldap_read"                  # Replace with AD bind account  
LDAP_PASSWORD = 'Pa$$w0rd'                           # Replace with password  
LDAP_BASE_DN = "DC=seancohmer,DC=com"                # Replace with your domain base DN  
```

### Traditional Deployment

#### Server Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --no-index --find-links=./server-depends/ -r ./server-requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Client Setup
```bash
python -m venv venv
.\venv\Scripts\activate.bat
pip install --no-index --find-links=.\client-depends -r .\client-requirements.txt
python client.py
```

#### Create Executable
```bash
pyinstaller -F --add-data=".env;." .\client.py
```
# Server Interface
Here is a screenshot of the server interface:  

![Server Interface](screenshots/server-interface.png)

# Client Interface
Here is a screenshot of the client interface:

![Client Interface](screenshots/client-interface.png)

# Note: Cleanup required

I'm aware that there's a bit of cleanup necessary.