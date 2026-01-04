#!/usr/bin/env python3
"""
Миграция данных из SQLite в PostgreSQL
Запуск: python migrate_to_postgres.py
"""

import asyncio
import aiosqlite
import asyncpg
import os
from tqdm import tqdm
from config import DATABASE_PATH

# PostgreSQL настройки
POSTGRES_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/2ch_parser')

async def migrate_sqlite_to_postgres():
    """Миграция данных из SQLite в PostgreSQL"""

    print("🚀 Начинаем миграцию SQLite → PostgreSQL")

    # Подключение к SQLite
    sqlite_conn = await aiosqlite.connect(DATABASE_PATH)
    sqlite_conn.row_factory = aiosqlite.Row

    # Подключение к PostgreSQL
    postgres_conn = await asyncpg.connect(POSTGRES_URL)

    try:
        # Получить общее количество записей
        total_count = await sqlite_conn.execute_scalar("SELECT COUNT(*) FROM videos")
        print(f"📊 Найдено {total_count} записей для миграции")

        # Получить все данные из SQLite
        cursor = await sqlite_conn.execute("""
            SELECT id, url, thread_id, post_id, filename, original_name, board,
                   thumbnail, width, height, duration, size, found_at, is_active
            FROM videos
            ORDER BY id
        """)

        rows = await cursor.fetchall()
        print(f"📥 Загружено {len(rows)} записей из SQLite")

        # Очистить PostgreSQL таблицу
        await postgres_conn.execute("TRUNCATE TABLE videos RESTART IDENTITY")
        print("🗑️ Очищена таблица PostgreSQL")

        # Миграция данных с прогресс-баром
        batch_size = 1000
        migrated = 0

        with tqdm(total=len(rows), desc="Миграция") as pbar:
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i+batch_size]

                # Подготовить данные для вставки
                values = []
                for row in batch:
                    values.extend([
                        row['url'], row['thread_id'], row['post_id'], row['filename'],
                        row['original_name'], row['board'], row['thumbnail'], row['width'],
                        row['height'], row['duration'], row['size'], row['found_at'], row['is_active']
                    ])

                # Создать плейсхолдеры для батча
                placeholders = ','.join([f'(${j+1})' for j in range(len(values))])

                # Вставить батч
                query = f"""
                INSERT INTO videos
                (url, thread_id, post_id, filename, original_name, board, thumbnail, width, height, duration, size, found_at, is_active)
                VALUES {placeholders}
                """

                await postgres_conn.execute(query, *values)
                migrated += len(batch)
                pbar.update(len(batch))

        print(f"✅ Миграция завершена! Перенесено {migrated} записей")

        # Проверить количество
        postgres_count = await postgres_conn.fetchval("SELECT COUNT(*) FROM videos")
        print(f"🔍 Проверка: PostgreSQL содержит {postgres_count} записей")

        if postgres_count == total_count:
            print("🎉 Миграция успешна!")
        else:
            print(f"⚠️  Внимание: расхождение в количестве записей! SQLite: {total_count}, PostgreSQL: {postgres_count}")

    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        raise

    finally:
        await sqlite_conn.close()
        await postgres_conn.close()

async def create_alembic_setup():
    """Создать структуру для Alembic миграций"""

    print("\n📝 Настройка Alembic для будущих миграций...")

    # Создать директорию для миграций
    os.makedirs('alembic/versions', exist_ok=True)

    # Создать alembic.ini
    alembic_ini = f"""# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = alembic

# template used to generate migration files
# file_template = %%(rev)s_%%(slug)s

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# timezone =

# max length of characters to apply to the
# "slug" field
#truncate_slug_length = 40

# set to 'true' to run the environment file as a script, rather than importing it
# false = import as a module
# true = execute as a script
# script_execution_mode = false

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualifier =

[logger_sqlalchemy]
level = WARN
handlers =
qualifier = sqlalchemy

[logger_alembic]
level = INFO
handlers =
qualifier = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic
qualifier =

[formatter_generic]
format = %%(levelname)-5.5s [%%(name)s] %%(message)s
datefmt = %%H:%%M:%%S

[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts. See the documentation for further
# detail and examples

# keys are script names, values are functions to execute
# update_defaults =
# update_defaults =

[alembic:exclude]
tables = spatial_ref_sys

"""

    with open('alembic.ini', 'w') as f:
        f.write(alembic_ini)

    # Создать env.py для Alembic
    env_py = '''import asyncio
import asyncpg
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from database_postgres import get_db_pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''

    with open('alembic/env.py', 'w') as f:
        f.write(env_py)

    print("✅ Alembic настроен для будущих миграций")

if __name__ == "__main__":
    print("🗄️  МИГРАЦИЯ SQLITE → POSTGRESQL")
    print("=" * 50)

    asyncio.run(migrate_sqlite_to_postgres())
    asyncio.run(create_alembic_setup())

    print("\n🎯 Далее:")
    print("1. Протестируйте работу с PostgreSQL")
    print("2. Для будущих изменений схемы используйте: alembic revision --autogenerate")
    print("3. Применяйте миграции: alembic upgrade head")
