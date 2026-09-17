import json
import sqlite3
import bcrypt
from datetime import datetime

from procesador_excel import (
    DEFAULT_JSON_HIJO, DEFAULT_JSON_PADRE, DEFAULT_MAPPING,
    DEFAULT_JSON_TRANSPORTE, DEFAULT_JSON_TRANSPORTE_HIJO, DEFAULT_MAPPING_TRANSPORTE,
    DEFAULT_COLUMNA_RECORRIDO_TRANSPORTE, DEFAULT_COLUMNA_PROFESIONAL_TRANSPORTE,
)

DB_PATH = "users.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) as count FROM users")
    if cursor.fetchone()["count"] == 0:
        hashed = bcrypt.hashpw("AdminCeder345".encode("utf-8"), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
            ("adminceder", hashed.decode("utf-8"), 1),
        )
        conn.commit()
        print("Usuario admin creado -> adminceder / AdminCeder345")

    conn.close()
    init_upload_logs()
    get_config_json()


def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return dict(user)
    return None


def create_user(username, password, is_admin=False):
    conn = get_connection()
    cursor = conn.cursor()
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    try:
        cursor.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
            (username, hashed.decode("utf-8"), 1 if is_admin else 0),
        )
        conn.commit()
        return True, "Usuario creado exitosamente"
    except sqlite3.IntegrityError:
        return False, "El nombre de usuario ya existe"
    finally:
        conn.close()


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, is_admin, created_at FROM users")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users


def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ? AND is_admin = 0", (user_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted > 0


