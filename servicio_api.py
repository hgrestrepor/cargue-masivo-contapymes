import json
import requests


def get_base_url(cfg):
    ip = cfg.get("ep_ip", "190.71.116.82")
    puerto = cfg.get("ep_puerto", "9000")
    return f"http://{ip}:{puerto}"


def get_auth(cfg, timeout=30):
    base = get_base_url(cfg)
    url = f'{base}/datasnap/rest/TBasicoGeneral/"GetAuth"/'
    data_json = json.dumps({
        "email": cfg.get("ep_email", ""),
        "password": cfg.get("ep_password", ""),
        "idmaquina": cfg.get("ep_idmaquina", "POSTMAN-TEST"),
    }, ensure_ascii=False)
    payload = {
        "_parameters": [
            data_json,
            "",
            cfg.get("ep_iapp", "1001"),
            "0",
        ]
    }
    resp = requests.post(url, json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def extraer_keyagente(respuesta):
    try:
        datos = respuesta["result"][0]["respuesta"]["datos"]
        return datos.get("keyagente", "")
    except (KeyError, IndexError, TypeError):
        return ""


def extraer_encabezado(respuesta):
    try:
        enc = respuesta["result"][0].get("encabezado", {})
        return enc
    except (KeyError, IndexError, TypeError):
        return {}


def extraer_datos_respuesta(respuesta):
    try:
        datos = respuesta["result"][0]["respuesta"]["datos"]
        return datos
    except (KeyError, IndexError, TypeError):
        return {}


def detalle_respuesta(respuesta):
    datos = extraer_datos_respuesta(respuesta)
    if not datos:
        enc = extraer_encabezado(respuesta)
        return enc.get("mensaje", "") or enc.get("imensaje", "") or "Sin detalle"
    partes = []
    for campo in ("inumoper", "inumsop", "snumsop", "qoprsok", "mtotaloperacion"):
        if dato := datos.get(campo):
            partes.append(f"{campo}={dato}")
    mensaje = extraer_encabezado(respuesta).get("mensaje", "")
    if mensaje:
        partes.append(mensaje)
    return " | ".join(partes) if partes else "Sin detalle"


def enviar_operacion(cfg, keyagente, oprdata, timeout=60):
    base = get_base_url(cfg)
    url = f'{base}/datasnap/rest/TCatOperaciones/"DoExecuteOprAction"/'
    payload = {
        "_parameters": [
            {
                "accion": "CREATE",
                "operaciones": [{"itdoper": "COM5"}],
                "oprdata": oprdata,
            },
            keyagente,
            cfg.get("ep_iapp", "1001"),
            "0",
        ]
    }
    resp = requests.post(url, json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp.json()