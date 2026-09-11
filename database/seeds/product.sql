INSERT INTO products (sku, name, price, is_active, created_at)
VALUES
  ('FS-KEYBOARD-01', 'Mechanical Keyboard', 2499.00, TRUE, CURRENT_TIMESTAMP),
  ('FS-MOUSE-01', 'Wireless Mouse', 999.00, TRUE, CURRENT_TIMESTAMP)
ON CONFLICT (sku) DO NOTHING;