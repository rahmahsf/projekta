-- Initialize databases for Projekta
CREATE DATABASE IF NOT EXISTS rs_rekom CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant privileges
GRANT ALL PRIVILEGES ON rs_pku.* TO 'projekta_user'@'%';
GRANT ALL PRIVILEGES ON rs_rekom.* TO 'projekta_user'@'%';

-- Flush privileges
FLUSH PRIVILEGES;
