"""SQLite-safe ADD COLUMN for Postgres-only IF NOT EXISTS migrations."""


def column_names(schema_editor, table: str) -> set[str]:
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        return {
            col.name
            for col in connection.introspection.get_table_description(cursor, table)
        }


def add_column_if_missing(schema_editor, table: str, column: str, sql: str) -> None:
    if column in column_names(schema_editor, table):
        return
    schema_editor.execute(sql.replace(' IF NOT EXISTS', ''))
