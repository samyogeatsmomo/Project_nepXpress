from app.models.database import Database

db = Database()
result = db.fetch_one("SELECT id, name, email, role FROM users WHERE email=%s", ("admin@admin.com",))
print(result)
db.close()