# **SmartPOS – Retail Point of Sale System API**

**SmartPOS** is a **Django REST Framework–based API** designed for small and medium-sized retail businesses. It offers robust features for user authentication, product and inventory management and sales processing.

---

## **Features**

### **Authentication & Role Management**

- JWT-based user authentication
- Role-based access control (**Admin**, **Cashier**)
- User registration, login/logout

### **Product & Inventory Management**

- Full **CRUD** operations for products
- Real-time inventory tracking with **low-stock alerts**
- Product categorization and **SKU-based identification**

### **Sales Management**

- Multi-product transaction processing with **automatic inventory updates**
- Sales history with **unique transaction IDs**
- Price capture at sale time

## **Tech Stack**

| Component             | Technology            |
| --------------------- | --------------------- |
| **Backend Framework** | Django 4.2+           |
| **API Framework**     | Django REST Framework |
| **Authentication**    | JWT (Simple JWT)      |
| **Database**          | SQLite (Development)  |
| **Python Version**    | 3.8+                  |

---

## **API Overview**

### **Base URL**

```
http://localhost:8000
```

### **Authentication**

Most endpoints require JWT-based authentication.
Include the token in the request header:

```
Authorization: Bearer YOUR_TOKEN_HERE
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

## **Authentication**

### **Endpoints**

| Method   | Endpoint              | Description                    | Auth Required |
| -------- | --------------------- | ------------------------------ | ------------- |
| **POST** | `/api/auth/register/` | Register a new user            | No            |
| **POST** | `/api/auth/login/`    | Authenticate and receive token | No            |
| **POST** | `/api/auth/logout/`   | Invalidate token               | Yes           |

### **Key Features**

- Supports **Admin** and **Cashier** roles with distinct permissions
- Secure user registration with password validation

---

## **Product Management**

### **Endpoints**

| Method     | Endpoint                                     | Description                    | Auth Required |
| ---------- | -------------------------------------------- | ------------------------------ | ------------- |
| **GET**    | `/api/products/`                             | List products (with filtering) | Yes           |
| **POST**   | `/api/products/`                             | Create product                 | Admin only    |
| **GET**    | `/api/products/{id}/`                        | Retrieve product details       | Yes           |
| **PUT**    | `/api/products/{id}/`                        | Update product                 | Admin only    |
| **DELETE** | `/api/products/{id}/`                        | Delete product                 | Admin only    |
| **GET**    | `/api/products/low-stock/`                   | List low-stock products        | Yes           |
| **GET**    | `/api/products/low-stock/?threshold={value}` | List out-of-stock products     | Yes           |
| **GET**    | `/api/products/out-of-stock/`                | List out-of-stock products     | Yes           |

### **Key Features**

- Product CRUD with real-time inventory updates
- Filtering by **price**, **stock**, and **search terms**
- **Low-stock alerts** based on predefined thresholds

---

## **Sales Management**

### **Endpoints**

| Method   | Endpoint                                    | Description                    | Auth Required                         |
| -------- | ------------------------------------------- | ------------------------------ | ------------------------------------- |
| **GET**  | `/api/sales/`                               | List sales with filters        | Yes                                   |
| **GET**  | `/api/sales/{id}/`                          | Retrieve sale details          | Yes _(Cashiers limited to own sales)_ |
| **GET**  | `/api/sales/daily-summary/`                 | Sales summary by date or range | Yes                                   |
| **GET**  | `/api/sales/daily-summary/?date=YYYY-MM-DD` | Sales summary by date or range | Yes                                   |
| **POST** | `/api/sales/`                               | Register a new sell            | Yes                                   |

### **Key Features**

- Processes **multi-product transactions**
- Automatic **inventory deduction** after sale
- **Admins** can view all sales; **Cashiers** see only their own

---

## **User Management**

### **Endpoints**

| Method     | Endpoint           | Description           | Auth Required |
| ---------- | ------------------ | --------------------- | ------------- |
| **GET**    | `/api/users/`      | List users            | Admin only    |
| **POST**   | `/api/users/`      | Create user           | Admin only    |
| **GET**    | `/api/users/{id}/` | Retrieve user details | Admin only    |
| **PUT**    | `/api/users/{id}/` | Update user           | Admin only    |
| **DELETE** | `/api/users/{id}/` | Delete user           | Admin only    |

### **Key Features**

- Users CRUD with real-time user detail updates

---

## **Testing with Postman**

### **Recommended Workflow**

1. **User Setup** – Register admin/cashier, log in, and store tokens.
2. **Product Management** – Create, update, and list products; verify low-stock alerts.
3. **Sales Processing** – Create sales transactions and confirm inventory updates.

### **Sample Test Data and Results**

### **Authentication**

1. **Registration**
   **POST** `/api/auth/register/`
   User Data:

```json
{
  "username": "Gabriel",
  "email": "gabriel@gmail.com",
  "password": "password@05",
  "password_confirm": "password@05",
  "role": "admin",
  "first_name": "Gabriel",
  "last_name": "Owen"
}
```

Sample Response:

```json
{
  "message": "User created successfully.",
  "user": {
    "id": 20,
    "username": "Gabriel",
    "email": "gabriel@gmail.com",
    "role": "admin",
    "first_name": "Gabriel",
    "last_name": "Owen",
    "created_at": "2025-10-28T15:07:28.360801Z",
    "updated_at": "2025-10-28T15:07:29.829857Z"
  }
}
```

2. **Login**
   **POST** `/api/auth/login/`
   User Data:

```json
{
  "username": "Gabriel",
  "password": "password@05"
}
```

Sample Response:

```json
{
  "message": "Login successful.",
  "user": {
    "id": 20,
    "username": "Gabriel",
    "email": "gabriel@gmail.com",
    "role": "admin",
    "first_name": "Gabriel",
    "last_name": "Owen",
    "created_at": "2025-10-28T15:07:28.360801Z",
    "updated_at": "2025-10-28T15:07:29.829857Z"
  },
  "tokens": {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2MjI2OTA5MSwiaWF0IjoxNzYxNjY0MjkxLCJqdGkiOiJlNWI4NDA0ODU4OGM0YWE0YjM0YWU3NTdhZGU3ODdlZiIsInVzZXJfaWQiOiIyMCJ9.dOglG632aVzIjbQE0-I9Crum1OO9UGuiZzkSH8ig94g",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYxNjY3ODkxLCJpYXQiOjE3NjE2NjQyOTEsImp0aSI6IjIyZjVmMDg5MTEyMzQxZWQ4NjlmMzA0ZjE4ODNlNmI1IiwidXNlcl9pZCI6IjIwIn0.Q_r0X4ATyFqF39hT1Jwkrxb_f13bLlOtVOn1qkLS-WQ"
  }
}
```

3. **Logout**
   **POST** `/api/auth/logout/`
   User Data:

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2MjI2OTA5MSwiaWF0IjoxNzYxNjY0MjkxLCJqdGkiOiJlNWI4NDA0ODU4OGM0YWE0YjM0YWU3NTdhZGU3ODdlZiIsInVzZXJfaWQiOiIyMCJ9.dOglG632aVzIjbQE0-I9Crum1OO9UGuiZzkSH8ig94g"
}
```

