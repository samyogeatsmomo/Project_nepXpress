import pymysql
from werkzeug.security import generate_password_hash


class Database:
    def __init__(self):
        self.connection = pymysql.connect(
            host="localhost",
            user="root",
            password="root1234",
            database="nepXpress",
            charset='utf8mb4'
        )

    def fetch_one(self, query, params=None):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return result

    def fetch_all(self, query, params=None):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result

    def execute(self, query, params=None):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        cursor.close()

    def close(self):
        self.connection.close()

    @staticmethod
    def create_tables():
        db = Database()

        # ── users table (unchanged) ───────────────────────────
        db.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "  id            INT PRIMARY KEY AUTO_INCREMENT,"
            "  name          VARCHAR(100)  NOT NULL,"
            "  email         VARCHAR(100)  NOT NULL UNIQUE,"
            "  password      VARCHAR(255)  NOT NULL,"
            "  role          VARCHAR(20)   NOT NULL DEFAULT 'customer',"
            "  created_at    TIMESTAMP     DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

        # Insert default admin user
        admin_password = generate_password_hash("admin123")
        db.execute(
            "INSERT IGNORE INTO users (name, email, password, role) "
            "VALUES (%s, %s, %s, %s)",
            ("Admin", "admin@admin.com", admin_password, "admin")
        )

        # ── orders table (new) ────────────────────────────────
        # customer_id is a FK → users.id but nullable so guest
        # orders are also possible in the future.
        db.execute(
            "CREATE TABLE IF NOT EXISTS orders ("
            "  id                   INT PRIMARY KEY AUTO_INCREMENT,"
            "  tracking_number      VARCHAR(20)   NOT NULL UNIQUE,"
            "  customer_id          INT           DEFAULT NULL,"

            # Sender
            "  sender_name          VARCHAR(100)  NOT NULL,"
            "  sender_phone         VARCHAR(20)   NOT NULL,"
            "  sender_address       VARCHAR(255)  NOT NULL,"
            "  sender_city          VARCHAR(100)  NOT NULL,"
            "  sender_district      VARCHAR(100)  NOT NULL,"

            # Receiver
            "  receiver_name        VARCHAR(100)  NOT NULL,"
            "  receiver_phone       VARCHAR(20)   NOT NULL,"
            "  receiver_address     VARCHAR(255)  NOT NULL,"
            "  receiver_city        VARCHAR(100)  NOT NULL,"
            "  receiver_district    VARCHAR(100)  NOT NULL,"

            # Package
            "  package_type         VARCHAR(50)   NOT NULL,"
            "  weight               DECIMAL(8,2)  NOT NULL DEFAULT 0.00,"
            "  estimated_value      DECIMAL(10,2) NOT NULL DEFAULT 0.00,"
            "  length               DECIMAL(8,2)  NOT NULL DEFAULT 0.00,"
            "  width                DECIMAL(8,2)  NOT NULL DEFAULT 0.00,"
            "  height               DECIMAL(8,2)  NOT NULL DEFAULT 0.00,"
            "  special_instructions TEXT          DEFAULT NULL,"

            # Delivery & Payment
            "  delivery_option      VARCHAR(20)   NOT NULL DEFAULT 'standard',"
            "  payment_method       VARCHAR(20)   NOT NULL DEFAULT 'cod',"
            "  delivery_fee         DECIMAL(8,2)  NOT NULL DEFAULT 150.00,"

            # Status & timestamps
            "  status               VARCHAR(30)   NOT NULL DEFAULT 'pending',"
            "  created_at           TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,"

            "  FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE SET NULL"
            ")"
        )

        db.close()
        print("✅ Database tables created successfully!")
