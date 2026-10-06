import json
import os
import re
from copy import deepcopy
from datetime import datetime, timedelta

import pandas as pd

JSONS_DIR = os.path.join(os.path.dirname(__file__), "jsons")

FORMATO_FECHA = "%m/%d/%Y"
FECHA_VACIA = "12/30/1899"

DEFAULT_MAPPING = [
    {"json": "icc", "excel": "centro de costos"},
    {"json": "icuenta", "excel": "Cta contable"},
    {"json": "mvalor", "excel": "valor"},
    {"json": "tdetalle", "excel": "observacion"},
]

DEFAULT_JSON_PADRE = {
    "encabezado": {
        "iemp": 1,
        "inumoper": 147,
        "tdetalle": "",
        "itdsop": 116,
        "itdoper": "COM5",
        "inumsop": 6,
        "snumsop": "DSEO6",
        "fsoport": "",
        "iclasifop": 0,
        "iccbase": "",
        "imoneda": "170",
        "iprocess": 0,
        "banulada": "F",
        "blocal": "T",
        "bniif": "T",
        "svaloradic1": "",
        "svaloradic2": "",
        "svaloradic3": "",
        "svaloradic4": "",
        "svaloradic5": "",
        "svaloradic6": "",
        "svaloradic7": "",
        "svaloradic8": "",
        "svaloradic9": "",
        "svaloradic10": "",
        "svaloradic11": "",
        "svaloradic12": "",
        "fecha1adic": FECHA_VACIA,
        "fecha2adic": FECHA_VACIA,
        "fecha3adic": FECHA_VACIA,
        "datosaddin": "",
        "fcreacion": "",
        "fultima": "",
        "fprocesam": FECHA_VACIA,
        "iusuario": "ADMIN",
        "iusuarioult": "ADMIN",
        "isucursal": "",
        "inumoperultimp": "",
        "inumoperpadre": 0,
        "bespadre": False,
        "bconfirmaenviofe": False,
        "accionesalgrabar": "",
        "mtotaloperacion": 0.0,
    },
    "datosprincipales": {
        "init": "",
        "ireferencia": "",
        "bshowsupportinfo": "F",
        "qregconcdescuento": 0,
    },
    "ingresosegresos": [],
    "liquidimpuestos": [],
    "formapago": {
        "mtotalreg": "0.00000000",
        "mtotalpago": "0.00000000",
        "qpagoscaja": 0,
        "qpagosbanco": 0,
        "qpagoscxp": 1,
        "qpagosamortcxc": 0,
        "fpagocaja": [],
        "fpagobanco": [],
        "fpagocxp": [
            {
                "id": 1,
                "init": "",
                "icuenta": "23359505",
                "qdiascxp": 30,
                "qdiasvencim": 0,
                "icc": "",
                "nconcepto": "",
                "ireferencia": "",
                "binteresvencido": "F",
                "itdperiodicidad": 0,
                "pinteres": 0.0,
                "pinteresmora": 0.0,
                "bmoramaxima": "F",
                "itdvalorcuota": 0,
                "qcuotas": 0,
                "valorcuotas": 0.0,
                "qperiodicidad": 0,
                "idia": 0,
                "bcuotasespeciales": "F",
                "mcuotaesp1": 0.0,
                "mcuotaesp2": 0.0,
                "mescuotaesp1": 0,
                "mescuotaesp2": 0,
                "bescalonadamente": "F",
                "bmanual": "F",
                "fprimeracuota": FECHA_VACIA,
                "itdopcion": 0,
                "icuotaopc": 0,
                "mvalor": 0.0,
                "mvrotramoneda": 0.0,
                "bconceptochanged": "F",
                "beditvrotramoneda": "F",
            }
        ],
        "fpagoamortcxc": [],
    },
}

DEFAULT_JSON_HIJO = [
    {
        "icc": "112",
        "icuenta": "6165950116",
        "iactivo": "",
        "mvalor": 1848000.0,
        "tdetalle": "CONTABILIZACION CUOTA DE SOSTENIMIENTO Y BONIFICACION MS MES DE JULIO",
        "itdsop": 116,
        "inumsop": "<AUTO>",
        "fsoport": "08/18/2026",
        "init": "",
        "mvrbase": 0.0,
        "binteres": "F",
        "binteresmora": "F",
        "bperdonarmora": "F",
        "binteresxcobrar": "F",
        "valor1": 0.0,
        "valor2": 0.0,
        "clase1": "",
        "clase2": "",
    },
    {
        "icc": "112",
        "icuenta": "6165950123",
        "iactivo": "",
        "mvalor": 1532041.0,
        "tdetalle": "CONTABILIZACION CUOTA DE SOSTENIMIENTO Y BONIFICACION MS MES DE JULIO",
        "itdsop": 116,
        "inumsop": "<AUTO>",
        "fsoport": "08/18/2026",
        "init": "",
        "mvrbase": 0.0,
        "binteres": "F",
        "binteresmora": "F",
        "bperdonarmora": "F",
        "binteresxcobrar": "F",
        "valor1": 0.0,
        "valor2": 0.0,
        "clase1": "",
        "clase2": "",
    },
]

