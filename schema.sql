-- Database schema for homeCloud application
-- Drop existing tables if they exist
DROP TABLE IF EXISTS shares;
DROP TABLE IF EXISTS files;
DROP TABLE IF EXISTS users;

-- Table for storing shared folders
CREATE TABLE shares (
    md5 TEXT PRIMARY KEY,        -- MD5 hash of the folder path
    path TEXT NOT NULL           -- File system path to the shared folder
);

-- Table for storing files within shares
CREATE TABLE files (
    sharemd5 TEXT NOT NULL,      -- MD5 hash of the parent share
    md5 TEXT PRIMARY KEY,        -- MD5 hash of the file path
    path TEXT NOT NULL,          -- File system path to the file
    mimetype TEXT NOT NULL       -- MIME type of the file
);

-- Table for storing user accounts
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique user ID
    username TEXT UNIQUE NOT NULL,         -- Username for login
    password_hash TEXT NOT NULL,           -- Hashed password
    is_admin INTEGER NOT NULL DEFAULT 0    -- Admin flag (1 for admin, 0 for regular user)
);
