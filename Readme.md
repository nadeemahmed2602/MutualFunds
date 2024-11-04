
# Mutual Fund Broker Web Application with RapidAPI Integration

This is a FastAPI application for managing mutual funds. It allows users to log in, register, and add funds to their watchlist.

## Table of Contents
- [File Structure](#file-structure)
- [Requirements](#requirements)
- [Setup](#setup)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [E2E Testing](#e2e-testing)
- [Documentation](#documentation)
- [License](#license)

## File Structure
- `main.py` - Entry point for the FastAPI application
- `models.py` - SQLAlchemy models 
- `schemas.py` - Pydantic schemas for request/response validation 
- `database.py` - Database configuration
- `requirements.txt` - Project dependencies 
- Static files (HTML, CSS, JS)
  - `login.html`
  - `register.html`
  - `dashboard.html`
- `README.md` - Project documentation

## Requirements
Make sure you have Python 3.7 or later installed. You can create a virtual environment and install the required packages using the following command:

### Required Packages
- FastAPI
- Uvicorn
- SQLAlchemy
- Passlib
- Requests

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://your-repository-url.git
   cd your-repository-name

2. Export Environment Variables:
You can set the required environment variables using the following commands:
```bash
export SECRET_KEY=your-secreate-key
export RAPIDAPI_KEY=your-api-key
```

3.	Install the dependencies:

```
pip install -r requirements.txt

```

## Running the Application

### Start the FastAPI server:

```
uvicorn main:app --reload
```


The application will be accessible at http://127.0.0.1:8000.

### Open your browser and navigate to:

	Login Page - http://127.0.0.1:8000/
	Register Page - http://127.0.0.1:8000/register
	Dashboard - http://127.0.0.1:8000/dashboard
	Watchlist - http://127.0.0.1:8000/watchlist
	API Documentation (ReDoc) - http://127.0.0.1:8000/redocs
	API Documentation (Swagger UI) - http://127.0.0.1:8000/docs

## API Endpoints

### Authentication

```
POST /register

```
Request Body:

```
{
  "email": "user@example.com",
  "password": "your_password"
}

```
Response:
```
{
  "message": "User registered successfully",
  "email": "user@example.com"
}

```
```
POST /login
```
Request Body:
```
{
  "email": "user@example.com",
  "password": "your_password"
}

```

Response:

```
{
  "message": "Login successful",
  "access_token": "your_access_token"
}
```




###  Fund Management

```angular2html
POST /fetch_funds
```
Request Body:

```
{
  "family": "SBI Mutual Fund"
}
```

Response:
```
{
  "funds": [ ... ]
}
```


```
GET /fund_family
```
Response:
```
[
  {
    "id": 1,
    "name": "SBI Mutual Fund"
  },
  ...
]
```



### Watchlist Management

```
POST /addtowatchlist
```
Request Body:

```
{
  "scheme_code": "XYZ123",
  "fund_family_id": "SBI Mutual Fund"
}
```

Response:

```
{
  "message": "Item added to watchlist",
  "item_id": 1
}
```

```
GET /watchlist
```

Response:
```
[
  {
    "id": 1,
    "fund_family_id": "SBI Mutual Fund"
  },
  ...
]
```