DEFAULT_JSON_TRANSPORTE = {
    "encabezado": {
        "iemp": 1,
        "inumoper": 3411,
        "tdetalle": "",
        "itdsop": 116,
        "itdoper": "COM5",
        "inumsop": 0,
        "snumsop": "<AUTO>",
        "fsoport": "",
        "iclasifop": 0,
        "iccbase": "",
        "imoneda": "170",
        "iprocess": 0,
        "banulada": "F",
        "blocal": "T",
        "bniif": "T",
        "svaloradic1": "",
        "svaloradic2": "",
        "svaloradic3": "",
        "svaloradic4": "",
        "svaloradic5": "",
        "svaloradic6": "",
        "svaloradic7": "",
        "svaloradic8": "",
        "svaloradic9": "",
        "svaloradic10": "",
        "svaloradic11": "",
        "svaloradic12": "",
        "fecha1adic": FECHA_VACIA,
        "fecha2adic": FECHA_VACIA,
        "fecha3adic": FECHA_VACIA,
        "datosaddin": "",
        "fcreacion": "",
        "fultima": "",
        "fprocesam": FECHA_VACIA,
        "iusuario": "",
        "iusuarioult": "",
        "isucursal": "",
        "inumoperultimp": "",
        "inumoperpadre": 0,
        "bespadre": False,
        "bconfirmaenviofe": False,
        "accionesalgrabar": "",
        "mtotaloperacion": 0.0,
    },
    "datosprincipales": {
        "init": "",
        "ireferencia": "",
        "bshowsupportinfo": "F",
        "qregconcdescuento": 0,
    },
    "ingresosegresos": [],
    "liquidimpuestos": [],
    "formapago": {
        "mtotalreg": "0.00000000",
        "mtotalpago": "0.00000000",
        "qpagoscaja": 0,
        "qpagosbanco": 0,
        "qpagoscxp": 0,
        "qpagosamortcxc": 0,
        "fpagocaja": [],
        "fpagobanco": [],
        "fpagocxp": [{
            "id": 1,
            "init": "",
            "icuenta": "",
            "qdiascxp": 30,
            "qdiasvencim": 0,
            "icc": "",
            "nconcepto": "",
            "ireferencia": "",
            "binteresvencido": "F",
            "itdperiodicidad": 0,
            "pinteres": 0.0,
            "pinteresmora": 0.0,
            "bmoramaxima": "F",
            "itdvalorcuota": 0,
            "qcuotas": 0,
            "valorcuotas": 0.0,
            "qperiodicidad": 0,
            "idia": 0,
            "bcuotasespeciales": "F",
            "mcuotaesp1": 0.0,
            "mcuotaesp2": 0.0,
            "mescuotaesp1": 0,
            "mescuotaesp2": 0,
            "bescalonadamente": "F",
            "bmanual": "F",
            "fprimeracuota": FECHA_VACIA,
            "itdopcion": 0,
            "icuotaopc": 0,
            "mvalor": 0.0,
            "mvrotramoneda": 0.0,
            "bconceptochanged": "F",
            "beditvrotramoneda": "F",
        }],
        "fpagoamortcxc": [],
    },
}

DEFAULT_JSON_TRANSPORTE_HIJO = {
    "icc": "",
    "icuenta": "",
    "iactivo": "",
    "mvalor": 0.0,
    "tdetalle": "",
    "itdsop": 116,
    "inumsop": "<AUTO>",
    "fsoport": "",
    "init": "",
    "mvrbase": 0.0,
    "binteres": "F",
    "binteresmora": "F",
    "bperdonarmora": "F",
    "binteresxcobrar": "F",
    "valor1": 0.0,
    "valor2": 0.0,
    "clase1": "",
    "clase2": "",
}

DEFAULT_MAPPING_TRANSPORTE = [
    {"json": "encabezado.tdetalle", "excel": "concepto general"},
    {"json": "datosprincipales.init", "excel": "numero de documento del acudiente"},
    {"json": "ingresosegresos.icc", "excel": "centro de costo"},
    {"json": "ingresosegresos.icuenta", "excel": "cuenta contable"},
    {"json": "ingresosegresos.mvalor", "excel": "valor"},
    {"json": "ingresosegresos.tdetalle", "excel": "concepto del detalle"},
    {"json": "formapago.fpagocxp.init", "excel": "documento profesional"},
    {"json": "formapago.fpagocxp.icuenta", "excel": "cuenta profesional"},
    {"json": "formapago.fpagocxp.nconcepto", "excel": "concepto general"},
    {"json": "formapago.fpagocxp.mvalor", "excel": "valor"},
]