def init_upload_logs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS upload_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            exitoso INTEGER NOT NULL,
            registros_procesados INTEGER DEFAULT 0,
            nombre_archivo TEXT,
            tipo TEXT DEFAULT ''
        )
    """)
    try:
        cursor.execute("ALTER TABLE upload_logs ADD COLUMN tipo TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE upload_logs ADD COLUMN usuario TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()


def log_upload(nombre_archivo, exitoso, registros_procesados=0, tipo="", usuario=""):
    now = datetime.now()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO upload_logs (fecha, hora, exitoso, registros_procesados, nombre_archivo, tipo, usuario) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), 1 if exitoso else 0, registros_procesados, nombre_archivo, tipo, usuario),
    )
    cursor.execute("SELECT COUNT(*) as total FROM upload_logs")
    total = cursor.fetchone()["total"]
    if total > 300:
        cursor.execute(
            "DELETE FROM upload_logs WHERE id IN ("
            "SELECT id FROM upload_logs ORDER BY id ASC LIMIT 50)"
        )
    conn.commit()
    conn.close()


def get_upload_logs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM upload_logs ORDER BY id DESC")
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return logs


def get_config_json():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS config_json (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            contenido TEXT NOT NULL DEFAULT '{}',
            contenido_hijo TEXT NOT NULL DEFAULT '{}',
            mapeo TEXT NOT NULL DEFAULT '[]'
        )
    """)
    for col, default in [
        ("contenido_hijo", "'{}'"),
        ("mapeo", "'[]'"),
        ("ep_ip", "'190.71.116.82'"),
        ("ep_puerto", "'9000'"),
        ("ep_email", "''"),
        ("ep_password", "''"),
        ("ep_iapp", "'1001'"),
        ("ep_idmaquina", "'POSTMAN-TEST'"),
        ("ep_keyagente", "''"),
        ("contenido_transporte", "'{}'"),
        ("contenido_transporte_hijo", "'{}'"),
        ("mapeo_transporte", "'[]'"),
        ("columna_recorrido_transporte", "''"),
        ("columna_profesional_transporte", "''"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE config_json ADD COLUMN {col} TEXT NOT NULL DEFAULT {default}")
        except sqlite3.OperationalError:
            pass
    conn.commit()

    cursor.execute(
        "SELECT contenido, contenido_hijo, mapeo, ep_ip, ep_puerto, ep_email, ep_password, ep_iapp, ep_idmaquina, ep_keyagente, contenido_transporte, contenido_transporte_hijo, mapeo_transporte, columna_recorrido_transporte, columna_profesional_transporte "
        "FROM config_json WHERE id = 1"
    )
    row = cursor.fetchone()
    default_padre = json.dumps(DEFAULT_JSON_PADRE, ensure_ascii=False, indent=2)
    default_hijo = json.dumps(DEFAULT_JSON_HIJO, ensure_ascii=False, indent=2)
    default_mapeo = json.dumps(DEFAULT_MAPPING, ensure_ascii=False, indent=2)
    default_transporte = json.dumps(DEFAULT_JSON_TRANSPORTE, ensure_ascii=False, indent=2)
    default_transporte_hijo = json.dumps(DEFAULT_JSON_TRANSPORTE_HIJO, ensure_ascii=False, indent=2)
    default_mapeo_transporte = json.dumps(DEFAULT_MAPPING_TRANSPORTE, ensure_ascii=False, indent=2)
    if not row:
        cursor.execute(
            "INSERT INTO config_json (id, contenido, contenido_hijo, mapeo, contenido_transporte, contenido_transporte_hijo, mapeo_transporte, columna_recorrido_transporte, columna_profesional_transporte) "
            "VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                default_padre, default_hijo, default_mapeo,
                default_transporte, default_transporte_hijo, default_mapeo_transporte,
                DEFAULT_COLUMNA_RECORRIDO_TRANSPORTE, DEFAULT_COLUMNA_PROFESIONAL_TRANSPORTE,
            ),
        )
        conn.commit()
        return {
            "json_padre": default_padre, "json_hijo": default_hijo, "mapeo": default_mapeo,
            "ep_ip": "190.71.116.82", "ep_puerto": "9000", "ep_email": "", "ep_password": "",
            "ep_iapp": "1001", "ep_idmaquina": "POSTMAN-TEST", "ep_keyagente": "",
            "json_transporte": default_transporte,
            "json_transporte_hijo": default_transporte_hijo,
            "mapeo_transporte": default_mapeo_transporte,
            "columna_recorrido_transporte": DEFAULT_COLUMNA_RECORRIDO_TRANSPORTE,
            "columna_profesional_transporte": DEFAULT_COLUMNA_PROFESIONAL_TRANSPORTE,
        }
    else:
        contenido = row["contenido"]
        contenido_hijo = row["contenido_hijo"]
        mapeo = row["mapeo"]
        contenido_transporte = row["contenido_transporte"]
        contenido_transporte_hijo = row["contenido_transporte_hijo"]
        mapeo_transporte = row["mapeo_transporte"]
        columna_recorrido_transporte = row["columna_recorrido_transporte"] or ""
        columna_profesional_transporte = row["columna_profesional_transporte"] or ""
        actualizar = False
        if not contenido or contenido.strip() == "{}":
            contenido = default_padre
            actualizar = True
        if not contenido_hijo or contenido_hijo.strip() == "{}":
            contenido_hijo = default_hijo
            actualizar = True
        if not mapeo or mapeo.strip() == "[]":
            mapeo = default_mapeo
            actualizar = True
        if not contenido_transporte or contenido_transporte.strip() in ("{}", "") or \
                contenido_transporte.strip() == default_padre.strip():
            contenido_transporte = default_transporte
            actualizar = True
        if not contenido_transporte_hijo or contenido_transporte_hijo.strip() == "{}":
            contenido_transporte_hijo = default_transporte_hijo
            actualizar = True
        if not mapeo_transporte or mapeo_transporte.strip() in ("[]", "") or \
                mapeo_transporte.strip() == default_mapeo.strip():
            mapeo_transporte = default_mapeo_transporte
            actualizar = True
        if not columna_recorrido_transporte:
            columna_recorrido_transporte = DEFAULT_COLUMNA_RECORRIDO_TRANSPORTE
            actualizar = True
        if not columna_profesional_transporte:
            columna_profesional_transporte = DEFAULT_COLUMNA_PROFESIONAL_TRANSPORTE
            actualizar = True
        if actualizar:
            cursor.execute(
                "UPDATE config_json SET contenido = ?, contenido_hijo = ?, mapeo = ?, contenido_transporte = ?, "
                "contenido_transporte_hijo = ?, mapeo_transporte = ?, columna_recorrido_transporte = ?, "
                "columna_profesional_transporte = ? WHERE id = 1",
                (
                    contenido, contenido_hijo, mapeo, contenido_transporte,
                    contenido_transporte_hijo, mapeo_transporte,
                    columna_recorrido_transporte, columna_profesional_transporte,
                ),
            )
            conn.commit()
    conn.close()
    return {
        "json_padre": contenido, "json_hijo": contenido_hijo, "mapeo": mapeo,
        "ep_ip": row["ep_ip"] or "190.71.116.82", "ep_puerto": row["ep_puerto"] or "9000",
        "ep_email": row["ep_email"] or "", "ep_password": row["ep_password"] or "",
        "ep_iapp": row["ep_iapp"] or "1001", "ep_idmaquina": row["ep_idmaquina"] or "POSTMAN-TEST",
        "ep_keyagente": row["ep_keyagente"] or "",
        "json_transporte": contenido_transporte,
        "json_transporte_hijo": contenido_transporte_hijo,
        "mapeo_transporte": mapeo_transporte,
        "columna_recorrido_transporte": columna_recorrido_transporte,
        "columna_profesional_transporte": columna_profesional_transporte,
    }


def save_config_json(contenido, contenido_hijo="{}", mapeo="[]", endpoint=None,
                     contenido_transporte="{}", contenido_transporte_hijo="{}",
                     mapeo_transporte="[]",
                     columna_recorrido_transporte=DEFAULT_COLUMNA_RECORRIDO_TRANSPORTE,
                     columna_profesional_transporte=DEFAULT_COLUMNA_PROFESIONAL_TRANSPORTE):
    conn = get_connection()
    cursor = conn.cursor()
    if endpoint:
        cursor.execute(
            "UPDATE config_json SET contenido = ?, contenido_hijo = ?, mapeo = ?, "
            "ep_ip = ?, ep_puerto = ?, ep_email = ?, ep_password = ?, ep_iapp = ?, ep_idmaquina = ?, ep_keyagente = ?, "
            "contenido_transporte = ?, contenido_transporte_hijo = ?, mapeo_transporte = ?, "
            "columna_recorrido_transporte = ?, columna_profesional_transporte = ? "
            "WHERE id = 1",
            (
                contenido, contenido_hijo, mapeo,
                endpoint.get("ep_ip", ""), endpoint.get("ep_puerto", "9000"),
                endpoint.get("ep_email", ""), endpoint.get("ep_password", ""),
                endpoint.get("ep_iapp", "1001"), endpoint.get("ep_idmaquina", ""),
                endpoint.get("ep_keyagente", ""),
                contenido_transporte, contenido_transporte_hijo, mapeo_transporte,
                columna_recorrido_transporte, columna_profesional_transporte,
            ),
        )
    else:
        cursor.execute(
            "UPDATE config_json SET contenido = ?, contenido_hijo = ?, mapeo = ?, contenido_transporte = ?, "
            "contenido_transporte_hijo = ?, mapeo_transporte = ?, columna_recorrido_transporte = ?, "
            "columna_profesional_transporte = ? WHERE id = 1",
            (
                contenido, contenido_hijo, mapeo, contenido_transporte,
                contenido_transporte_hijo, mapeo_transporte,
                columna_recorrido_transporte, columna_profesional_transporte,
            ),
        )
    conn.commit()
    conn.close()
