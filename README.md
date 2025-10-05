## 📱 Pixel Point — Online Electronics Store

Pixel Point is a modern online electronics store built with **Django**, featuring secure payments via **LiqPay** and automatic delivery integration with **Nova Poshta API**.
It provides users with a convenient way to browse, purchase, and receive electronic products across Ukraine.
<img width="1920" height="954" alt="image" src="https://github.com/user-attachments/assets/c8115fe9-dede-4584-a7cd-09cd11d7a08e" />

---

### 🚀 Features

* 🛍️ Product catalog with categories and descriptions
* 💳 Secure payments through **LiqPay**
* 🚚 Automated delivery with **Nova Poshta API**
* 🧾 Order management and database tracking
* 📱 Responsive and user-friendly interface
* ⚙️ Admin panel for product and order management

---

### 🧠 Tech Stack

* **Backend:** Django 5
* **Frontend:** HTML, CSS
* **Database:** PostgreSQL
* **Payments:** LiqPay SDK
* **Delivery:** Nova Poshta API
* **Environment:** Python 3.12, PyCharm

---

### ⚙️ Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/pixel-point.git
   cd pixel-point/Project/Djangoproject
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate   # on macOS/Linux
   venv\Scripts\activate      # on Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**

   ```bash
   python manage.py migrate
   ```

5. **Run the development server**

   ```bash
   python manage.py runserver
   ```

6. Open your browser and go to
   👉 `http://127.0.0.1:8000/`

---

### ⚙️ Post-Installation Steps (Admin Setup)

After you've run the server, your product catalog will be empty. To start adding products and managing orders, you need to access the Django Admin panel.

1.  **Create a Superuser:**
    You must create an administrator account to log into the panel.
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts in your terminal to set your username, email, and password.

2.  **Access the Admin Panel:**
    Open your web browser and navigate to the admin interface:
    👉 `http://127.0.0.1:8000/admin/`

3.  **Add Products:**
    Log in with the superuser credentials you just created. Use the **Products** and **Categories** sections of the admin panel to populate your store's catalog and begin managing your inventory.

---

### 📂 Project Structure

```
Project/
└── Djangoproject/
    ├── Djangoproject/      # Core Django settings and URLs
    ├── main/               # Main app (views, models, templates)
    ├── liqpay/             # LiqPay SDK integration
    ├── db.sqlite3          # Local database
    └── manage.py           # Entry point
```

---

### 🧾 Environment Variables

Create a `.env` file in the project root to store your credentials:

```
SECRET_KEY=django-insecure-your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,yourdomain.com
DB_NAME=YourDatabaseName
DB_USER=YourDbUser
DB_PASSWORD=YourDbPassword
DB_HOST=localhost
DB_PORT=5432
LIQPAY_PUBLIC_KEY=your_liqpay_public_key
LIQPAY_PRIVATE_KEY=your_liqpay_private_key
LIQPAY_SANDBOX=True
NOVA_POSHTA_API_KEY=your_nova_poshta_api_key
NP_API_URL=https://api.novaposhta.ua/v2.0/json/
```

---


