CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    amount REAL NOT NULL,
    payment_method TEXT NOT NULL,
    bank TEXT NOT NULL,
    merchant TEXT NOT NULL,
    region TEXT NOT NULL,
    status TEXT NOT NULL,
    latency_ms REAL NOT NULL,
    http_status INTEGER NOT NULL,
    error_code TEXT,
    retry_count INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_transactions_bank ON transactions(bank);
CREATE INDEX IF NOT EXISTS idx_transactions_method ON transactions(payment_method);
CREATE INDEX IF NOT EXISTS idx_transactions_region ON transactions(region);

CREATE TABLE IF NOT EXISTS incidents (
    incident_id TEXT PRIMARY KEY,
    incident_type TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    severity TEXT NOT NULL,
    affected_component TEXT NOT NULL,
    affected_bank TEXT,
    affected_payment_method TEXT,
    affected_region TEXT,
    expected_symptoms TEXT NOT NULL
);
