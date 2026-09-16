"""Schema leftovers after a code rollback (later NOT NULL columns still in DB)."""
from django.db import connection
from django.utils import timezone


def _accepts_empty_string(col):
    name = col.name
    if name.endswith(('_cs', '_en', '_ru')) or name == 'site_url':
        return True
    type_code = getattr(col, 'type_code', None)
    if isinstance(type_code, str):
        lowered = type_code.lower()
        return any(token in lowered for token in ('char', 'text', 'clob'))
    return type_code in (25, 1042, 1043)


def leftover_not_null_columns(model):
    table = model._meta.db_table
    model_cols = {field.column for field in model._meta.local_concrete_fields}
    with connection.cursor() as cursor:
        descriptions = connection.introspection.get_table_description(cursor, table)
    leftovers = []
    for col in descriptions:
        name = col.name
        if name in model_cols or name == 'id' or name.endswith('_id'):
            continue
        if getattr(col, 'null_ok', True):
            continue
        if not _accepts_empty_string(col):
            continue
        leftovers.append(name)
    return leftovers


def ensure_leftover_not_null_defaults(model):
    """
    Postgres: SET DEFAULT '' on leftover NOT NULL columns so ORM INSERT can omit them.
    SQLite cannot ALTER COLUMN DEFAULT — caller should use create_with_leftovers.
    """
    leftovers = leftover_not_null_columns(model)
    if not leftovers or connection.vendor != 'postgresql':
        return leftovers
    qn = connection.ops.quote_name
    table = qn(model._meta.db_table)
    with connection.cursor() as cursor:
        for col in leftovers:
            quoted = qn(col)
            cursor.execute(
                f"ALTER TABLE {table} ALTER COLUMN {quoted} SET DEFAULT ''"
            )
            cursor.execute(
                f"UPDATE {table} SET {quoted} = '' WHERE {quoted} IS NULL"
            )
    return leftovers


def create_with_leftovers(model, **kwargs):
    leftovers = leftover_not_null_columns(model)
    if not leftovers:
        return model.objects.create(**kwargs)
    if connection.vendor == 'postgresql':
        ensure_leftover_not_null_defaults(model)
        return model.objects.create(**kwargs)

    obj = model(**kwargs)
    cols = []
    vals = []
    for field in model._meta.local_concrete_fields:
        if field.primary_key and getattr(field, 'auto_created', False):
            continue
        if getattr(field, 'auto_now', False) or getattr(field, 'auto_now_add', False):
            value = timezone.now()
            setattr(obj, field.attname, value)
        else:
            value = getattr(obj, field.attname)
        cols.append(field.column)
        vals.append(value)
    cols.extend(leftovers)
    vals.extend([''] * len(leftovers))
    qn = connection.ops.quote_name
    table = qn(model._meta.db_table)
    col_sql = ', '.join(qn(c) for c in cols)
    placeholders = ', '.join(['%s'] * len(cols))
    with connection.cursor() as cursor:
        cursor.execute(
            f'INSERT INTO {table} ({col_sql}) VALUES ({placeholders})',
            vals,
        )
        obj.pk = cursor.lastrowid
    obj._state.adding = False
    obj._state.db = 'default'
    return obj
