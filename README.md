# Inventory Management E-commerce Webapp

## Overview  
This project is a secure, full-stack inventory management and e-commerce application built with Python, Flask, and SQLite. It simulates a complete retail environment, managing user roles (Admin/User), dynamic inventory, and a secure payment pipeline integrated with Stripe

The application serves as a comprehensive demonstration of backend security best practices, data integrity via database transactions, and professional third-party API integration.

## Features  

### **Admin Functionalities:**  
- User Management: Add and manage users securely.
- Inventory Control: Add new items and update stock levels dynamically.
- Pricing: Edit item market prices.
- Order Visibility: View all current orders and access complete purchase history.
- Restocking Alerts: Track and manage out-of-stock items.


### **User Functionalities:**  
- Browse & Shop: Browse available items by category.
- Dynamic Shopping Cart: Add items to a session-based cart.
- Secure Checkout: Redirect to Stripe for secure payment processing.
- Order Management: View previous purchases and cancel non-finalized orders.

## **Key Technical & Security Highlights**
This project showcases a deep understanding of production-grade software development principles:

**1. Atomic Transactional Integrity**
- ACID Compliance: Implements database transactions (BEGIN TRANSACTION / COMMIT / ROLLBACK) within the Stripe Webhook handler.

- Guaranteed Consistency: This ensures that the stock deduction and order insertion are treated as a single, indivisible operation, preventing data corruption if a server crash occurs.

**2. Fraud-Proof Payment Pipeline**
- Secure Webhook: Utilizes a dedicated Stripe Webhook endpoint (/stripe-webhook) for server-to-server payment confirmation. This avoids client-side fraud entirely.

- Signature Verification: Employs stripe.Webhook.construct_event with a secret signing key to cryptographically verify that the payment confirmation message is authentic and untampered.

**3. Core Application Security**
- SQL Injection Prevention: All database operations utilize Parameterized Queries to securely handle user input.

- Secret Management: Sensitive keys (API keys, Flask secrets) are safely loaded using python-dotenv and Environment Variables, eliminating hardcoded secrets in the codebase.

- Access Control: Enforces role-based authorization using @login_required and explicit current_user.is_admin checks on all protected routes.



![WhatsApp Image 2025-03-26 at 7 40 31 PM](https://github.com/user-attachments/assets/002c6c0c-f987-4022-9375-22052d3a2816)
![WhatsApp Image 2025-03-26 at 7 39 45 PM](https://github.com/user-attachments/assets/2686ca4f-5a85-474b-9dd2-ad9a2b5f59ad)
![WhatsApp Image 2025-03-26 at 7 39 46 PM (1)](https://github.com/user-attachments/assets/bd08eaa4-9fb6-47e5-b375-a9a2f2cba20e)
![WhatsApp Image 2025-03-26 at 7 39 45 PM (8)](https://github.com/user-attachments/assets/5bf4bc49-012f-47bd-8dcc-8ab44ffd347b)
![WhatsApp Image 2025-03-26 at 7 39 46 PM](https://github.com/user-attachments/assets/0611f804-d0d7-4637-bce6-b696f5543e9d)
![WhatsApp Image 2025-03-26 at 7 39 45 PM (1)](https://github.com/user-attachments/assets/ce799a9e-8c2d-4fcf-bd32-8d4d189272c1)
![WhatsApp Image 2025-03-26 at 7 39 45 PM (3)](https://github.com/user-attachments/assets/97451dbd-4ce9-4607-8769-20c0e853ae77)
![WhatsApp Image 2025-03-26 at 7 39 45 PM (7)](https://github.com/user-attachments/assets/7406cef2-aa9d-4fd2-a6a1-d28003e41562)
![WhatsApp Image 2025-03-26 at 7 39 45 PM (6)](https://github.com/user-attachments/assets/00687209-2aa0-4e7b-9a11-ada55a14a111)
![WhatsApp Image 2025-03-26 at 7 39 45 PM (5)](https://github.com/user-attachments/assets/30f3496c-c21d-4be6-98ba-bbec9e0fd5ca)
![WhatsApp Image 2025-03-26 at 7 39 45 PM (4)](https://github.com/user-attachments/assets/2c87efe4-0d0e-4f69-8a8f-bf6919fd735e)


## Technology Stack Used
- **Back-end:** Python (Flask)  
- **Database:** SQLite3
- **Security:**Flask-Login, Werkzeug
- **Payment:**Stripe API
- **Front-end:** HTML, CSS
