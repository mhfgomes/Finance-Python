from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
ALTER TABLE fin_account ADD COLUMN currency TEXT NOT NULL DEFAULT 'EUR';

CREATE TABLE IF NOT EXISTS fin_exchange_rate (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    currency TEXT NOT NULL UNIQUE,
    rate_to_eur REAL NOT NULL DEFAULT 1.0,
    updated_at TEXT NOT NULL
);

INSERT OR IGNORE INTO fin_exchange_rate (currency, rate_to_eur, updated_at) VALUES
    ('EUR', 1.0,    '2026-02-18'),
    ('USD', 0.96,   '2026-02-18'),
    ('GBP', 1.20,   '2026-02-18'),
    ('CHF', 1.05,   '2026-02-18'),
    ('JPY', 0.0062, '2026-02-18'),
    ('CAD', 0.68,   '2026-02-18'),
    ('AUD', 0.60,   '2026-02-18');
""",
            reverse_sql="""
DROP TABLE IF EXISTS fin_exchange_rate;
""",
        ),
    ]
