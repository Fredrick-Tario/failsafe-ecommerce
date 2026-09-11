INSERT INTO inventory_items (product_id, available, reserved, updated_at)
VALUES
  (1, 25, 0, CURRENT_TIMESTAMP),
  (2, 40, 0, CURRENT_TIMESTAMP)
ON CONFLICT (product_id) DO NOTHING;