DEFAULT_COLUMNA_RECORRIDO_TRANSPORTE = "NOMBRE DEL ACUDIENTE"
DEFAULT_COLUMNA_PROFESIONAL_TRANSPORTE = "NOMBRE PROFESIONAL"

TERCEROS_PATTERNS = {
    "tercero",
    "clientid",
    "client",
    "cliente",
    "codigocliente",
    "idtercero",
    "codtercero",
    "nit",
}
TERCEROS_CONTAINS = ["tercero", "client"]

CCOSTOS_PATTERNS = {
    "centrodecostos",
    "centrocosto",
    "centrocostos",
    "ccostos",
    "centrodeconsto",
}
CCOSTOS_CONTAINS = ["centro", "costos"]

VALOR_PATTERNS = {"valor", "mvalor", "importe", "monto", "value", "vlr", "total"}
VALOR_CONTAINS = ["valor"]

OBS_PATTERNS = {
    "observacion",
    "observación",
    "detalle",
    "descripcion",
    "glosa",
    "concepto",
    "tdetalle",
}
OBS_CONTAINS = ["observ", "detalle", "glosa"]

NATURALEZA_PATTERNS = {"naturaleza", "tipomovimiento", "movimiento", "tipo", "dc", "db", "cr", "debito", "credito"}
NATURALEZA_CONTAINS = ["natur", "movimiento", "debito", "credito", "tipomov"]

CEDULA_PATTERNS = {
    "cedula",
    "cédula",
    "numcedula",
    "numerocedula",
    "idcedula",
    "cedulaciudadana",
}
CEDULA_CONTAINS = ["cedula", "cédula"]

DEBITO_VALUES = {"D", "DB", "DEBITO", "DEBITOS", "DÉBITO", "DÉBITOS"}
CREDITO_VALUES = {"C", "CR", "CREDITO", "CREDITOS", "CRÉDITO", "CRÉDITOS"}


def _normalize(col):
    return str(col).strip().lower().replace("_", "").replace("-", "").replace(" ", "")


def _find_column(df, patterns, contains=None):
    for col in df.columns:
        if _normalize(col) in patterns:
            return col
    if contains:
        for col in df.columns:
            normalized = _normalize(col)
            for token in contains:
                if token in normalized:
                    return col
    return None


def _es_columna_naturaleza(col):
    normalizada = _normalize(col)
    if normalizada in NATURALEZA_PATTERNS:
        return True
    return any(token in normalizada for token in NATURALEZA_CONTAINS)


def _columna_tiene_marcas(serie):
    """True si la columna tiene al menos una celda marcada como D o C."""
    for valor in serie:
        if _to_str(valor).upper() in DEBITO_VALUES or _to_str(valor).upper() in CREDITO_VALUES:
            return True
    return False


def _columna_es_naturaleza(serie, proporcion_minima=0.6):
    """True si la mayoría de los valores no vacíos de la columna son marcas D/C.

    Se usa para las columnas que se asumen por posición (C, D y E) y para las
    vecinas de un encabezado combinado, así una letra suelta en otra columna
    (ej. una observación que empiece por 'C') no se toma como naturaleza.
    """
    valores = [v for v in (_to_str(valor).upper() for valor in serie) if v]
    if not valores:
        return False
    marcas = sum(1 for valor in valores if valor in DEBITO_VALUES or valor in CREDITO_VALUES)
    if not marcas:
        return False
    return (marcas / len(valores)) >= proporcion_minima


def _columnas_naturaleza(df):
    """Columnas del Excel que definen la naturaleza (D/C) de cada fila.

    1. Usa las columnas con nombre de naturaleza. Si el encabezado viene
       combinado (una sola celda 'Naturaleza' sobre varias columnas), las
       columnas vecinas quedan como 'Unnamed' y se agregan solo si traen
       mayoritariamente marcas D/C.
    2. Si no hay ninguna con nombre, toma las columnas C, D y E del Excel
       (solo las que traigan marcas D/C).
    3. Si ninguna trae marcas D/C, devuelve lista vacía (todas las filas se
       toman como débito, como cuando no existía la columna naturaleza).
    """
    columnas = list(df.columns)
    encontradas = [col for col in columnas if _es_columna_naturaleza(col)]

    for col in list(encontradas):
        inicio = columnas.index(col)
        for posicion in range(inicio + 1, min(inicio + 3, len(columnas))):
            vecina = columnas[posicion]
            if vecina in encontradas:
                continue
            if _normalize(vecina).startswith("unnamed") and _columna_es_naturaleza(df[vecina]):
                encontradas.append(vecina)

    con_marcas = [col for col in encontradas if _columna_tiene_marcas(df[col])]
    if con_marcas:
        return con_marcas

    if len(columnas) >= 5:
        posicionales = [col for col in columnas[2:5] if _columna_es_naturaleza(df[col])]
        if posicionales:
            return posicionales

    return []


