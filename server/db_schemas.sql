PRAGMA foreign_keys = ON;

-- =====================
-- USERS
-- =====================
CREATE TABLE UserInfo (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    balance       REAL NOT NULL DEFAULT 0,
    public_key_e    TEXT,
    public_key_n    TEXT,
    created_at    INTEGER NOT NULL                -- unix timestamp
);

-- =====================
-- AUCTIONS
-- =====================
CREATE TABLE Auctions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id   TEXT NOT NULL,
    title       TEXT NOT NULL,
    description TEXT,
    base_price  REAL NOT NULL,
    created_at  INTEGER NOT NULL,                 -- unix timestamp
    end_at      INTEGER NOT NULL,
    status      TEXT NOT NULL DEFAULT 'ACTIVE',

    FOREIGN KEY (seller_id) REFERENCES UserInfo(id)
);

-- =====================
-- IMAGES
-- =====================
CREATE TABLE Images (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    auction_id INTEGER NOT NULL,
    is_cover   BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (auction_id) REFERENCES Auctions(id) ON DELETE CASCADE
);

-- =====================
-- BIDS
-- =====================
CREATE TABLE Bids (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    auction_id INTEGER NOT NULL,
    user_id    TEXT NOT NULL,                     -- UUID (string)
    created_at INTEGER NOT NULL,                  -- unix timestamp
    price      REAL NOT NULL,

    FOREIGN KEY (auction_id) REFERENCES Auctions(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES UserInfo(id) ON DELETE CASCADE
);
