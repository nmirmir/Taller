DROP TABLE IF EXISTS objects;
DROP TABLE IF EXISTS zones;
DROP TABLE IF EXISTS categories;

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE objects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    zone_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'Available',
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (zone_id) REFERENCES zones (id),
    FOREIGN KEY (category_id) REFERENCES categories (id)
);

CREATE TABLE IF NOT EXISTS action_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL,
    object_id INTEGER NOT NULL,
    comment TEXT,
    creation_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert default categories
INSERT INTO categories (name) VALUES 
    ('Tools'),
    ('Equipment'),
    ('Materials'),
    ('Supplies'); 