def _naturaleza_fila(fila, columnas):
    """Primera marca D/C encontrada en las columnas de naturaleza de la fila."""
    for col in columnas:
        valor = _to_str(fila[col]).upper()
        if valor in DEBITO_VALUES:
            return "D"
        if valor in CREDITO_VALUES:
            return "C"
    return ""


def _es_marca(valor):
    return _to_str(valor).upper() in DEBITO_VALUES or _to_str(valor).upper() in CREDITO_VALUES


def _es_rotulo_identificador(valor):
    """True si la celda parece un rótulo de columna (Cédula, tercero, etc.)."""
    texto = _to_str(valor)
    if not texto or len(texto) > 30 or any(digito.isdigit() for digito in texto):
        return False
    normalizada = _normalize(texto)
    if normalizada in CEDULA_PATTERNS or normalizada in TERCEROS_PATTERNS:
        return True
    return any(token in normalizada for token in CEDULA_CONTAINS + TERCEROS_CONTAINS)


def _fila_es_encabezado(fila):
    no_vacias = [celda for celda in fila if _to_str(celda)]
    if len(no_vacias) < 2:
        return False
    return any(_es_rotulo_identificador(celda) for celda in fila)


def _nombres_unicos(nombres):
    usados = {}
    unicos = []
    for nombre in nombres:
        base = nombre or "columna"
        if base in usados:
            usados[base] += 1
            unicos.append(f"{base}.{usados[base]}")
        else:
            usados[base] = 1
            unicos.append(base)
    return unicos


def _es_cabecera_cuenta(cabecera):
    """True si el rótulo de una columna marcada puede ser una cuenta contable."""
    normalizada = _normalize(cabecera)
    if not normalizada or _es_columna_naturaleza(cabecera):
        return False
    if normalizada in CEDULA_PATTERNS or normalizada in TERCEROS_PATTERNS:
        return False
    if any(token in normalizada for token in CEDULA_CONTAINS + TERCEROS_CONTAINS):
        return False
    if normalizada in CCOSTOS_PATTERNS or any(token in normalizada for token in CCOSTOS_CONTAINS):
        return False
    if normalizada in OBS_PATTERNS or any(token in normalizada for token in OBS_CONTAINS):
        return False
    return True


def _fila_marcas_columnas(matriz, posicion_encabezado):
    """Fila con las marcas d/c de cada columna (encabezado combinado).

    Debe estar justo encima o justo debajo de la fila del encabezado y traer
    al menos dos marcas en columnas que parezcan cuentas."""
    for posicion in (posicion_encabezado - 1, posicion_encabezado + 1):
        if posicion < 0 or posicion >= len(matriz):
            continue
        fila = matriz[posicion]
        if _fila_es_encabezado(fila):
            continue
        celdas = [(i, _to_str(valor).upper()) for i, valor in enumerate(fila) if _es_marca(valor)]
        if len(celdas) < 2:
            continue
        encabezados = [_to_str(valor) for valor in matriz[posicion_encabezado]]
        if all(i < len(encabezados) and _es_cabecera_cuenta(encabezados[i]) for i, _ in celdas):
            return posicion, celdas
    return None


