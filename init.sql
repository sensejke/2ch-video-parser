-- Инициализация PostgreSQL базы данных для 2ch Video Parser

-- Создание пользователя с ограниченными правами (опционально)
-- CREATE USER parser_user WITH PASSWORD 'secure_password';
-- GRANT ALL PRIVILEGES ON DATABASE "2ch_parser" TO parser_user;

-- Настройки производительности
-- ALTER SYSTEM SET shared_buffers = '256MB';
-- ALTER SYSTEM SET effective_cache_size = '1GB';
-- ALTER SYSTEM SET work_mem = '4MB';
-- ALTER SYSTEM SET maintenance_work_mem = '64MB';

-- Создание таблицы (если не создана через код)
-- CREATE TABLE IF NOT EXISTS videos (
--     id SERIAL PRIMARY KEY,
--     url TEXT NOT NULL,
--     thread_id TEXT,
--     post_id TEXT,
--     filename TEXT,
--     original_name TEXT,
--     board TEXT,
--     thumbnail TEXT,
--     width INTEGER,
--     height INTEGER,
--     duration TEXT,
--     size BIGINT,
--     found_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
--     is_active BOOLEAN DEFAULT TRUE
-- );

-- Создание индексов (если не созданы через код)
-- CREATE INDEX IF NOT EXISTS idx_found_at ON videos(found_at DESC);
-- CREATE INDEX IF NOT EXISTS idx_board ON videos(board);
-- CREATE INDEX IF NOT EXISTS idx_url ON videos(url);
-- CREATE UNIQUE INDEX IF NOT EXISTS idx_url_board ON videos(url, board);
-- CREATE INDEX IF NOT EXISTS idx_active_found_at ON videos(is_active, found_at DESC);
-- CREATE INDEX IF NOT EXISTS idx_board_active_found_at ON videos(board, is_active, found_at DESC);
-- CREATE INDEX IF NOT EXISTS idx_active_board ON videos(is_active, board);

-- Комментарий
COMMENT ON DATABASE "2ch_parser" IS '2ch.org Video Parser Database';
-- COMMENT ON TABLE videos IS 'Видео файлы с 2ch досок';
