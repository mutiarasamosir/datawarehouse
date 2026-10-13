
CREATE TABLE IF NOT EXISTS warehouse_load_log (
    source_file VARCHAR NOT NULL,
    source_sheet VARCHAR NOT NULL,
    target_table VARCHAR NOT NULL,
    row_count BIGINT NOT NULL,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