def _preparar_dataframe(df, max_filas=20):
    """Detecta el encabezado real y el formato ancho (una columna por cuenta).

    Formato ancho: la fila del encabezado trae las cuentas (ej. 6165950116,
    6165950123, 23359505) y justo encima o debajo vienen las marcas d/c de
    cada columna. Esas columnas se convierten a filas con
    cedula + naturaleza + Cta contable + valor + centro de costos + observacion,
    para que todo el resto del proceso funcione igual.

    Devuelve (dataframe, cuenta_credito)."""
    matriz = [list(df.columns)] + [list(fila) for fila in df.head(max_filas).values]

    posicion_encabezado = None
    for i, fila in enumerate(matriz):
        if _fila_es_encabezado(fila):
            posicion_encabezado = i
            break
    if posicion_encabezado is None:
        return df, None

    marcas = _fila_marcas_columnas(matriz, posicion_encabezado)

    if marcas is None:
        if posicion_encabezado == 0:
            return df, None
        nuevo = df.iloc[posicion_encabezado:].copy()
        nuevo.columns = _nombres_unicos([_to_str(valor) for valor in matriz[posicion_encabezado]])
        return nuevo, None

    posicion_marcas, celdas = marcas
    columnas = _nombres_unicos([_to_str(valor) for valor in matriz[posicion_encabezado]])
    datos = df.iloc[posicion_encabezado:].copy()
    indice_marcas = posicion_marcas - 1 - posicion_encabezado
    if indice_marcas >= 0:
        datos = datos.iloc[[i for i in range(len(datos)) if i != indice_marcas]]
    datos.columns = columnas

    col_cedula = _find_column(datos, CEDULA_PATTERNS, CEDULA_CONTAINS)
    if col_cedula is None:
        col_cedula = _find_column(datos, TERCEROS_PATTERNS, TERCEROS_CONTAINS)
    if col_cedula is None:
        return df, None

    col_centro = _find_column(datos, CCOSTOS_PATTERNS, CCOSTOS_CONTAINS)
    col_obs = _find_column(datos, OBS_PATTERNS, OBS_CONTAINS)

    columnas_valor = [(i, marca) for i, marca in celdas if _es_cabecera_cuenta(columnas[i])]
    if not columnas_valor:
        return df, None

    cuenta_credito = ""
    for i, marca in columnas_valor:
        if marca == "C" and not cuenta_credito:
            cuenta_credito = _to_str(matriz[posicion_encabezado][i])

    filas = []
    for _, fila in datos.iterrows():
        cedula = _to_str(fila[col_cedula])
        if not cedula:
            continue
        centro = _to_str(fila[col_centro]) if col_centro else ""
        observacion = _to_str(fila[col_obs]) if col_obs else ""
        for i, marca in columnas_valor:
            valor = fila[columnas[i]]
            if not _to_str(valor):
                continue
            filas.append({
                "cedula": cedula,
                "Naturaleza": marca,
                "Cta contable": _to_str(matriz[posicion_encabezado][i]),
                "valor": valor,
                "centro de costos": centro,
                "observacion": observacion,
            })

    if not filas:
        return df, None
    return pd.DataFrame(filas), cuenta_credito


def _to_str(value):
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def _to_float(value):
    if value is None:
        return 0.0
    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        pass
    s = str(value).strip().replace("$", "").replace(" ", "")
    if not s:
        return 0.0
    if "," in s:
        si_no_miles = s.replace(".", "")
        if si_no_miles.replace(",", "").isdigit():
            s = si_no_miles.replace(",", ".")
    else:
        s = re.sub(r"\.(?=\d{3}(?:\.|$))", "", s)
    try:
        return float(s)
    except ValueError:
        return 0.0


def _is_numeric_field(field_name):
    name = _normalize(field_name)
    return name.startswith("m") or "valor" in name or "monto" in name or "importe" in name


def _sanitize_filename(value):
    name = _to_str(value)
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", name)
    return name or "sin_tercero"


def _fecha_contable():
    """30 del mes anterior a la fecha actual, formato mm/dd/aaaa."""
    ultimo_dia_mes_anterior = datetime.now().replace(day=1) - timedelta(days=1)
    return datetime(ultimo_dia_mes_anterior.year, ultimo_dia_mes_anterior.month, 30).strftime(FORMATO_FECHA)


def _parse_template(template, default):
    if isinstance(template, dict):
        return deepcopy(template)
    if isinstance(template, str):
        try:
            data = json.loads(template)
            if isinstance(data, type(default)):
                return data
            if isinstance(data, list) and data:
                return data
        except json.JSONDecodeError:
            pass
    return deepcopy(default)


STOPWORDS = {"de", "del", "la", "el", "los", "las", "un", "una", "y"}


def _tokenize(name):
    text = str(name).lower().replace("_", " ").replace("-", " ").replace(".", " ")
    tokens = set()
    for part in re.split(r"\s+", text.strip()):
        if part and part not in STOPWORDS:
            tokens.add(part)
    return tokens


def _columns_match(col, target):
    t = _tokenize(target)
    c = _tokenize(col)
    if not c or not t:
        return _normalize(col) == _normalize(target)
    inter = set()
    for a in t:
        for b in c:
            if a == b or (len(a) >= 3 and len(b) >= 3 and (a.startswith(b) or b.startswith(a))):
                inter.add(a)
                inter.add(b)
    if t <= c or c <= t:
        return True
    small = min(len(t), len(c))
    return small > 0 and len(inter) / small >= 0.6


def _column_exists(df, excel_name):
    for col in df.columns:
        if _columns_match(col, excel_name):
            return col
    return None


def _find_named_column(df, nombre):
    if not nombre:
        return None
    target = str(nombre).strip()
    return _column_exists(df, target)


