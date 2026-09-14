import hashlib
import json
import os
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from database import (
    init_db, verify_user, create_user, get_all_users, delete_user,
    log_upload, get_upload_logs, get_config_json, save_config_json,
)

app = Flask(__name__)
app.secret_key = "cargue-ceder-secret-key-2026"

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        if not session.get("is_admin"):
            flash("No tienes permisos de administrador", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = verify_user(username, password)
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = user["is_admin"]
            flash(f"Bienvenido {user['username']}", "success")
            return redirect(url_for("dashboard"))
        flash("Usuario o contraseña incorrectos", "danger")
    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/dashboard-transportes")
@login_required
def dashboard_transportes():
    return render_template("dashboard_transportes.html")


@app.route("/upload", methods=["POST"])
@login_required
def upload():
    if "excel_file" not in request.files:
        flash("No se seleccionó ningún archivo", "danger")
        return redirect(url_for("dashboard"))

    file = request.files["excel_file"]
    if file.filename == "":
        flash("No se seleccionó ningún archivo", "danger")
        return redirect(url_for("dashboard"))

    allowed = (".xlsx", ".xls")
    if not file.filename.lower().endswith(allowed):
        flash("Solo se permiten archivos Excel (.xlsx, .xls)", "danger")
        log_upload(file.filename, False, 0, tipo="Madres")
        return redirect(url_for("dashboard"))

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        import pandas as pd
        from procesador_excel import generar_jsons
        from servicio_api import (
            get_auth, extraer_keyagente, get_base_url, enviar_operacion,
            extraer_encabezado, detalle_respuesta,
        )

        df = pd.read_excel(filepath)
        num_registros = len(df)
        cfg = get_config_json()
        json_padre = cfg["json_padre"]
        json_hijo = cfg["json_hijo"]
        mapeo = cfg["mapeo"]
        creados, registros_json, error, archivos_generados = generar_jsons(
            df, file.filename, json_padre, json_hijo, mapeo
        )
        if error:
            log_upload(file.filename, False, num_registros, tipo="Madres")
            flash(f"No se pudo generar el JSON: {error}", "danger")
            return redirect(url_for("dashboard"))

        log_upload(file.filename, True, num_registros, tipo="Madres")

        if not cfg.get("ep_email") or not cfg.get("ep_password"):
            flash(
                "JSONs generados pero no se enviaron: configura el Email y la contraseña del endpoint.",
                "warning",
            )
            return redirect(url_for("dashboard"))

        try:
            auth_resp = get_auth(cfg)
        except Exception as exc:
            flash(f"Error al autenticar (GetAuth): {str(exc)}", "danger")
            return redirect(url_for("dashboard"))

        encabezado_auth = extraer_encabezado(auth_resp)
        if encabezado_auth.get("resultado") != "true":
            flash(
                f"Autenticación fallida (GetAuth): {encabezado_auth.get('mensaje', 'Sin detalle')} "
                f"[imensaje {encabezado_auth.get('imensaje', '')}]",
                "danger",
            )
            return redirect(url_for("dashboard"))

        keyagente = extraer_keyagente(auth_resp)
        if not keyagente:
            flash("No se obtuvo el keyagente de la autenticación.", "danger")
            return redirect(url_for("dashboard"))

        save_config_json(
            json_padre, json_hijo, cfg["mapeo"],
            endpoint={
                "ep_ip": cfg["ep_ip"], "ep_puerto": cfg["ep_puerto"],
                "ep_email": cfg["ep_email"], "ep_password": cfg["ep_password"],
                "ep_iapp": cfg["ep_iapp"], "ep_idmaquina": cfg["ep_idmaquina"],
                "ep_keyagente": keyagente,
            },
            contenido_transporte=cfg["json_transporte"],
            mapeo_transporte=cfg["mapeo_transporte"],
        )

        exitosos = 0
        fallidos = []
        resultados = []
        for ruta in archivos_generados:
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    oprdata = json.load(f)
                opr_resp = enviar_operacion(cfg, keyagente, oprdata)
                enc = extraer_encabezado(opr_resp)
                ok = enc.get("resultado", "false") == "true"
                if ok:
                    exitosos += 1
                else:
                    fallidos.append(ruta)
                resultados.append({
                    "archivo": ruta,
                    "ok": ok,
                    "mensaje": enc.get("mensaje", ""),
                    "imensaje": enc.get("imensaje", ""),
                    "detalle": detalle_respuesta(opr_resp),
                })
            except Exception as exc:
                fallidos.append(ruta)
                resultados.append({
                    "archivo": ruta,
                    "ok": False,
                    "mensaje": str(exc),
                    "imensaje": "",
                })

        flash(
            f"Archivo '{file.filename}' procesado. Registros: {num_registros}. "
            f"JSON generados: {creados}. Enviados: {exitosos}. Fallidos: {len(fallidos)}.",
            "success" if not fallidos else "warning",
        )
        for res in resultados:
            estado = "EXITOSO" if res["ok"] else "FALLIDO"
            mensaje = res.get("detalle") or res.get("mensaje") or "Sin detalle"
            flash(f"[{estado}] {res['archivo']}: {mensaje}", "success" if res["ok"] else "danger")
    except Exception as e:
        log_upload(file.filename, False, 0, tipo="Madres")
        flash(f"Error al procesar el archivo: {str(e)}", "danger")

    return redirect(url_for("dashboard"))


@app.route("/upload-transportes", methods=["POST"])
@login_required
def upload_transportes():
    if "excel_file" not in request.files:
        flash("No se seleccionó ningún archivo", "danger")
        return redirect(url_for("dashboard_transportes"))

    file = request.files["excel_file"]
    if file.filename == "":
        flash("No se seleccionó ningún archivo", "danger")
        return redirect(url_for("dashboard_transportes"))

    allowed = (".xlsx", ".xls")
    if not file.filename.lower().endswith(allowed):
        flash("Solo se permiten archivos Excel (.xlsx, .xls)", "danger")
        log_upload(file.filename, False, 0, tipo="Transportes")
        return redirect(url_for("dashboard_transportes"))

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        import pandas as pd

        df = pd.read_excel(filepath)
        num_registros = len(df)
        cfg = get_config_json()
        json_transporte = cfg["json_transporte"]
        mapeo_transporte = cfg["mapeo_transporte"]
        log_upload(file.filename, True, num_registros, tipo="Transportes")
        flash(
            f"Archivo '{file.filename}' recibido. Registros detectados: {num_registros}. "
            f"La generación de JSON de transportes se implementará próximamente.",
            "info",
        )
    except Exception as e:
        log_upload(file.filename, False, 0, tipo="Transportes")
        flash(f"Error al procesar el archivo: {str(e)}", "danger")

    return redirect(url_for("dashboard_transportes"))


@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin_panel():
    message = None
    msg_type = None

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        is_admin = "is_admin" in request.form
        success, message = create_user(username, password, is_admin)
        msg_type = "success" if success else "danger"

    users = get_all_users()
    return render_template("admin.html", users=users, message=message, msg_type=msg_type)


@app.route("/admin/delete/<int:user_id>", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    if user_id == session.get("user_id"):
        flash("No puedes eliminarte a ti mismo", "danger")
    elif delete_user(user_id):
        flash("Usuario eliminado", "success")
    else:
        flash("No se pudo eliminar el usuario", "danger")
    return redirect(url_for("admin_panel"))


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for("login"))


@app.route("/config-json", methods=["GET", "POST"])
@admin_required
def config_json():
    if request.method == "POST":
        json_padre = request.form.get("json_padre", "{}")
        json_hijo = request.form.get("json_hijo", "[]")
        campos_json = request.form.getlist("campo_json")
        campos_excel = request.form.getlist("campo_excel")

        json_transporte = request.form.get("json_transporte", "{}")
        campos_json_transporte = request.form.getlist("campo_json_transporte")
        campos_excel_transporte = request.form.getlist("campo_excel_transporte")

        ep_email = request.form.get("ep_email", "")
        ep_password = request.form.get("ep_password", "")
        if not ep_password and ep_email.strip():
            ep_password = hashlib.md5(ep_email.strip().lower().encode("utf-8")).hexdigest()

        endpoint = {
            "ep_ip": request.form.get("ep_ip", ""),
            "ep_puerto": request.form.get("ep_puerto", "9000"),
            "ep_email": ep_email,
            "ep_password": ep_password,
            "ep_iapp": request.form.get("ep_iapp", "1001"),
            "ep_idmaquina": request.form.get("ep_idmaquina", ""),
            "ep_keyagente": request.form.get("ep_keyagente", ""),
        }

        mapeo = [
            {"json": j, "excel": e}
            for j, e in zip(campos_json, campos_excel)
            if j.strip() and e.strip()
        ]
        mapeo_json = json.dumps(mapeo, ensure_ascii=False, indent=2)

        mapeo_transporte = [
            {"json": j, "excel": e}
            for j, e in zip(campos_json_transporte, campos_excel_transporte)
            if j.strip() and e.strip()
        ]
        mapeo_transporte_json = json.dumps(mapeo_transporte, ensure_ascii=False, indent=2)

        padre_valido = True
        hijo_valido = True
        transporte_valido = True
        try:
            json.loads(json_padre)
        except json.JSONDecodeError:
            padre_valido = False
            flash("El JSON Padre no es válido. Verifica la sintaxis.", "danger")
        try:
            json.loads(json_hijo)
        except json.JSONDecodeError:
            hijo_valido = False
            flash("El Índice Hijo del JSON no es válido. Verifica la sintaxis.", "danger")
        try:
            json.loads(json_transporte)
        except json.JSONDecodeError:
            transporte_valido = False
            flash("El JSON Transporte no es válido. Verifica la sintaxis.", "danger")

        if padre_valido and hijo_valido and transporte_valido:
            save_config_json(json_padre, json_hijo, mapeo_json, endpoint,
                             contenido_transporte=json_transporte,
                             mapeo_transporte=mapeo_transporte_json)
            flash("Configuración guardada exitosamente", "success")

    cfg = get_config_json()
    mapeo_list = []
    try:
        mapeo_list = json.loads(cfg["mapeo"])
        if not isinstance(mapeo_list, list):
            mapeo_list = []
    except json.JSONDecodeError:
        pass
    mapeo_transporte_list = []
    try:
        mapeo_transporte_list = json.loads(cfg["mapeo_transporte"])
        if not isinstance(mapeo_transporte_list, list):
            mapeo_transporte_list = []
    except json.JSONDecodeError:
        pass
    return render_template(
        "config_json.html",
        json_padre=cfg["json_padre"],
        json_hijo=cfg["json_hijo"],
        mapeo=mapeo_list,
        json_transporte=cfg["json_transporte"],
        mapeo_transporte=mapeo_transporte_list,
        ep_ip=cfg["ep_ip"],
        ep_puerto=cfg["ep_puerto"],
        ep_email=cfg["ep_email"],
        ep_password=cfg["ep_password"],
        ep_iapp=cfg["ep_iapp"],
        ep_idmaquina=cfg["ep_idmaquina"],
        ep_keyagente=cfg["ep_keyagente"],
    )


@app.route("/registros")
@login_required
def registros():
    logs = get_upload_logs()
    return render_template("registros.html", logs=logs)


if __name__ == "__main__":
    init_db()
    print("=" * 50)
    print("  Servidor iniciado!")
    print("  URL: http://localhost:5000")
    print("  Admin: adminceder / AdminCeder345")
    print("=" * 50)
    app.run(debug=False, host="0.0.0.0", port=5000)
