# Chatbot API

This is the backend of the chatbot application built with FastAPI. It handles user authentication, message management, and interacts with a PostgreSQL database.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Server](#running-the-server)
- [API Documentation](#api-documentation)

## Features

- User authentication with JWT tokens
- CRUD operations for messages
- Chatbot responses

## Prerequisites

Before you begin, ensure you have the following:

- **Python**: Version 3.8 or newer
- **PostgreSQL**: Ensure it is installed and running

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-username/chatbot-api.git
   cd chatbot-api
   
2. **Set up the Python virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt

## Running the Server

1. **Configure the PostgreSQL database**:
   
   Create a PostgreSQL database and update your `database.py` file with the database URL
   
   ```bash
   SQLALCHEMY_DATABASE_URL=postgresql://username:password@localhost:5432/chatbot_api

4. **Start the FastAPI server**:

   ```bash
   uvicorn main:app --reload

## API Documentation

Access the API documentation at `http://localhost:8000/docs` for interactive API testing.