def _bloques_por_tercero(serie):
    """Divide las filas en bloques consecutivos según la columna de terceros.

    Una celda vacía significa que la fila pertenece al mismo tercero de la
    fila anterior (el valor se arrastra hacia abajo). Solo se abre un bloque
    nuevo cuando aparece un tercero distinto al anterior."""
    bloques = []
    actual = ""
    posiciones = []
    for posicion, valor in enumerate(serie.tolist()):
        tercero = _to_str(valor)
        if tercero:
            if actual and tercero != actual:
                bloques.append((actual, posiciones))
                posiciones = []
            actual = tercero
        if not actual:
            continue
        posiciones.append(posicion)
    if posiciones:
        bloques.append((actual, posiciones))
    return bloques


def _parse_mapping(mapping_raw, default=None):
    if default is None:
        default = DEFAULT_MAPPING
    if isinstance(mapping_raw, list):
        items = mapping_raw
    elif isinstance(mapping_raw, str):
        try:
            parsed = json.loads(mapping_raw)
            items = parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            items = []
    else:
        items = []
    mapping = []
    for item in items:
        if isinstance(item, dict) and item.get("json") and item.get("excel"):
            mapping.append({
                "json": str(item["json"]).strip(),
                "excel": str(item["excel"]).strip(),
            })
    if not mapping:
        return deepcopy(default)
    return mapping


def generar_jsons(df, archivo_origen, template_padre=None, template_hijo=None,
                  mapping=None, carpeta=None, usuario=None):
    carpeta = carpeta or JSONS_DIR
    os.makedirs(carpeta, exist_ok=True)

    padre = _parse_template(template_padre, DEFAULT_JSON_PADRE)
    hijo = _parse_template(template_hijo, DEFAULT_JSON_HIJO)
    if isinstance(hijo, list):
        base_hijo = hijo[0] if hijo else deepcopy(DEFAULT_JSON_HIJO[0])
    else:
        base_hijo = hijo

    mapping = _parse_mapping(mapping)

    campos_mapeados = {item["json"] for item in mapping}
    for item in DEFAULT_MAPPING:
        if item["json"] not in campos_mapeados:
            mapping.append(dict(item))
            campos_mapeados.add(item["json"])

    origen_base = os.path.splitext(os.path.basename(archivo_origen))[0]

    df, cuenta_credito = _preparar_dataframe(df)

    tercero_col = _find_column(df, CEDULA_PATTERNS, CEDULA_CONTAINS)
    if tercero_col is None:
        tercero_col = _find_column(df, TERCEROS_PATTERNS, TERCEROS_CONTAINS)
    if tercero_col is None:
        return 0, 0, "No se encontró la columna de Cédula/Tercero en el Excel.", []

    col_mapping = []
    for item in mapping:
        col = _column_exists(df, item["excel"])
        col_mapping.append({"json": item["json"], "excel": item["excel"], "col": col})

    fecha = _fecha_contable()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    columnas_naturaleza = _columnas_naturaleza(df)

    carpeta_archivo = os.path.join(carpeta, f"{origen_base}_{timestamp}")
    os.makedirs(carpeta_archivo, exist_ok=True)

    total_json = 0
    total_registros = 0
    archivos_generados = []
    nombres_usados = set()

    bloques = _bloques_por_tercero(df[tercero_col])
    if not bloques:
        return 0, 0, "La columna de Cédula no tiene ningún valor.", []

    for tercero, posiciones in bloques:
        grupo = df.iloc[posiciones]
        filas_debito = grupo
        filas_credito = None
        if columnas_naturaleza:
            posiciones_debito = []
            posiciones_credito = []
            for posicion_local, (_, fila) in enumerate(grupo.iterrows()):
                naturaleza = _naturaleza_fila(fila, columnas_naturaleza)
                if naturaleza == "D":
                    posiciones_debito.append(posicion_local)
                elif naturaleza == "C":
                    posiciones_credito.append(posicion_local)
            filas_debito = grupo.iloc[posiciones_debito]
            filas_credito = grupo.iloc[posiciones_credito]

        ingresos = []
        for _, row in filas_debito.iterrows():
            ingreso = deepcopy(base_hijo)
            for item in col_mapping:
                col = item["col"]
                if col is None:
                    continue
                valor = row[col]
                if _is_numeric_field(item["json"]):
                    ingreso[item["json"]] = _to_float(valor)
                else:
                    ingreso[item["json"]] = _to_str(valor)
            ingreso["fsoport"] = fecha
            ingresos.append(ingreso)

        total = 0.0
        col_obs = next((item["col"] for item in col_mapping
                        if item["json"] == "tdetalle" and item["col"] is not None), None)
        col_icc = next((item["col"] for item in col_mapping
                        if item["json"] == "icc" and item["col"] is not None), None)

        obs_credito = ""
        icc_credito = ""
        if filas_credito is not None and not filas_credito.empty:
            fila_credito = filas_credito.iloc[0]
            if col_obs is not None:
                obs_credito = _to_str(fila_credito[col_obs])
            if col_icc is not None:
                icc_credito = _to_str(fila_credito[col_icc])
            for item in col_mapping:
                if item["json"] == "mvalor" and item["col"] is not None:
                    total = _to_float(fila_credito[item["col"]])
                    break
        if not icc_credito and col_icc is not None and not grupo.empty:
            icc_credito = _to_str(grupo.iloc[0][col_icc])
        if total == 0.0:
            total = sum(float(i.get("mvalor") or 0.0) for i in ingresos)

        total_registros += len(ingresos)

        documento = deepcopy(padre)
        documento["ingresosegresos"] = ingresos

        encabezado = documento.get("encabezado", {})
        encabezado["fsoport"] = fecha
        encabezado["fcreacion"] = fecha
        encabezado["fultima"] = fecha
        encabezado["mtotaloperacion"] = round(total, 2)
        if usuario:
            encabezado["iusuario"] = usuario
            encabezado["iusuarioult"] = usuario
        if obs_credito:
            encabezado["tdetalle"] = obs_credito

        datos_principales = documento.get("datosprincipales", {})
        datos_principales["init"] = _to_str(tercero)

        formapago = documento.get("formapago", {})
        formapago["mtotalreg"] = "{:.8f}".format(total)
        formapago["mtotalpago"] = "{:.8f}".format(total)
        fpagocxp = formapago.get("fpagocxp", [])
        for item in fpagocxp:
            item["init"] = _to_str(tercero)
            item["mvalor"] = round(total, 2)
            if icc_credito:
                item["icc"] = icc_credito
            if obs_credito:
                item["nconcepto"] = obs_credito
            if cuenta_credito and re.fullmatch(r"[0-9]+", cuenta_credito):
                item["icuenta"] = cuenta_credito

        base_nombre = f"{origen_base}_{_sanitize_filename(tercero)}_{timestamp}"
        nombre = f"{base_nombre}.json"
        sufijo = 2
        while nombre in nombres_usados:
            nombre = f"{base_nombre}_{sufijo}.json"
            sufijo += 1
        nombres_usados.add(nombre)
        ruta = os.path.join(carpeta_archivo, nombre)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(documento, f, ensure_ascii=False, indent=2)
        archivos_generados.append({"ruta": ruta, "tercero": _to_str(tercero)})
        total_json += 1

    return total_json, total_registros, None, archivos_generados


