# Fast-Backend

This is a simple backend service for an e-commerce application, built with FastAPI and MongoDB. It provides APIs for
managing products and orders.

## Features

* **Product Management**: Create and list products.
* **Order Management**: Create and list orders for users.
* **Database Integration**: Uses MongoDB for data storage.
* **Data Validation**: Pydantic models for request and response validation.

## Deployment

The application is deployed on Railway and is live.

* **Live Application**: https://fast-backend-production.up.railway.app/
* **API Docs (Swagger UI)**: https://fast-backend-production.up.railway.app/docs

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/bhavya257/fast-backend.git
   cd fast-backend
   ```

2. **Create a virtual environment and install dependencies:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root directory and add your MongoDB connection string:

   ```
   MONGO_URI="your_mongodb_connection_string"
   ```

## Usage

1. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```
2. **Access the API documentation:**
   Open your browser and go to `http://127.0.0.1:8000/docs` to see the interactive API documentation (Swagger UI).

### API Endpoints

* **Products**
    * `POST /products/`: Create a new product.
    * `GET /products/`: Get a list of products.
* **Orders**
    * `POST /orders/`: Create a new order.
    * `GET /orders/{user_id}`: Get a list of orders for a specific user.
