from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
CREATE TABLE IF NOT EXISTS fin_account (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    account_type TEXT NOT NULL,
    balance REAL NOT NULL DEFAULT 0.0,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fin_category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    category_type TEXT NOT NULL,
    color TEXT NOT NULL DEFAULT '#6366f1',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fin_transaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    account_id INTEGER NOT NULL REFERENCES fin_account(id) ON DELETE RESTRICT,
    category_id INTEGER REFERENCES fin_category(id) ON DELETE SET NULL,
    amount REAL NOT NULL,
    transaction_type TEXT NOT NULL,
    description TEXT,
    date TEXT NOT NULL,
    receipt_image TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fin_budget (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES fin_category(id) ON DELETE CASCADE,
    amount REAL NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(user_id, category_id, month, year)
);
""",
            reverse_sql="""
DROP TABLE IF EXISTS fin_budget;
DROP TABLE IF EXISTS fin_transaction;
DROP TABLE IF EXISTS fin_category;
DROP TABLE IF EXISTS fin_account;
""",
        ),
    ]