def _parse_template_transporte(template_transporte, template_hijo):
    """Devuelve (plantilla_padre, plantilla_hijo) para transportes."""
    transporte = _parse_template(template_transporte, DEFAULT_JSON_TRANSPORTE)
    if not isinstance(transporte, dict):
        transporte = deepcopy(DEFAULT_JSON_TRANSPORTE)

    hijo = _parse_template(template_hijo, DEFAULT_JSON_TRANSPORTE_HIJO)
    if isinstance(hijo, list):
        hijo = hijo[0] if hijo else deepcopy(DEFAULT_JSON_TRANSPORTE_HIJO)
    if not isinstance(hijo, dict):
        hijo = deepcopy(DEFAULT_JSON_TRANSPORTE_HIJO)

    ingresos_plantilla = transporte.get("ingresosegresos", [])
    if isinstance(ingresos_plantilla, list) and ingresos_plantilla and isinstance(ingresos_plantilla[0], dict):
        hijo = deepcopy(ingresos_plantilla[0])

    return transporte, hijo


def _aplicar_mapeo_transporte(documento, ingreso, path, valor):
    """Asigna valor según la ruta JSON del mapeo de transportes.

    Soporta rutas que atraviesan listas (ej. formapago.fpagocxp.init):
    aplica el valor a cada dict dentro de la lista."""
    if not path:
        return
    partes = [p for p in str(path).split(".") if p]
    if not partes:
        return
    if partes[0] == "ingresosegresos":
        if len(partes) > 1:
            key = partes[1]
            ingreso[key] = _to_float(valor) if _is_numeric_field(key) else _to_str(valor)
        return

    def _resolver(cursor, restantes):
        parte = restantes[0]
        resta = restantes[1:]
        if isinstance(cursor, dict) and isinstance(cursor.get(parte), list):
            for elemento in cursor[parte]:
                if isinstance(elemento, dict) and resta:
                    _resolver(elemento, resta)
            return
        if len(restantes) == 1:
            clave = restantes[0]
            cursor[clave] = _to_float(valor) if _is_numeric_field(clave) else _to_str(valor)
            return
        siguiente = cursor.get(parte) if isinstance(cursor, dict) else None
        if not isinstance(siguiente, dict):
            siguiente = {}
            if isinstance(cursor, dict):
                cursor[parte] = siguiente
        _resolver(siguiente, resta)

    _resolver(documento, partes)