Sample Response:

```json
{ "message": "Logout successful" }
```

### **User Management**

1. **User Registration**
   **POST** `/api/users/`
   User Data:

```json
{
  "username": "TestUser",
  "email": "test1@gmail.com",
  "password": "password@05",
  "password_confirm": "password@05",
  "role": "cashier",
  "first_name": "Test",
  "last_name": "User"
}
```

Sample Response:

```json
{
  "id": 21,
  "username": "TestUser",
  "email": "test1@gmail.com",
  "role": "cashier",
  "first_name": "Test",
  "last_name": "User",
  "created_at": "2025-10-28T15:23:58.097089Z",
  "updated_at": "2025-10-28T15:23:59.518806Z"
}
```

2. **Get all users**
   **GET** `/api/users/`

Sample Response:

```json
{
  "count": 20,
  "next": "http://127.0.0.1:8000/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 21,
      "username": "TestUser",
      "email": "test1@gmail.com",
      "role": "cashier",
      "first_name": "Test",
      "last_name": "User",
      "created_at": "2025-10-28T15:23:58.097089Z",
      "updated_at": "2025-10-28T15:23:59.518806Z"
    },
    {
      "id": 20,
      "username": "Gabriel",
      "email": "gabriel@gmail.com",
      "role": "admin",
      "first_name": "Gabriel",
      "last_name": "Owen",
      "created_at": "2025-10-28T15:07:28.360801Z",
      "updated_at": "2025-10-28T15:07:29.829857Z"
    },
    {
      "id": 19,
      "username": "Peter",
      "email": "peter@gmail.com",
      "role": "admin",
      "first_name": "Peter",
      "last_name": "Nguyamu",
      "created_at": "2025-10-27T07:59:27.933486Z",
      "updated_at": "2025-10-27T07:59:29.378586Z"
    },
    {
      "id": 18,
      "username": "Davey",
      "email": "dave@gmail.com",
      "role": "admin",
      "first_name": "Davey",
      "last_name": "Norman",
      "created_at": "2025-10-23T07:57:34.348238Z",
      "updated_at": "2025-10-23T07:57:35.884374Z"
    }
  ]
}
```

