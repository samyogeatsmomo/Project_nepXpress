"""
=============================================================
  OrderModel — inherits BaseModel (Abstraction/Inheritance)
=============================================================
  Represents a shipment/order row in the `orders` table.
  Follows the exact same pattern as UserModel.py so the
  codebase stays consistent.
=============================================================
"""

from app.models.BaseModel import BaseModel
from app.models.database import Database
import random
import string


class Order(BaseModel):
    # ── tells BaseModel which table to query ──────────────────
    table = "orders"

    def __init__(
        self,
        customer_id=None,
        # Sender
        sender_name="",
        sender_phone="",
        sender_address="",
        sender_city="",
        sender_district="",
        # Receiver
        receiver_name="",
        receiver_phone="",
        receiver_address="",
        receiver_city="",
        receiver_district="",
        # Package
        package_type="",
        weight=0.0,
        estimated_value=0.0,
        length=0.0,
        width=0.0,
        height=0.0,
        special_instructions="",
        # Delivery & Payment
        delivery_option="standard",
        payment_method="cod",
        delivery_fee=150.0,
        # Status
        status="pending",
    ):
        self.id = None
        self.tracking_number = None          # auto-generated on save
        self.customer_id = customer_id

        self.sender_name = sender_name
        self.sender_phone = sender_phone
        self.sender_address = sender_address
        self.sender_city = sender_city
        self.sender_district = sender_district

        self.receiver_name = receiver_name
        self.receiver_phone = receiver_phone
        self.receiver_address = receiver_address
        self.receiver_city = receiver_city
        self.receiver_district = receiver_district

        self.package_type = package_type
        self.weight = weight
        self.estimated_value = estimated_value
        self.length = length
        self.width = width
        self.height = height
        self.special_instructions = special_instructions

        self.delivery_option = delivery_option
        self.payment_method = payment_method
        self.delivery_fee = delivery_fee

        self.status = status
        self.created_at = None

    # ── Generate a unique NXP-XXXXXX tracking number ─────────
    @staticmethod
    def generate_tracking_number():
        suffix = ''.join(random.choices(string.digits, k=6))
        return f"NXP-{suffix}"

    # ── Save a new order to the database ─────────────────────
    def save(self):
        """Insert a new order row and store the generated ID."""
        tracking = self.generate_tracking_number()
        self.tracking_number = tracking

        db = Database()
        query = (
            f"INSERT INTO {self.table} ("
            f"  tracking_number, customer_id,"
            f"  sender_name, sender_phone, sender_address, sender_city, sender_district,"
            f"  receiver_name, receiver_phone, receiver_address, receiver_city, receiver_district,"
            f"  package_type, weight, estimated_value, length, width, height, special_instructions,"
            f"  delivery_option, payment_method, delivery_fee, status"
            f") VALUES ("
            f"  %s, %s,"
            f"  %s, %s, %s, %s, %s,"
            f"  %s, %s, %s, %s, %s,"
            f"  %s, %s, %s, %s, %s, %s, %s,"
            f"  %s, %s, %s, %s"
            f")"
        )
        params = (
            tracking, self.customer_id,
            self.sender_name, self.sender_phone, self.sender_address,
            self.sender_city, self.sender_district,
            self.receiver_name, self.receiver_phone, self.receiver_address,
            self.receiver_city, self.receiver_district,
            self.package_type, self.weight, self.estimated_value,
            self.length, self.width, self.height, self.special_instructions,
            self.delivery_option, self.payment_method, self.delivery_fee,
            self.status,
        )
        db.execute(query, params)

        # Fetch the auto-incremented id back
        row = db.fetch_one(
            f"SELECT id FROM {self.table} WHERE tracking_number = %s",
            (tracking,)
        )
        if row:
            self.id = row["id"]

        db.close()
        return self.tracking_number

    # ── Fetch all orders belonging to one customer ────────────
    def find_by_customer(self, customer_id):
        db = Database()
        results = db.fetch_all(
            f"SELECT * FROM {self.table} WHERE customer_id = %s ORDER BY created_at DESC",
            (customer_id,)
        )
        db.close()
        return results

    # ── Update order status (used by admin / delivery agent) ──
    def update_status(self, order_id, new_status):
        db = Database()
        db.execute(
            f"UPDATE {self.table} SET status = %s WHERE id = %s",
            (new_status, order_id)
        )
        db.close()

    # ── Rebuild an Order object from a database dict row ──────
    @classmethod
    def from_db(cls, db_row):
        order = cls()
        for key, value in db_row.items():
            setattr(order, key, value)
        return order