def generar_jsons_transporte(df, archivo_origen, template_transporte=None,
                             template_hijo=None, mapping=None,
                             columna_recorrido=None, columna_profesional=None,
                             carpeta=None, usuario=None):
    """Genera JSONs de transporte agrupando el Excel por la columna de recorrido
    (por defecto NOMBRE DEL ACUDIENTE). Los datos del profesional se comparten
    (se replican/heredan) entre todos los acudientes de ese profesional."""
    carpeta = carpeta or JSONS_DIR
    os.makedirs(carpeta, exist_ok=True)

    transporte, hijo = _parse_template_transporte(template_transporte, template_hijo)
    mapping = _parse_mapping(mapping, DEFAULT_MAPPING_TRANSPORTE)

    campos_mapeados = {item["json"] for item in mapping}
    for item in DEFAULT_MAPPING_TRANSPORTE:
        if item["json"] not in campos_mapeados:
            mapping.append(dict(item))
            campos_mapeados.add(item["json"])

    col_recorrido = _find_named_column(df, columna_recorrido or DEFAULT_COLUMNA_RECORRIDO_TRANSPORTE)
    if col_recorrido is None:
        return 0, 0, (
            f"No se encontró la columna de recorrido '{columna_recorrido or DEFAULT_COLUMNA_RECORRIDO_TRANSPORTE}' "
            "en el Excel. Revísala en Configuraciones > Transportes."
        ), []

    # Columnas de nivel profesional que se comparten/heredan entre acudientes.
    columnas_compartidas = []
    if columna_profesional:
        col = _find_named_column(df, columna_profesional)
        if col is not None:
            columnas_compartidas.append(col)
    for patron in ("documento profesional", "cuenta profesional", "concepto general"):
        col = _find_named_column(df, patron)
        if col is not None and col not in columnas_compartidas:
            columnas_compartidas.append(col)
    df = df.copy()
    for col in columnas_compartidas:
        df[col] = df[col].ffill()

    col_mapping = []
    for item in mapping:
        col = _find_named_column(df, item["excel"])
        col_mapping.append({"json": item["json"], "excel": item["excel"], "col": col})

    fecha = _fecha_contable()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    origen_base = os.path.splitext(os.path.basename(archivo_origen))[0]

    carpeta_archivo = os.path.join(carpeta, f"{origen_base}_transporte_{timestamp}")
    os.makedirs(carpeta_archivo, exist_ok=True)

    total_json = 0
    total_registros = 0
    archivos_generados = []

    for acudiente, grupo in df.groupby(col_recorrido, dropna=False):
        registro = _to_str(acudiente)
        if not registro:
            continue

        documento = deepcopy(transporte)
        ingresos = []
        for _, row in grupo.iterrows():
            ingreso = deepcopy(hijo)
            ingreso["fsoport"] = fecha
            for item in col_mapping:
                col = item["col"]
                if col is None:
                    continue
                valor = row[col]
                path = item["json"]
                if path in ("ingresosegresos",) or "." in path and path.split(".")[0] == "ingresosegresos":
                    key = path.split(".")[-1]
                    if _is_numeric_field(key):
                        ingreso[key] = _to_float(valor)
                    else:
                        ingreso[key] = _to_str(valor)
                elif "." not in path:
                    if _is_numeric_field(path):
                        ingreso[path] = _to_float(valor)
                    else:
                        ingreso[path] = _to_str(valor)
                else:
                    _aplicar_mapeo_transporte(documento, ingreso, path, valor)
            ingresos.append(ingreso)

        total = sum(float(i.get("mvalor") or 0.0) for i in ingresos)
        total_registros += len(ingresos)

        documento["ingresosegresos"] = ingresos

        encabezado = documento.get("encabezado", {})
        encabezado["fsoport"] = fecha
        encabezado["fcreacion"] = fecha
        encabezado["fultima"] = fecha
        encabezado["mtotaloperacion"] = round(total, 2)
        if usuario:
            encabezado["iusuario"] = usuario
            encabezado["iusuarioult"] = usuario

        datos_principales = documento.get("datosprincipales", {})
        if not datos_principales.get("init"):
            datos_principales["init"] = registro

        formapago = documento.get("formapago", {})
        formapago["mtotalreg"] = "{:.8f}".format(total)
        formapago["mtotalpago"] = "{:.8f}".format(total)

        nombre = f"{origen_base}_transporte_{_sanitize_filename(registro)}_{timestamp}.json"
        ruta = os.path.join(carpeta_archivo, nombre)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(documento, f, ensure_ascii=False, indent=2)
        archivos_generados.append({"ruta": ruta, "tercero": _to_str(registro)})
        total_json += 1

    return total_json, total_registros, None, archivos_generados