3. **Update a user**
   **PUT** `/api/users/{id}/`
   User Data:

```json
{
  "username": "TestUser",
  "email": "test2@gmail.com",
  "password": "password@05",
  "password_confirm": "password@05",
  "role": "cashier",
  "first_name": "Test",
  "last_name": "User"
}
```

Sample Response:

```json
{
  "id": 21,
  "username": "TestUser",
  "email": "test2@gmail.com",
  "role": "cashier",
  "first_name": "Test",
  "last_name": "User",
  "created_at": "2025-10-28T15:23:58.097089Z",
  "updated_at": "2025-10-28T15:27:52.576033Z"
}
```

4. **Delete a user**
   **DELETE** `/api/users/{id}/`

Sample Response:
**Status: 204 No Content**

### **Product Management**

1. **Get all products**
   **GET** `/api/products/`

Sample Response:

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 6,
      "name": "Mouthwash 2L",
      "sku": "OIL016",
      "category": "Antidotes",
      "unit_price": "19.50",
      "quantity_in_stock": 15,
      "low_stock_threshold": 5,
      "is_low_stock": false,
      "is_out_of_stock": false,
      "created_at": "2025-10-27T08:51:19.794420Z",
      "updated_at": "2025-10-27T08:51:19.794469Z"
    },
    {
      "id": 1,
      "name": "Coca Cola 500ml",
      "sku": "BEV001",
      "category": "Beverages",
      "unit_price": "1.50",
      "quantity_in_stock": 97,
      "low_stock_threshold": 20,
      "is_low_stock": false,
      "is_out_of_stock": false,
      "created_at": "2025-10-18T10:00:00Z",
      "updated_at": "2025-10-27T09:11:19.933200Z"
    },
    {
      "id": 2,
      "name": "Bread Loaf",
      "sku": "BAK001",
      "category": "Bakery",
      "unit_price": "2.00",
      "quantity_in_stock": 3,
      "low_stock_threshold": 5,
      "is_low_stock": true,
      "is_out_of_stock": false,
      "created_at": "2025-10-18T10:00:00Z",
      "updated_at": "2025-10-18T10:00:00Z"
    },
    {
      "id": 3,
      "name": "Milk 1L",
      "sku": "DAI001",
      "category": "Dairy",
      "unit_price": "3.50",
      "quantity_in_stock": 46,
      "low_stock_threshold": 10,
      "is_low_stock": false,
      "is_out_of_stock": false,
      "created_at": "2025-10-18T10:00:00Z",
      "updated_at": "2025-10-27T09:11:19.929340Z"
    },
    {
      "id": 4,
      "name": "Rice 5kg",
      "sku": "GRN001",
      "category": "Grains",
      "unit_price": "15.00",
      "quantity_in_stock": 6,
      "low_stock_threshold": 5,
      "is_low_stock": false,
      "is_out_of_stock": false,
      "created_at": "2025-10-18T10:00:00Z",
      "updated_at": "2025-10-27T07:26:40.049345Z"
    }
  ]
}
```

2. **Add a product**
   **POST** `/api/products/`
   User Data:

```json
{
  "name": "Detergent 2L",
  "sku": "OIL019",
  "category": "Soaps",
  "unit_price": "19.50",
  "quantity_in_stock": 15,
  "low_stock_threshold": 5
}
```

Sample Response:

```json
{
  "id": 6,
  "name": "Detergent 2L",
  "sku": "OIL019",
  "category": "Soaps",
  "unit_price": "19.50",
  "quantity_in_stock": 15,
  "low_stock_threshold": 5,
  "created_at": "2025-10-27T16:58:45.239Z"
}
```

3. **Edit a product**
   **PUT** `/api/products/`
   User Data:

```json
{
  "name": "Detergent 2L",
  "sku": "OIL020",
  "category": "Soaps",
  "unit_price": "19.50",
  "quantity_in_stock": 15,
  "low_stock_threshold": 5
}
```

Sample Response:

```json
{
  "id": 6,
  "name": "Detergent 2L",
  "sku": "OIL020",
  "category": "Soaps",
  "unit_price": "19.50",
  "quantity_in_stock": 15,
  "low_stock_threshold": 5,
  "created_at": "2025-10-27T16:58:45.239Z"
}
```

4. **Delete a product**
   **DELETE** `/api/products/{id}`

Sample Response:
**Status: 204 No Content**

5. **Get low-stock products**
   **GET** `/api/products/low-stock/` | `/api/products/low-stock/?threshold={value}`

Sample Response:

```json
{
  "status": "success",
  "count": 1,
  "data": [
    {
      "id": 2,
      "name": "Bread Loaf",
      "sku": "BAK001",
      "category": "Bakery",
      "unit_price": "2.00",
      "quantity_in_stock": 3,
      "low_stock_threshold": 5,
      "is_low_stock": true,
      "is_out_of_stock": false,
      "created_at": "2025-10-18T10:00:00Z",
      "updated_at": "2025-10-18T10:00:00Z"
    }
  ]
}
```

6. **Get out-of-stock products**
   **GET** `/api/products/out-of-stock/`

Sample Response:

```json
{
  "status": "success",
  "count": 1,
  "data": [
    {
      "id": 2,
      "name": "Toilet Paper",
      "sku": "BAK001",
      "category": "Cleaning",
      "unit_price": "2.00",
      "quantity_in_stock": 0,
      "low_stock_threshold": 5,
      "is_low_stock": true,
      "is_out_of_stock": true,
      "created_at": "2025-10-18T10:00:00Z",
      "updated_at": "2025-10-18T10:00:00Z"
    }
  ]
}
```

### **Sales Management**

1. **Registration**
   **POST** `/api/sales/`
   User Data:

```json
{
  "cashier": 1,
  "items": [
    {
      "product_id": 3,
      "quantity": 2,
      "price_at_sale": 29.99
    },
    {
      "product_id": 1,
      "quantity": 1,
      "price_at_sale": 49.99
    }
  ]
}
```

Sample Response:

```json
{
  "status": "success",
  "message": "Sale created successfully",
  "data": {
    "id": 3,
    "transaction_id": "TXN-02649E28AE3B",
    "sale_date": "2025-10-28T15:57:57.316055Z",
    "cashier": 18,
    "cashier_username": "Davey",
    "cashier_name": "Davey Norman",
    "total_amount": "109.97",
    "items": [
      {
        "id": 5,
        "product_name": "Milk 1L",
        "quantity": 2,
        "price_at_sale": "29.99",
        "subtotal": "59.98"
      },
      {
        "id": 6,
        "product_name": "Coca Cola 500ml",
        "quantity": 1,
        "price_at_sale": "49.99",
        "subtotal": "49.99"
      }
    ]
  }
}
```

2. **Get all sales**
   **GET** `/api/sales/` | `/api/sales/{id}/`

Sample Response:

```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 3,
      "transaction_id": "TXN-02649E28AE3B",
      "sale_date": "2025-10-28T15:57:57.316055Z",
      "cashier_username": "Davey",
      "total_amount": "109.97",
      "items_count": 2
    },
    {
      "id": 2,
      "transaction_id": "TXN-35FBE6AB72C3",
      "sale_date": "2025-10-27T09:11:19.927316Z",
      "cashier_username": "Davey",
      "total_amount": "159.96",
      "items_count": 2
    },
    {
      "id": 1,
      "transaction_id": "TXN-FD3B437E2063",
      "sale_date": "2025-10-27T09:10:21.444268Z",
      "cashier_username": "Davey",
      "total_amount": "109.97",
      "items_count": 2
    }
  ]
}
```

3. **Get daily-sale summary**
   **GET** `/api/sales/daily-summary/` | `/api/sales/daily-summary/?date=YYYY-MM-DD`

Sample Response:

```json
{
  "status": "success",
  "data": {
    "date": "2025-10-28",
    "total_sales": 2,
    "total_revenue": 219.94,
    "total_items_sold": 3,
    "average_sale_value": 109.97,
    "sales_by_cashier": [
      {
        "cashier__id": 18,
        "cashier__username": "Davey",
        "cashier__first_name": "Davey",
        "cashier__last_name": "Norman",
        "sales_count": 1,
        "revenue": 109.97
      }
    ]
  }
}
```

---

## **Error Handling**

- Validates input data (e.g., negative prices, missing fields)
- Enforces permissions (**Admin-only endpoints**)
- Handles invalid tokens, missing resources, and business logic errors (e.g., insufficient stock)
