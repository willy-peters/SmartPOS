SmartPOS – Retail Point of Sale System API
SmartPOS is a Django REST Framework-based API designed for small and medium-sized retail businesses, offering robust features for user authentication, product and inventory management, sales processing, and real-time analytics. It provides a scalable, secure, and modular backend to streamline retail operations.
🚀 Features

🔐 Authentication & Role Management  

JWT-based user authentication  
Role-based access control (Admin, Cashier)  
User registration, login/logout, profile management, and password updates


📦 Product & Inventory Management  

Full CRUD operations for products  
Real-time inventory tracking with low-stock alerts  
Product categorization and SKU-based identification


💰 Sales Management  

Multi-product transaction processing with automatic inventory updates  
Sales history with unique transaction IDs  
Price capture at sale time


📊 Reports & Analytics  

Sales summaries (daily, weekly, monthly)  
Top-selling product analysis and revenue reporting  
Inventory status and cashier performance reports



🛠 Tech Stack

Backend Framework: Django 4.2+  
API Framework: Django REST Framework  
Authentication: JWT (Simple JWT)  
Database: SQLite (Development), PostgreSQL (Production)  
Python: 3.8+

📚 API Overview
Base URL
http://localhost:8000

Authentication
Most endpoints require JWT-based authentication. Include the token in the request header:
Authorization: Token YOUR_TOKEN_HERE

Response Format
All responses follow this JSON structure:
{
  "status": "success" | "error",
  "message": "Description of result",
  "data": {} | []
}

Common Status Codes

200 OK: Successful GET/PUT/PATCH request  
201 Created: Successful POST request  
204 No Content: Successful DELETE request  
400 Bad Request: Validation error  
401 Unauthorized: Authentication required  
403 Forbidden: Permission denied  
404 Not Found: Resource not found

🔑 User Management & Authentication
Endpoints

POST /api/users/register/: Register a new user (no auth required)  
POST /api/users/login/: Authenticate and receive token (no auth required)  
POST /api/users/logout/: Invalidate token (auth required)  
GET /api/users/profile/: Retrieve user profile (auth required)  
PUT/PATCH /api/users/profile/: Update user profile (auth required)  
POST /api/users/change-password/: Change password (auth required)

Key Features

Supports Admin and Cashier roles with distinct permissions  
Secure user registration with password validation  
Profile updates and password management

📦 Product Management
Endpoints

GET /api/products/: List products with filtering (auth required)  
POST /api/products/: Create product (admin only)  
GET /api/products/{id}/: Retrieve product details (auth required)  
PUT/PATCH /api/products/{id}/: Update product (admin only)  
DELETE /api/products/{id}/: Delete product (admin only)  
GET /api/products/low-stock/: List low-stock products (auth required)

Key Features

Product CRUD with real-time inventory updates  
Filtering by price, stock, and search terms  
Low-stock alerts based on thresholds

💰 Sales Management
Endpoints

GET /api/sales/: List sales with filters (auth required)  
GET /api/sales/{id}/: Retrieve sale details (auth required, cashier limited to own sales)  
GET /api/sales/daily-summary/: Sales summary by date or range (auth required)

Key Features

Processes multi-product transactions  
Automatic inventory deduction  
Admin can view all sales; cashiers view only their own

📊 Reports & Analytics
Endpoints

GET /api/reports/sales/: Sales reports by period (admin only)  
GET /api/reports/inventory/: Inventory status report (admin only)  
GET /api/reports/cashier-performance/: Cashier performance report (admin only)  
GET /api/reports/product-performance/: Product sales performance (admin only)

Key Features

Detailed sales, inventory, and cashier performance analytics  
Customizable reports by period, cashier, or product  
Insights into top-selling products and revenue trends

🧪 Testing with Postman
Workflow

User Setup: Register admin/cashier, login, and save tokens  
Product Management: Create, update, and list products; verify low-stock alerts  
Sales Processing: Create transactions, verify inventory updates, and check sales history  
Reports: Generate and validate sales, inventory, and performance reports

Sample Test Data
[
  {
    "name": "Laptop HP ProBook",
    "cost_price": "800.00",
    "selling_price": "999.99",
    "stock_quantity": 10,
    "low_stock_threshold": 2
  },
  {
    "name": "Wireless Mouse",
    "cost_price": "15.00",
    "selling_price": "29.99",
    "stock_quantity": 50,
    "low_stock_threshold": 10
  }
]

🚧 Error Handling

Validates input data (e.g., negative prices, missing fields)  
Enforces permissions (e.g., admin-only endpoints)  
Handles invalid tokens, non-existent resources, and business logic errors (e.g., insufficient stock)
