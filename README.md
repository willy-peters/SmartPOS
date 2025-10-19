# **SmartPOS – Retail Point of Sale System API**

**SmartPOS** is a **Django REST Framework–based API** designed for small and medium-sized retail businesses. It offers robust features for user authentication, product and inventory management, sales processing, and real-time analytics.
The system provides a **scalable, secure, and modular backend** to streamline retail operations.

---

## 🚀 **Features**

### **Authentication & Role Management**

* JWT-based user authentication
* Role-based access control (**Admin**, **Cashier**)
* User registration, login/logout, profile management, and password updates

### **Product & Inventory Management**

* Full **CRUD** operations for products
* Real-time inventory tracking with **low-stock alerts**
* Product categorization and **SKU-based identification**

### **Sales Management**

* Multi-product transaction processing with **automatic inventory updates**
* Sales history with **unique transaction IDs**
* Price capture at sale time

### **Reports & Analytics**

* Sales summaries (**daily**, **weekly**, **monthly**)
* Top-selling product and revenue reporting
* Inventory status and cashier performance reports

---

## 🛠 **Tech Stack**

| Component             | Technology                                    |
| --------------------- | --------------------------------------------- |
| **Backend Framework** | Django 4.2+                                   |
| **API Framework**     | Django REST Framework                         |
| **Authentication**    | JWT (Simple JWT)                              |
| **Database**          | SQLite (Development), PostgreSQL (Production) |
| **Python Version**    | 3.8+                                          |

---

## 📚 **API Overview**

### **Base URL**

```
http://localhost:8000
```

### **Authentication**

Most endpoints require JWT-based authentication.
Include the token in the request header:

```
Authorization: Token YOUR_TOKEN_HERE
```

### **Response Format**

All responses follow this JSON structure:

```json
{
  "status": "success" | "error",
  "message": "Description of result",
  "data": {} | []
}
```

### **Common Status Codes**

| Code                 | Meaning                          |
| -------------------- | -------------------------------- |
| **200 OK**           | Successful GET/PUT/PATCH request |
| **201 Created**      | Successful POST request          |
| **204 No Content**   | Successful DELETE request        |
| **400 Bad Request**  | Validation error                 |
| **401 Unauthorized** | Authentication required          |
| **403 Forbidden**    | Permission denied                |
| **404 Not Found**    | Resource not found               |

---

## 🔑 **User Management & Authentication**

### **Endpoints**

| Method        | Endpoint                      | Description                    | Auth Required |
| ------------- | ----------------------------- | ------------------------------ | ------------- |
| **POST**      | `/api/users/register/`        | Register a new user            | No            |
| **POST**      | `/api/users/login/`           | Authenticate and receive token | No            |
| **POST**      | `/api/users/logout/`          | Invalidate token               | Yes           |
| **GET**       | `/api/users/profile/`         | Retrieve user profile          | Yes           |
| **PUT/PATCH** | `/api/users/profile/`         | Update user profile            | Yes           |
| **POST**      | `/api/users/change-password/` | Change password                | Yes           |

### **Key Features**

* Supports **Admin** and **Cashier** roles with distinct permissions
* Secure user registration with password validation
* Profile updates and password management

---

## 📦 **Product Management**

### **Endpoints**

| Method        | Endpoint                   | Description                    | Auth Required |
| ------------- | -------------------------- | ------------------------------ | ------------- |
| **GET**       | `/api/products/`           | List products (with filtering) | Yes           |
| **POST**      | `/api/products/`           | Create product                 | Admin only    |
| **GET**       | `/api/products/{id}/`      | Retrieve product details       | Yes           |
| **PUT/PATCH** | `/api/products/{id}/`      | Update product                 | Admin only    |
| **DELETE**    | `/api/products/{id}/`      | Delete product                 | Admin only    |
| **GET**       | `/api/products/low-stock/` | List low-stock products        | Yes           |

### **Key Features**

* Product CRUD with real-time inventory updates
* Filtering by **price**, **stock**, and **search terms**
* **Low-stock alerts** based on predefined thresholds

---

## 💰 **Sales Management**

### **Endpoints**

| Method  | Endpoint                    | Description                    | Auth Required                         |
| ------- | --------------------------- | ------------------------------ | ------------------------------------- |
| **GET** | `/api/sales/`               | List sales with filters        | Yes                                   |
| **GET** | `/api/sales/{id}/`          | Retrieve sale details          | Yes *(Cashiers limited to own sales)* |
| **GET** | `/api/sales/daily-summary/` | Sales summary by date or range | Yes                                   |

### **Key Features**

* Processes **multi-product transactions**
* Automatic **inventory deduction** after sale
* **Admins** can view all sales; **Cashiers** see only their own

---

## 📊 **Reports & Analytics**

### **Endpoints**

| Method  | Endpoint                            | Description                | Access     |
| ------- | ----------------------------------- | -------------------------- | ---------- |
| **GET** | `/api/reports/sales/`               | Sales reports by period    | Admin only |
| **GET** | `/api/reports/inventory/`           | Inventory status report    | Admin only |
| **GET** | `/api/reports/cashier-performance/` | Cashier performance report | Admin only |
| **GET** | `/api/reports/product-performance/` | Product sales performance  | Admin only |

### **Key Features**

* Detailed sales, inventory, and performance analytics
* Customizable reports by **period**, **cashier**, or **product**
* Insights into **top-selling products** and **revenue trends**

---

## 🧪 **Testing with Postman**

### **Recommended Workflow**

1. **User Setup** – Register admin/cashier, log in, and store tokens.
2. **Product Management** – Create, update, and list products; verify low-stock alerts.
3. **Sales Processing** – Create sales transactions and confirm inventory updates.
4. **Reports** – Generate and validate sales, inventory, and performance reports.

### **Sample Test Data**

```json
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
```

---

## 🚧 **Error Handling**

* Validates input data (e.g., negative prices, missing fields)
* Enforces permissions (**Admin-only endpoints**)
* Handles invalid tokens, missing resources, and business logic errors (e.g., insufficient stock)
