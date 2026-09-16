"""Schema leftovers after a code rollback (later NOT NULL columns still in DB)."""
import json
import time
from pathlib import Path

from django.db import connection
from django.utils import timezone

# #region agent log
_DEBUG_LOG = Path('/Users/sofiadmitrenko/prometeyRenova/.cursor/debug-104b19.log')
_LOGGED_TABLES = set()


def _agent_log(hypothesis_id, location, message, data):
    payload = {
        'sessionId': '104b19',
        'hypothesisId': hypothesis_id,
        'location': location,
        'message': message,
        'data': data,
        'timestamp': int(time.time() * 1000),
        'runId': 'post-fix-alter',
    }
    try:
        with _DEBUG_LOG.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + '\n')
    except OSError:
        pass
    print(f'[debug-104b19] {hypothesis_id} {message} {data}', flush=True)
# #endregion


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
    pk_col = qn(model._meta.pk.column)
    col_sql = ', '.join(qn(c) for c in cols)
    placeholders = ', '.join(['%s'] * len(cols))
    insert_sql = f'INSERT INTO {table} ({col_sql}) VALUES ({placeholders})'
    # #region agent log
    if model._meta.db_table not in _LOGGED_TABLES:
        _LOGGED_TABLES.add(model._meta.db_table)
        _agent_log(
            'H',
            'legacy_schema.py:create_with_leftovers',
            'raw-insert-leftovers',
            {
                'table': model._meta.db_table,
                'vendor': connection.vendor,
                'in_atomic': connection.in_atomic_block,
                'leftovers': leftovers,
                'will_alter': False,
            },
        )
    # #endregion
    with connection.cursor() as cursor:
        if connection.vendor == 'postgresql':
            cursor.execute(f'{insert_sql} RETURNING {pk_col}', vals)
            obj.pk = cursor.fetchone()[0]
        else:
            cursor.execute(insert_sql, vals)
            obj.pk = cursor.lastrowid
    obj._state.adding = False
    obj._state.db = 'default'
    return obj
