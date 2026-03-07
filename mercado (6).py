"""
MercadoFrutas — pip install flask matplotlib pillow — python mercado.py
Administrador: http://localhost:5000/admin
Contraseña de administrador: Admin2026$ Contraseña de maestra: Frutas$Master2006
"""
desde flask importar Flask, solicitud, redirigir, url_for, sesión, Respuesta
importar sqlite3, base64, io, json, sistema operativo
desde datetime importar datetime
importar matplotlib
matplotlib.use('Agg')
importar matplotlib.pyplot como plt

aplicación = Flask(__nombre__)
app.secret_key = "mercado_frutas_2026!"
CONTRASEÑA DE ADMINISTRACIÓN = "Admin2026$"
CONTRASEÑA_MAESTRA = "Frutas$Master2006"
DB = "mercado.db"

# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
# BASE DE DATOS
# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
definición obtener_db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    devolver c

definición init_db():
    db = obtener_db()
    db.execute("""
        CREAR TABLA SI NO EXISTE productos(
            id ENTERO CLAVE PRIMARIA AUTOINCREMENTO,
            nombre TEXTO NO NULO,
            precio REAL NO NULO,
            descripción TEXTO PREDETERMINADO '',
            unidad TEXTO PREDETERMINADO 'unidad',
            categoria TEXTO POR DEFECTO 'Frutas',
            imagen TEXTO,
            activo ENTERO PREDETERMINADO 1
        )""")
    db.execute("""
        CREAR TABLA SI NO EXISTE pedidos(
            id ENTERO CLAVE PRIMARIA AUTOINCREMENTO,
            nombre_cliente TEXTO NO NULO,
            celular TEXTO NO NULO,
            dirección TEXTO NO NULO,
            barrio TEXTO PREDETERMINADO '',
            referencia TEXTO PREDETERMINADO '',
            notas TEXTO PREDETERMINADO '',
            elementos TEXTO NO NULO,
            subtotal REAL NO NULO,
            envio REAL PREDETERMINADO 0,
            total REAL NO NULO,
            estado TEXTO POR DEFECTO 'Pendiente',
            confirmacion TEXTO POR DEFECTO 'pendiente',
            hora_entrega TEXTO PREDETERMINADO '',
            motivo TEXTO PREDETERMINADO '',
            fecha TEXTO NO NULO,
            ficha TEXTO PREDETERMINADO ''
        )""")
    db.execute("""
        CREAR TABLA SI NO EXISTE configuracion(
            clave TEXTO CLAVE PRIMARIA,
            valor TEXTO
        )""")
    db.execute("INSERT OR IGNORE INTO configuracion VALUES('nombre','Mercado Frutas Frescas')")
    db.execute("INSERTAR O IGNORAR EN los valores de configuración ('logo','')")
    db.execute("INSERTAR O IGNORAR EN LA CONFIGURACIÓN VALUES('activo','1')")
    db.execute("""CREAR TABLA SI NO EXISTE compras(
        id ENTERO CLAVE PRIMARIA AUTOINCREMENTO,
        producto TEXTO NO NULO,
        cantidad TEXTO NO NULO,
        costo REAL NO NULO,
        fecha TEXTO NO NULO,
        notas TEXTO PREDETERMINADO ''
    )""")
    # Sin productos demo - el dueÃ±o agrega los suyos desde el admin
    db.commit()
    db.close()

definición cfg():
    db = obtener_db()
    filas = db.execute("SELECT clave,valor FROM configuracion").fetchall()
    db.close()
    devuelve {r["clave"]: r["valor"] para r en filas}

definición sitio_on():
    db = obtener_db()
    r = db.execute("SELECT valor FROM configuracion WHERE clave='activo'").fetchone()
    db.close()
    devuelve r["valor"] == "1" si r de lo contrario es Verdadero

definición fmt(n):
    devuelve "â‚¡ {:,.0f}".format(float(n o 0))

def esc(s):
    devuelve str(s o "").replace("\\","\\\\").replace("'","\\'").replace('"','\\"').replace("\n"," ")

def ficha_nueva():
    n = fecha y hora.ahora()
    devuelve n.strftime("%H%M%S") + str(n.microsegundo)[:3]

# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
# INICIALIZAR DB AL IMPORTAR (FIX RAILWAY/GUNICORN)
# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
init_db()

# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
#ESTILOS
# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
ESTILOS = """
<estilo>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');
*{tamaño de la caja:border-box;margen:0;relleno:0}
:raíz{
  --mo:#f5c518;
  --mo2:#c8a415;
  --hacer:#cc0000;
  --do2:#ff4444;
  --bg:#0a0a0a;
  --bl:#f5c518;
  --gr:#c8a415;
  --er:#dc2626;
  --ok:#16a34a;
  --r:10px;
  --sh:0 4px 18px rgba(200,0,0,.18);
}
cuerpo{font-family:'Nunito',sans-serif;fondo:#0a0a0a;color:#f5c518;altura mínima:100vh}
*{color:heredarse}
a,p,span,div,td,th,h1,h2,h3,h4,li{color:heredarse}

/* MARCA DE AGUA */
cuerpo::antes{
  contenido:"BISMARCK";posición:fija;abajo:18px;derecha:24px;
  tamaño de fuente: 4.5rem; peso de fuente: 900; espaciado entre letras: 5px;
  color:rgba(200,0,0,.08);eventos de puntero:ninguno;índice z:0;
}
cuerpo::después{
  contenido:"BISMARCK";posición:fija;arriba:38%;izquierda:-38px;
  tamaño de fuente: 3rem; peso de fuente: 900; espaciado entre letras: 4px;
  color:rgba(200,0,0,.05);eventos de puntero:ninguno;índice z:0;
  transformar:rotar(-90deg);transformar-origen:centro izquierdo;
}

/*NAV*/
navegación{
  fondo:gradiente-lineal(135deg,#1a0000,#8b0000);
  relleno:14px 28px;pantalla:flexible;alinear-elementos:centro;
  justificar-contenido:espacio-entre;posición:pegajosa;superior:0;índice-z:100;
  caja-sombra:0 3px 16px rgba(200,0,0,.4);
}
.logo{tamaño de fuente:1.5rem;peso de fuente:900;color:#fff;decoración de texto:ninguna;
  pantalla:flexible;alinear-elementos:centro;espacio:10px}
.logo img{alto:36px;ancho:36px;radio del borde:8px;ajuste al objeto:cubierta;
  borde:2px sólido rgba(255,255,255,.4)}
.badge-nav{fondo:var(--do2);color:#8b0000;tamaño de fuente:.6rem;peso de fuente:900;
  relleno:2px 8px;radio del borde:20px;espaciado entre letras:1px}
.nav-links{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.nav-links a{color:#f5c518;decoración de texto:none;relleno:6px 14px;
  radio del borde: 20px; tamaño de fuente: .84rem; peso de fuente: 700; transición: .2s;
  borde: 2px sólido transparente}
.nav-links a:hover,.nav-links a.on{background:rgba(255,255,255,.18);
  color del borde:rgba(255,255,255,.35)}
.btn-carrito{fondo:#cc0000;color:#fff;borde:ninguno;radio del borde:20px;
  relleno:7px 16px;tamaño de fuente:.88rem;peso de fuente:900;cursor:puntero;
  pantalla:flexible;alinear elementos:centrar;espacio:6px;transición:.2s;familia de fuentes:'Nunito',sans-serif}
.btn-carrito:hover{fondo:#ff4444;transformar:escala(1.04)}
.badge-cnt{fondo:#1a1a1a;color:#cc0000;radio del borde:50%;ancho:20px;alto:20px;
  mostrar:flexible en línea;alinear elementos:centrar;justificar contenido:centrar;
  tamaño de fuente: .72rem; peso de fuente: 900}

/* CONTENEDOR */
.wrap{ancho máximo: 1100px; margen: 0 automático; relleno: 26px 18px; posición: relativa; índice z: 1}

/* HÉROE */
.héroe{
  fondo:gradiente-lineal(135deg,#1a0000,#8b0000,#cc0000);
  radio del borde:var(--r);relleno:40px;alineación del texto:centro;margen inferior:24px;
  caja-sombra:0 8px 36px rgba(200,0,0,.35);posición:relativa;desbordamiento:oculto;
}
.hero::before{content:"ðŸ Š ðŸ ‹ ðŸ ‡ ðŸ “ ðŸ ðŸ¥ ðŸ ‰";posición:absoluta;arriba:8px;
  izquierda:0;derecha:0;tamaño de fuente:1.8rem;opacidad:.12;espaciado entre letras:16px}
.hero h1{tamaño de fuente:2.4rem;peso de fuente:900;color:#f5c518;margen inferior:8px;
  sombra de texto:0 2px 10px rgba(0,0,0,.3)}
.héroe p{color:#f5c518;tamaño de fuente:.98rem;peso de fuente:600}

/* BUSCADOR */
.buscador-box{fondo:#1a1a1a;radio-del-borde:var(--r);relleno:14px;
  margen inferior:14px;borde:2px sólido #440000;sombra de caja:var(--sh);
  pantalla:flexible;espacio:10px;alinear-elementos:centro}
.buscador-box input{flex:1;border:2px solid #440000;border-radius:8px;
  relleno:10px 14px;tamaño de fuente:.94rem;familia de fuentes:'Nunito',sans-serif;
  contorno:ninguno;color:var(--bl);transición:.2s}
.buscador-box entrada:enfoque{color-borde:var(--mo)}
.btn-limpiar{fondo:#f5f0ff;borde:2px sólido #440000;radio del borde:8px;
  relleno:9px 14px;cursor:puntero;color:var(--mo);tamaño de fuente:.84rem;
  peso de fuente: 800; familia de fuentes: 'Nunito', sans-serif; transición: .2s}
.btn-limpiar:hover{fondo:var(--mo);color:#fff}

/* CATEGORÍAS */
.cats{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px}
.cat{relleno:7px 16px;radio del borde:20px;borde:2px sólido var(--do);
  fondo:#1a1a1a;color:var(--bl);tamaño de fuente:.82rem;peso de fuente:800;
  cursor:puntero;transición:.2s;familia-de-fuentes:'Nunito',sans-serif}
.cat:hover,.cat.sel{fondo:linear-gradient(135deg,var(--mo),var(--mo2));
  color:#fff;color-borde:var(--mo)}

/* TARJETAS */
.grid{display:grid;grid-template-columns:repeat(autocompletar,minmax(210px,1fr));gap:16px}
.card{fondo:#1a1a1a;radio del borde:var(--r);borde:2px sólido #440000;
  desbordamiento: oculto; transición: .25s; sombra de caja: var(--sh)}
.card:hover{transformar:traducirY(-4px);sombra-de-caja:0 10px 28px rgba(200,0,0,.28);
  color del borde: #cc0000}
.card-img{ancho:100%;alto:148px;fondo:gradiente-lineal(135deg,#1a0000,#2a0000);
  pantalla:flexible;alinear elementos:centrar;justificar contenido:centrar;tamaño de fuente:3.2rem;
  posición:relativa;cursor:puntero}
.tag-cat{posición:absoluta;superior:8px;izquierda:8px;fondo:gradiente-lineal(135deg,#8b0000,#cc0000);
  color: #fff; tamaño de fuente: 66rem; peso de fuente: 900; relleno: 3px 9px; radio del borde: 20px}
.tag-ver{posición:absoluta;inferior:8px;derecha:8px;fondo:rgba(180,0,0,.85);
  color: #fff; tamaño de fuente: .68rem; relleno: 3px 8px; radio del borde: 6px; peso de la fuente: 700}
.card-body{relleno:13px}
.card-nombre{font-size:.98rem;font-weight:900;margin-bottom:2px;cursor:pointer;
  color:#f5c518;transición:.2s}
.card-nombre:hover{color:var(--mo)}
.card-desc{tamaño de fuente: .75rem;color: #c8a415;margen inferior: 5px;altura de línea: 1.4}
.card-unidad{font-size:.73rem;color:var(--mo);font-weight:700;margin-bottom:8px}
.card-precio{font-size:1.22rem;font-weight:900;color:#f5c518;margin-bottom:10px}

/* CANTIDAD */
.qty-row{display:flex;align-items:center;gap:8px;margin-bottom:10px}
.qty-btn{ancho:30px;alto:30px;radio del borde:50%;borde:2px sólido var(--mo);
  fondo:#1a1a1a;color:var(--mo);tamaño de fuente:1.15rem;peso de fuente:900;cursor:puntero;
  pantalla:flexible;alinear-elementos:centrar;justificar-contenido:centrar;transición:.2s}
.qty-btn:hover{fondo:#cc0000;color:#fff}
.cantidad-núm{ancho:48px;alineación-del-texto:centro;borde:2px sólido #440000;radio-del-borde:8px;
  relleno: 4px; tamaño de fuente: .95rem; peso de fuente: 800; familia de fuentes: 'Nunito', sans-serif}
.btn-add{ancho:100%;relleno:10px;borde:ninguno;radio del borde:8px;
  fondo: gradiente lineal (135 grados, var (--mo), var (--mo2));
  color:#fff;tamaño de fuente:.88rem;peso de fuente:900;cursor:puntero;
  familia de fuentes: 'Nunito', sans-serif; transición: .2s}
.btn-add:hover{transformar:translateY(-1px);box-shadow:0 4px 12px rgba(180,0,0,.35)}
.btn-add.ok{fondo:gradiente-lineal(135grados,#16a34a,#22c55e)}

/* FORMULARIOS */
.fg{margen inferior:13px}
.fg etiqueta{pantalla:bloque;tamaño de fuente:.76rem;color:#c8a415;margen inferior:4px;
  peso de fuente: 800; transformación de texto: mayúsculas; espaciado entre letras: 0,4 px}
.fg entrada, .fg selección, .fg área de texto {ancho: 100%; relleno: 10px 13px;
  fondo:#1a1a1a;borde:2px sólido #440000;radio del borde:8px;
  color:#fff;tamaño de fuente:.92rem;familia de fuentes:'Nunito',sans-serif;transición:.2s}
.fg entrada:enfoque, .fg selección:enfoque, .fg área de texto:enfoque{contorno:ninguno;color del borde:#cc0000}
.fg textarea{cambio de tamaño: vertical; altura mínima: 68 px}

/* BOTONES */
.btn{mostrar:inline-flex;alinear-elementos:centro;espacio:6px;relleno:10px 20px;
  borde:ninguno;radio del borde:8px;tamaño de fuente:.87rem;peso de fuente:800;cursor:puntero;
  transición:.2s;decoración de texto:ninguna;familia de fuentes:'Nunito',sans-serif}
.btn-mo{fondo:gradiente-lineal(135deg,#8b0000,#cc0000);color:#f5c518}
.btn-mo:hover{transformar:translateY(-1px);box-shadow:0 4px 12px rgba(180,0,0,.35)}
.btn-do{fondo:gradiente-lineal(135 grados,var(--do),var(--do2));color:#8b0000}
.btn-do:hover{transformar:traducirY(-1px)}
.btn-ve{fondo:gradiente-lineal(135grados,#16a34a,#22c55e);color:#f5c518}
.btn-ve:hover{transformar:traducirY(-1px)}
.btn-ro{fondo:gradiente-lineal(135grados,#dc2626,#ef4444);color:#f5c518}
.btn-ro:hover{transformar:traducirY(-1px)}
.btn-az{fondo:gradiente-lineal(135grados,#1d4ed8,#3b82f6);color:#f5c518}
.btn-full{ancho:100%;justificar-contenido:centro}

/* ALERTAS */
.alerta{relleno:11px 15px;radio del borde:8px;margen inferior:12px;
  tamaño de fuente: .87rem; peso de fuente: 700}
.alerta-ok{fondo:#dcfce7;borde:1px sólido #16a34a;color:#f5c518}
.alerta-er{fondo:#fee2e2;borde:1px sólido #dc2626;color:#b91c1c}
.alerta-in{fondo:#fef9c3;borde:1px sólido #ca8a04;color:#92400e}

/* PANEL */
.panel{fondo:#1a1a1a;radio del borde:var(--r);relleno:20px;
  borde:2px sólido #440000;margen inferior:18px;sombra de caja:var(--sh)}
.panel h2{tamaño de fuente:1.15rem;peso de fuente:900;color:#f5c518;
  margen inferior: 14px; borde inferior: 2px sólido #440000; relleno inferior: 8px}

/* ESTADÍSTICAS */
.stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px;margin-bottom:18px}
.stat{fondo:#1a1a1a;radio del borde:var(--r);relleno:16px;alineación del texto:centro;
  borde: 2px sólido #440000; borde superior: 4px sólido var(--do); sombra de caja: var(--sh)}
.stat-n{tamaño de fuente: 1.9rem;peso de fuente: 900;color: #f5c518}
.stat-l{tamaño de fuente: .7rem;color: #c8a415;margen superior: 2px;transformación de texto: mayúsculas;
  espaciado entre letras: 0,5 px; peso de fuente: 700}

/* TABLA */
.tabla-wrap{desbordamiento-x:auto}
tabla{ancho:100%;colapso del borde:colapso}
th{fondo:gradiente-lineal(135deg,#1a0000,#8b0000);relleno:10px 12px;
  alineación de texto:izquierda;color:#fff;tamaño de fuente:.76rem;transformación de texto:mayúsculas;espaciado entre letras:.7px}
td{relleno:9px 12px;borde inferior:1px sólido #2a0000;tamaño de fuente:.86rem;alineación vertical:medio;color:#f5c518}
tr:hover td{fondo:#1a0000}

/* INSIGNIAS */
.bdg{display:inline-block;padding:3px 10px;border-radius:20px;font-size:.72rem;font-weight:800}
.bdg-p{fondo:#2a1a00;color:#ffa500;borde:1px sólido #aa6600}
.bdg-c{fondo:#002a0a;color:#22c55e;borde:1px sólido #16a34a}
.bdg-x{fondo:#2a0000;color:#f5c518;borde:1px sólido #cc0000}
.bdg-e{fondo:#001a2a;color:#38bdf8;borde:1px sólido #0284c7}
.bdg-espera{fondo:#2a1500;color:#f5a623;borde:1px sólido #a06010}

/* PEDIDOS PROCESO */
.proceso{fondo:#1a1a1a;radio-del-borde:var(--r);relleno:16px;margen-inferior:20px;
  borde:2px sólido #440000;borde-izquierdo:5px sólido var(--do);sombra-de-caja:var(--sh)}
.proceso h3{color:var(--mo);font-size:1.05rem;font-weight:900;margin-bottom:10px}
.ped-chip{fondo:#2a0000;radio del borde:8px;relleno:8px 13px;
  pantalla:flexible;alinear elementos:centro;espacio:9px;margen inferior:5px;
  borde izquierdo: 3px sólido var(--mo2);flex-wrap:wrap}
.ped-id{fondo:var(--mo);color:#fff;radio del borde:20px;relleno:2px 9px;
  peso de fuente: 900; tamaño de fuente: .76rem}
.ped-ficha{fondo:#cc0000;color:#fff;radio del borde:20px;relleno:2px 9px;
  peso de fuente: 900; tamaño de fuente: .76rem}

/* MODAL */
.overlay{display:none;position:fixed;top:0;left:0;width:100%;height:100%;
  fondo:rgba(0,0,0,.58);índice z:9999;justificar contenido:centro;
  alinear elementos: inicio flexible; relleno: 28px 14px; desbordamiento y: automático; filtro de fondo: desenfoque (3px)}
.overlay.abierto{display:flex}
.modal{fondo:#1a1a1a;radio del borde:var(--r);relleno:26px;ancho:100%;
  ancho máximo: 520 px; borde: 2 px sólido #cc0000; posición: relativa; margen: automático;
  sombra de caja:0 18px 54px rgba(180,0,0,.22)}
.modal.ancho{ancho máximo: 580px}
.modal-x{posición:absoluta;superior:11px;derecha:13px;fondo:rgba(0,0,0,.07);
  borde:ninguno;color:var(--bl);tamaño de fuente:1.25rem;peso de fuente:900;cursor:puntero;
  radio del borde: 7px; ancho: 30px; alto: 30px; visualización: flex; alinear elementos: centro;
  justificar-contenido:centro;transición:.2s}
.modal-x:hover{fondo:var(--er);color:#fff}
.modal-titulo{tamaño de fuente:1.25rem;peso de fuente:900;color:var(--mo);
  margen inferior: 16px; relleno derecho: 33px}

/* CARRITO */
.car-item{display:flex;align-items:flex-start;padding:9px 0;
  borde inferior: 1 px sólido #440000; espacio: 9 px}
.car-nombre{font-weight:800;font-size:.89rem;cursor:pointer;color:var(--mo)}
.cantidad-de-coche{color:#c8a415;tamaño-de-fuente:.8rem}
.car-precio{color:var(--mo);font-weight:900;font-size:.89rem}
.car-total-row{visualización:flexible;justificar-contenido:espacio-entre;relleno:13px 0;
  tamaño de fuente: 1.08rem; peso de fuente: 900; borde superior: 2px sólido var(--mo); margen superior: 7px}
.car-total-row span:last-child{color:#f5c518;font-size:1.2rem}

/* BOLETO */
.ticket{fondo:#1a1a1a;color:#1a0033;radio del borde:8px;relleno:18px;
  familia de fuentes: 'Courier New', monoespaciado; borde: 2 px discontinuo #440000}
.tk-head{text-align:center;border-bottom:2px discontinuo #440000;
  relleno-inferior:9px;margen-inferior:9px}
.tk-row{display:flex;justify-content:space-between;padding:2px 0;font-size:.83rem;color:#f5c518}
.tk-foot{text-align:center;margin-top:9px;border-top:2px discontinuo #440000;
  relleno superior:8px;tamaño de fuente:.73rem;color:#c8a415}

/* PEDIDO CLIENTE */
.ped-card{fondo:#1a1a1a;radio del borde:var(--r);relleno:14px;margen inferior:11px;
  borde: 2px sólido #440000; borde izquierdo: 4px sólido var(--mo); sombra de caja: var(--sh)}
.ped-meta{display:flex;gap:12px;flex-wrap:wrap;margin-top:8px;
  tamaño de fuente: .81rem; color: #c8a415}
.confirmar-box{fondo:#1a0000;borde:2px sólido #cc0000;radio del borde:8px;
  relleno:14px;margen:9px 0}

/* ACCESO */
.login-box{ancho máximo:370px;margen:68px automático;fondo:#1a1a1a;radio del borde:var(--r);
  relleno:38px;borde:2px sólido #440000;sombra de caja:0 8px 36px rgba(180,0,0,.14)}
.login-box h2{texto-alineado:centro;margen-inferior:22px;color:#f5c518;
  tamaño de fuente: 1.9rem; peso de fuente: 900}

/* ADMINISTRADOR GRILLA */
.ag{display:grid;grid-template-columns:1fr 2fr;gap:18px}
@media(ancho máximo: 720px){.ag{columnas de plantilla de cuadrícula: 1fr}}

/* TABLA DE ELEMENTOS */
.it{ancho:100%;colapso del borde:colapso;tamaño de fuente:.81rem;margen:7px 0}
.it th{fondo:#2a0000;relleno:5px 9px;alineación del texto:izquierda;color:#f5c518;tamaño de fuente:.73rem}
.it td{relleno:5px 9px;borde inferior:1px sólido #440000}

/* SECCIÓN ENV */
.env-section{fondo:#1a1a1a;radio del borde:var(--r);relleno:20px;margen inferior:18px;
  borde:2px sólido #ff2222;sombra de caja:var(--sh)}
.env-section h2{tamaño de fuente:1.1rem;peso de fuente:900;margen inferior:14px;
  color: #f5c518; borde inferior: 1 px sólido #1a0000; relleno inferior: 8 px}

/* PESTAÑAS */
.tabs{display:flex;gap:7px;margin-bottom:16px;flex-wrap:wrap}

/* CONFIG */
.logo-prev{ancho:66px;alto:66px;ajuste-del-objeto:cubierta;radio-del-borde:8px;
  borde:2px sólido var(--do);mostrar:bloque;margen inferior:9px}

/* PIE DE PÁGINA */
pie de página{texto alineado:centro;relleno:24px;color:#c8a415;tamaño de fuente:.76rem;
  borde superior:2px sólido #440000;margen superior:34px;fondo:#1a1a1a;
  posición:relativa;índice z:1;peso de fuente:700}
pie de página span{color:var(--mo);font-weight:900}
</estilo>
"""

# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
#JS CARRITO
# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
JS_CARRITO = """
<guión>
var carrito = {};

función abrirModal(id){ documento.getElementById(id).classList.add('abierto'); documento.body.style.overflow='hidden'; }
función cerrarModal(id){ document.getElementById(id).classList.remove('abierto'); document.body.style.overflow=''; }
document.addEventListener('click', function(e){ if(e.target.classList.contains('overlay')){ e.target.classList.remove('abierto'); document.body.style.overflow=''; } });

función mostrarTab(t){
  ['pedidos','encargos','productos','config','stats'].forEach(function(x){
    var el = document.getElementById('tab_'+x);
    if(el) el.style.display = (x===t) ? 'bloque' : 'ninguno';
  });
}

función cambiarQty(id, delta){
  var inp = document.getElementById('cantidad_'+id);
  si(!inp) retorna;
  var v = parseInt(inp.value||0) + delta;
  si(v < 0) v = 0;
  entrada.valor = v;
}

función actualizarContador(){
  var total=0, n=0;
  for(var k in carrito){ total += carrito[k].precio * carrito[k].qty; n += carrito[k].qty; }
  var el = document.getElementById('cnt-carrito');
  si(el) el.textContent = n;
}

function agregarProducto(id, nombre, precio, img, unidad){
  var inp = document.getElementById('cantidad_'+id);
  var cantidad = parseInt(entrada? entrada.valor: 0);
  if(qty <= 0){ alert('Ingresa una cantidad mayor a 0'); devolver; }
  if(carrito[id]){ carrito[id].qty += qty; }
  else { carrito[id] = {nombre:nombre, precio:precio, qty:qty, img:img||'', unidad:unidad||'unidad'}; }
  actualizarContador();
  var btn = document.getElementById('btn_'+id);
  if(btn){ btn.textContent='âœ… ¡Agregado!'; btn.classList.add('ok');
    setTimeout(función(){ btn.textContent='ðŸ›' Agregar'; btn.classList.remove('ok'); }, 1500); }
}

function agregarDesdeDetalle(id, nombre, precio, img, unidad){
  var inp = documento.getElementById('qd'+id);
  var cantidad = parseInt(entrada? entrada.valor: 0);
  if(qty <= 0){ alert('Ingresa una cantidad mayor a 0'); devolver; }
  if(carrito[id]){ carrito[id].qty += qty; }
  else { carrito[id] = {nombre:nombre, precio:precio, qty:qty, img:img||'', unidad:unidad||'unidad'}; }
  actualizarContador();
  var btn = document.getElementById('btn_'+id);
  if(btn){ btn.textContent='âœ… ¡Agregado!'; btn.classList.add('ok');
    setTimeout(función(){ btn.textContent='ðŸ›' Agregar'; btn.classList.remove('ok'); }, 1500); }
  cerrarModal('md'+id);
}

function quitarItem(id){ eliminar carrito[id]; actualizarContador(); renderCarrito(); }

función renderCarrito(){
  var el = document.getElementById('carrito-items');
  si(!el) regresa;
  var html='', total=0;
  para(var k en carrito){
    var it = carrito[k];
    var sub = it.precio * it.cantidad;
    total += sub;
    var imgH = it.img
      ? '<img src="'+it.img+'" style="ancho:50px;alto:50px;ajuste-del-objeto:cubierta;radio-del-borde:7px;borde:2px sólido #440000;reducción-flexible:0">'
      : '<div style="ancho:50px;alto:50px;fondo:#f5f0ff;radio-del-borde:7px;pantalla:flexible;alinear-elementos:centro;justificar-contenido:centro;tamaño-de-fuente:1.6rem;flex-shrink:0">ðŸŠ</div>';
    html += '<div class="artículo-de-coche">';
    html += imgH;
    html += '<div style="flex:1;min-width:0">';
    html += '<div class="car-nombre" onclick="abrirModal(\"det_'+k+'\")">'+it.nombre+' <span style="font-size:.7rem;color:#aaa">ðŸ” </span></div>';
    html += '<div style="font-size:.73rem;color:#888;margin:1px 0">ðŸ“¦ '+it.unidad+'</div>';
    html += '<div class="car-qty">'+it.qty+' Ã— â‚¡'+it.precio.toLocaleString('es-CR')+'</div>';
    html += '</div>';
    html += '<div style="display:flex;flex-direction:column;align-items:flex-end;gap:5px">';
    html += '<span class="car-precio">â‚¡'+sub.toLocaleString('es-CR')+'</span>';
    html += '<button onclick="quitarItem('+k+')" estilo="fondo:#fee2e2;borde:1px sólido #fca5a5;radio del borde:20px;relleno:2px 9px;cursor:puntero;color:#b91c1c;tamaño de fuente:.78rem;peso de fuente:800">âœ•</button>';
    html += '</div></div>';
  }
  if(!html) html = '<div style="text-align:center;padding:28px;color:#aaa"><div style="font-size:2.8rem;margin-bottom:9px">ðŸ›'</div><p>El carrito está vacío</p></div>';
  el.innerHTML = html;
  var tt = document.getElementById('carrito-total');
  if(tt) tt.textContent = 'â‚¡ '+total.toLocaleString('es-CR');
  var inp = document.getElementById('inp_items');
  si(inp){
    var elementos=[];
    for(var k in carrito){ items.push({id:k, nombre:carrito[k].nombre, precio:carrito[k].precio, qty:carrito[k].qty, unidad:carrito[k].unidad}); }
    inp.value = JSON.stringify(elementos);
  }
  var si = document.getElementById('inp_subtotal');
  si(si){ var s=0; for(var k in carrito) s+=carrito[k].precio*carrito[k].qty; si.valor=s; }
}

function abrirCarrito(){ renderCarrito(); abrirModal('modal_carrito'); }

función irAPedido(){
  if(Object.keys(carrito).length===0){ alert('Agrega productos al carrito primero'); devolver; }
  renderCarrito();
  cerrarModal('modal_carrito');
  abrirModal('modal_pedido');
}

función imprimirTicket(id){
  var el = document.getElementById(id);
  si(!el) regresa;
  var tk = el.querySelector('.ticket');
  si(!tk) retorna;
  var v = ventana.open('','_blank','ancho=460,alto:680');
  v.document.write('<!DOCTYPE html><html><head><title>Pedido</title><style>body{font-family:monospace;padding:18px;max-width:400px;margin:0 auto}.tk-row{display:flex;justify-content:space-between;padding:2px 0;font-size:.83rem;color:#f5c518}.tk-head{text-align:center;border-bottom:2px dashed #ccc;padding-bottom:8px;margin-bottom:8px}.tk-foot{text-align:center;margin-top:9px;border-top:2px dashed #ccc;padding-top:8px;font-size:.72rem;color:#888}</style></head><body>');
  v.documento.write(tk.outerHTML);
  v.document.write('</body></html>');
  v.documento.cerrar(); v.enfoque();
  setTimeout(función(){ v.print(); }, 350);
}

ventana.addEventListener('DOMContentLoaded', función(){
  var n = document.querySelectorAll('#grilla .card').length;
  var ct = document.getElementById('cnt-prods');
  if(ct) ct.textContent = '('+n+' productos)';
});
función toggleMotivo(id, val){
  var caja = documento.getElementById('motivo_caja_'+id);
  if(box) box.style.display = (val==='Negado') ? 'bloque' : 'ninguno';
}
</script>
"""

# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
# AYUDANTES HTML
# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
def nav(activo="tienda", c=Ninguno):
    si c es Ninguno: c = cfg()
    nom = c.get("nombre","Mercado Frutas Frescas")
    logotipo = c.get("logotipo","")
    logo_tag = ('<img src="data:image/jpeg;base64,%s">' % logo) si logo de lo contrario "ðŸ Š"
    links = [("tienda","/","ðŸ Š Tienda"),("mis_pedidos","/mis-pedidos","ðŸ“¦ Mis Pedidos"),("admin_panel","/admin","âš™ï¸ Admin")]
    li = "".join('<a href="%s" class="%s">%s</a>' % (u, "on" if activo==k else "", l) for k,u,l in links)
    return """<!DOCTYPE html><html lang="es"><head>
<meta charset="UTF-8"><meta name="ventana gráfica" content="ancho=ancho-del-dispositivo,escala-inicial=1.0">
<link rel="preconectar" href="https://fonts.googleapis.com">
<link rel="preconexión" href="https://fonts.gstatic.com" crossorigin>
<título>%s</título>%s</cabeza><cuerpo>
<navegación>
  <a class="logo" href="/">%s %s <span class="badge-nav">MERCADO FRESCO</span></a>
  <div class="nav-links">%s
    <button class="btn-carrito" onclick="abrirCarrito()">
      ðŸ›' Carrito <span class="badge-cnt" id="cnt-carrito">0</span>
    </botón>
  </div>
</nav>""" % (nom, ESTILOS, logo_tag, nom, li)

PIE = '<footer><p>ðŸ Š <span>Mercado Frutas Frescas</span> — Desarrollado por <span>Bismarck</span></p></footer>'

def alerta(msg, tipo="ok"):
    si no msg: devuelve ""
    cls = {"ok":"alerta-ok","er":"alerta-er","in":"alerta-in"}.get(tipo,"alerta-in")
    devolver '<div class="alerta %s">%s</div>' % (cls, msg)

def bdg_estado(e):
    m = {"Pendiente":("bdg-p","â ³"),"Aprobado":("bdg-c","âœ…"),"En Espera":("bdg-espera","ðŸ'°"),"Pagado":("bdg-c","ðŸ'μ"),"Negado":("bdg-x","â Œ"),"Confirmado":("bdg-c","âœ…"),"Cancelado":("bdg-x","â Œ"),"Enviado":("bdg-e","ðŸšš")}
    cls, ico = m.get(e, ("bdg-p","â ³"))
    devolver '<span class="bdg %s">%s %s</span>' % (cls, ico, e)

def tabla_items(items_json):
    prueba: items = json.loads(items_json)
    excepto: devolver "<p>—</p>"
    filas = ""
    para ello en artículos:
        sub = float(it["precio"]) * int(it["cantidad"])
        filas += "<tr><td>%s</td><td>%d %s</td><td>%s</td><td><strong>%s</strong></td></tr>" % (
            it["nombre"], it["cantidad"], it.get("unidad",""), fmt(it["precio"]), fmt(sub))
    devolver "<table class='it'><thead><tr><th>Producto</th><th>Cantidad</th><th>Precio</th><th>Subtotal</th></tr></thead><tbody>%s</tbody></table>" % filas

def hacer_ticket(p, admin=False):
    prueba: items = json.loads(p["items"])
    excepto: elementos = []
    filas = ""
    para ello en artículos:
        sub = float(it["precio"]) * int(it["cantidad"])
        filas += '<div class="tk-row"><span>%sx%d %s</span><span>%s</span></div>' % (
            it["nombre"][:18], it["cantidad"], it.get("unidad",""), fmt(sub))
    env_row = ""
    si float(p["envio"] o 0) > 0:
        env_row = '<div class="tk-row"><span>ðŸšš EnvÃo:</span><span style="color:var(--do)">+ %s</span></div>' % fmt(p["envio"])
    hora_row = ('<div class="tk-row"><span>â ° Llega:</span><strong>%s</strong></div>' % p["hora_entrega"]) if p["hora_entrega"] else ""
    pie_txt = "Panel Admin" if admin else "Â¡Gracias por tu compra! ðŸ Š"
    devolver """<div class="ticket">
  <div class="tk-head">
    <strong style="font-size:1rem;color:#cc0000">ðŸ Š Mercado Frutas Frescas</strong><br>
    <span style="font-size:.7rem;color:#888">%s — Pedido #%d · Ficha: %s</span>
  </div>
  <div class="tk-row"><span>ðŸ'¤ Cliente:</span><span>%s</span></div>
  <div class="tk-row"><span>ðŸ“± Celular:</span><span>%s</span></div>
  <div style="font-size:.77rem;color:#888;padding:2px 0 5px">ðŸ“ %s</div>
  <hr style="border:none;border-top:1px discontinuo #440000;margin:6px 0">
  %s
  <hr style="border:none;border-top:1px discontinuo #440000;margin:6px 0">
  <div class="tk-row"><span>Subtotal:</span><span>%s</span></div>
  %s
  <div class="tk-row" style="font-size:1rem;font-weight:900"><span>TOTAL:</span><span style="color:#cc0000">%s</span></div>
  %s
  <div class="tk-foot">%s</div>
</div>""" % (p["fecha"], p["id"], p["ficha"] o "—",
             p["nombre_cliente"], p["celular"], p["direccion"],
             filas, fmt(p["subtotal"]), env_row, fmt(p["total"]), hora_row, pie_txt)

def banner_activos(peatones):
    activos = [p for p in peds if p["estado"] in ("Pendiente","Aprobado","Confirmado","En Espera")]
    activos = ordenados(activos, clave=lambda x: x["id"])
    si no activos: devuelve ""
    patatas fritas = ""
    para p en activos[:10]:
        fch = ('<span class="ped-ficha">Ficha #%s</span>' % p["ficha"]) if p["ficha"] else ""
        n = len(json.loads(p["elementos"] o "[]"))
        chips += '<div class="ped-chip"><span class="ped-id">#%d</span>%s<strong>%s</strong><span style="color:#888;font-size:.8rem">— %d artículos</span>%s</div>' % (
            p["id"], fch, p["nombre_cliente"], n, bdg_estado(p["estado"]))
    extra = " (%d total)" % len(activos) if len(activos) > 10 else ""
    return '<div class="proceso"><h3>ðŸ Š Pedidos en Proceso%s</h3>%s</div>' % (extra, chips)


# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
# RUTA: TIENDA
# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•

@app.route("/imagen/<int:pid>")
def imagen_producto(pid):
    db = obtener_db()
    fila = db.execute("SELECT imagen FROM productos WHERE id=?", (pid,)).fetchone()
    db.close()
    si no es fila o no es fila["imagen"]:
        devolver "", 404
    raw = fila["imagen"]
    si ";" en bruto:
        mime, b64 = raw.split(";", 1)
    demás:
        mime, b64 = "imagen/jpeg", sin procesar
    Respuesta de importación de matraz
    importar base64 como b64mod
    devolver Respuesta(b64mod.b64decode(b64), tipo MIME=mime,
                    encabezados={"Cache-Control": "público, edad máxima=86400"})


@app.route("/")
def tienda():
    si no sitio_on():
        return "<h1 style='text-align:center;padding:80px;font-family:sans-serif'>ðŸ Š El mercado está temporalmente cerrado.</h1>"
    c = cfg()
    db = obtener_db()
    prods = db.execute("SELECT * FROM productos WHERE activo=1 ORDER BY categoria,nombre").fetchall()
    peds = db.execute("SELECT * FROM pedidos WHERE estado IN ('Pendiente','Confirmado') ORDER BY id LIMIT 15").fetchall()
    db.close()
    msg = solicitud.args.get("msg","")
    tipo = request.args.get("tipo","ok")
    nom = c.get("nombre","Mercado Frutas Frescas")

    gatos_conjunto = ordenado(conjunto(p["categoría"] para p en productos))
    cats_html = '<button class="cat sel" data-cat="todos" onclick="filtrarCat(this,\'todos\')">ðŸ Š Todos</button>'
    iconos = {"Tropicales":"ðŸŒ´","CÃtricos":"ðŸ ‹","Berries":"ðŸ “","Frutas":"ðŸ Ž","Verduras":"ðŸ¥¬","Otros":"ðŸ›'"}
    para gato en cats_set:
        ico = iconos.get(gato, "ðŸ Š")
        gatos_html += '<button class="cat" data-cat="%s" onclick="filtrarCat(this,\'%s\')">%s %s</button>' % (esc(cat),esc(cat),ico,cat)

    tarjetas_html = ""
    modales_det = ""
    para p en productos:
        has_img = bool(p["imagen"])
        img_src = "/imagen/%d" % p["id"] si tiene_img si no ""
        img_card = '<img src="%s" estilo="ancho:100%%;alto:100%%;object-fit:cover" cargando="perezoso">' % img_src si tiene_img si no "ðŸ Š"
        img_modal = ('<img src="%s" style="width:100%%;max-height:250px;object-fit:cover;border-radius:8px;margin-bottom:14px" loading="lazy">' % img_src) si tiene_img de lo contrario '<div style="text-align:center;font-size:5rem;padding:18px 0">ðŸŠ</div>'
        desc = p["descripcion"] o ""
        unid = p["unidad"] o "unidad"
        medio = "md%d" % p["id"]

        modales_det += """
<div class="superposición" id="%s">
  <div class="modal">
    <button class="modal-x" onclick="cerrarModal('%s')">âœ•</button>
    %s
    <div class="modal-titulo">%s</div>
    <div style="fondo:#150000;radio del borde:8px;relleno:10px 13px;margen inferior:13px;tamaño de fuente:.84rem;color:#555">
      %s
      <div style="margin-top:5px;color:var(--mo);font-weight:700">ðŸ“¦ Unidad: %s  Â·  ðŸ“‚ %s</div>
    </div>
    <div style="text-align:center;background:linear-gradient(135deg,#150000,#1a0000);border-radius:8px;padding:13px;margin-bottom:13px">
      <div style="font-size:1.9rem;font-weight:900;color:var(--mo)">%s</div>
      <div style="font-size:.76rem;color:#888">Por %s · Pago contra entrega</div>
    </div>
    <div clase="cantidad-fila" estilo="justificar-contenido:centro;margen-inferior:11px">
      <button class="qty-btn" onclick="cambiarQty('md%d',-1)">âˆ'</button>
      <input type="number" class="qty-num" id="qd%d" value="0" min="0">
      <button class="qty-btn" onclick="cambiarQty('md%d',1)">+</button>
    </div>
    <button class="btn btn-mo btn-full" data-img="%s" onclick="agregarDesdeDetalle(%d,'%s',%g,this.dataset.img,'%s')">ðŸ›' Agregar al pedido</button>
  </div>
</div>""" % (mid, mid, img_modal, p["nombre"],
             desc, unid, p["categoría"],
             fmt(p["precio"]), unid,
             p["id"], p["id"], p["id"],
             img_src, p["id"], esc(p["nombre"]), p["precio"], esc(unid))

        tarjetas_html += """<div class="tarjeta" data-cat="%s" data-nombre="%s">
  <div class="card-img" onclick="abrirModal('%s')">
    <span class="tag-cat">%s</span>%s<span class="tag-ver">ðŸ” Ver más</span>
  </div>
  <div class="cuerpo-de-la-tarjeta">
    <div class="card-nombre" onclick="abrirModal('%s')">%s</div>
    %s
    <div class="card-unidad">ðŸ“¦ Por %s</div>
    <div class="card-precio">%s</div>
    <div class="cantidad-fila">
      <button class="qty-btn" onclick="cambiarQty(%d,-1)">âˆ'</button>
      <input type="number" class="cantidad-num" id="cantidad_%d" value="0" min="0">
      <button class="qty-btn" onclick="cambiarQty(%d,1)">+</button>
    </div>
    <button class="btn-add" id="btn_%d" data-img="%s" onclick="agregarProducto(%d,'%s',%g,document.getElementById('btn_%d').dataset.img,'%s')">ðŸ›' Agregar</button>
  </div>
</div>""" % (esc(p["categoria"]), esc(p["nombre"]),
             medio, p["categoría"], img_card,
             medio, p["nombre"],
             ('<div class="card-desc">%s</div>' % desc[:55]+("..." si len(desc)>55 de lo contrario "")) si desc de lo contrario "",
             unid, fmt(p["precio"]),
             p["id"], p["id"], p["id"],
             p["id"], img_src, p["id"], esc(p["nombre"]), p["precio"], p["id"], esc(unid))

    grid = '<div class="grid" id="grilla">%s</div>' % cards_html if cards_html else '<div class="alerta alerta-in">No hay productos disponibles.</div>'

    modal_carrito = """
<div class="overlay" id="modal_carrito">
  <div class="modal ancho">
    <button class="modal-x" onclick="cerrarModal('modal_carrito')">âœ•</button>
    <div class="modal-titulo">ðŸ›' Tu Carrito</div>
    <div id="carrito-items"></div>
    <div class="car-total-row"><span>Total:</span><span id="carrito-total">â‚¡ 0</span></div>
    <button class="btn btn-mo btn-full" style="margin-top:13px" onclick="irAPedido()">âœ… Hacer Pedido</button>
  </div>
</div>"""

    modal_pedido = """
<div class="overlay" id="modal_pedido">
  <div class="modal ancho">
    <button class="modal-x" onclick="cerrarModal('modal_pedido')">âœ•</button>
    <div class="modal-titulo">ðŸ'¤ Datos del Cliente</div>
    <formulario método="POST" acción="/hacer-pedido">
      <tipo de entrada="oculto" nombre="items_json" id="inp_items">
      <input type="hidden" name="subtotal" id="inp_subtotal">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:11px">
        <div class="fg"><label>Nombre Completo *</label>
          <input type="text" name="nombre" required placeholder="Juan García"></div>
        <div class="fg"><label>Celular *</label>
          <input type="text" name="celular" required placeholder="8888-8888"></div>
      </div>
      <div class="fg"><label>Notas del pedido</label>
        <textarea name="notas" placeholder="Ej: frutas bien maduras, sin golpes..."></textarea></div>
      <div style="fondo:#150000;borde:2px sólido #440000;radio del borde:8px;relleno:11px;margen inferior:13px;tamaño de fuente:.82rem;color:#888">
        ðŸ“ Su pedido quedará listo para <strong>recoger</strong> en el mercado.<br>
        ðŸ'μ Pago <strong>contra entrega</strong> al momento de recoger.
      </div>
      <button type="submit" class="btn btn-mo btn-full">âœ… Confirmar Pedido</button>
    </form>
  </div>
</div>"""

    devolver nav("tienda", c) + """
<div class="wrap">
  <div class="héroe">
    %s
    <p>Frutas frescas del mercado directo a tu puerta ðŸ ‹</p>
  </div>
  %s%s
  <div class="buscador-box">
    <span style="font-size:1.2rem">ðŸ” </span>
    <input type="text" id="inp-buscar" placeholder="Buscar fruta o categoría... (ej: mango, fresa, cítricos)" oninput="buscar(this.value)">
    <button class="btn-limpiar" onclick="limpiar()">âœ• Limpiar</button>
  </div>
  <div class="gatos">%s</div>
  <h2 style="font-size:1.5rem;font-weight:900;color:var(--mo);margin-bottom:14px">
    ðŸ ‹ Productos Frescos <span id="cnt-prods" style="font-size:.88rem;color:#888;font-weight:700"></span>
  </h2>
  %s
  <div id="sin-resultados" style="display:none;text-align:center;padding:38px;color:#aaa">
    <div style="font-size:2.8rem;margin-bottom:10px">ðŸ” </div><p>No se encontraron productos.</p>
  </div>
</div>
%s%s%s
<guión>
función filtrarCat(btn, cat){
  documento.querySelectorAll('.cat').forEach(función(b){ b.classList.remove('sel'); });
  btn.classList.add('sel');
  btn.dataset.catActiva = gato;
  buscarYFiltrar(cat, document.getElementById('inp-buscar').value.toLowerCase());
}
función buscar(txt){
  var btn = document.querySelector('.cat.sel');
  var gato = btn? (btn.dataset.catActiva || btn.dataset.cat || 'todos') : 'todos';
  buscarYFiltrar(cat, txt.toLowerCase());
}
función buscarYFiltrar(cat, txt){
  var tarjetas = document.querySelectorAll('#grilla .tarjeta');
  var vis = 0;
  tarjetas.paraCada(función(c){
    var mc = (cat==='todos' || c.dataset.cat===cat);
    var mb = !txt || (c.dataset.nombre||'').toLowerCase().includes(txt) || (c.dataset.cat||'').toLowerCase().includes(txt);
    c.style.display = (mc && mb) ? '' : 'ninguno';
    si(mc && mb) vis++;
  });
  document.getElementById('sin-resultados').style.display = vis===0 ? 'block' : 'none';
  var ct = document.getElementById('cnt-prods');
  if(ct) ct.textContent = '('+vis+' productos)';
}
función limpiar(){
  documento.getElementById('inp-buscar').value = '';
  var btns = document.querySelectorAll('.cat');
  btns.forEach(función(b){ b.classList.remove('sel'); });
  btns[0].classList.add('sel');
  buscarYFiltrar('todos','');
}
</script>
""" % (nom, alerta(msg,tipo), "", cats_html, grid,
       modal_carrito, modal_pedido, modales_det) + PIE + JS_CARRITO + "</body></html>"


# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
# RUTA: HACER PEDIDO
# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
@app.route("/hacer-pedido", métodos=["POST"])
def hacer_pedido():
    si no sitio_on(): devolver redirect(url_for("tienda"))
    f = solicitud.formulario
    items_raw = f.get("items_json","[]")
    subtotal = float(f.get("subtotal",0))
    nombre = f.get("nombre","").strip()
    celular = f.get("celular","").strip()
    notas = f.get("notas","").strip()
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    fch = ficha_nueva()
    db = obtener_db()
    db.execute("""INSERTAR EN pedidos(nombre_cliente,celular,direccion,barrio,referencia,
        notas,items,subtotal,envio,total,fecha,ficha)
        VALORES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (nombre,celular,'','','',notas,items_raw,subtotal,0,subtotal,fecha,fch))
    db.commit(); db.close()
    retorno redirección(url_para("tienda",
        msg="âœ… Pedido realizado. Ficha #%s â€ Ve a 'Mis Pedidos' con tu celular para seguimiento." % fch,
        tipo="ok"))


# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
# RUTA: MIS PEDIDOS
# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
@app.route("/mis-pedidos", métodos=["GET","POST"])
def mis_pedidos():
    c = cfg()
    celular = Ninguno; peds = Ninguno; msg = Ninguno
    si solicitud.metodo == "POST":
        celular = request.form.get("celular","").strip()
    elif solicitud.args.get("celular"):
        celular = request.args.get("celular","").strip()
        msg = solicitud.args.get("msg","")
    si celular:
        db = obtener_db()
        peds = db.execute("SELECCIONAR * DE pedidos DONDE celular=? ORDENAR POR id DESC",(celular,)).fetchall()
        db.close()

    items_html = ""; modales = ""
    si peatones:
        para p en peds:
            envio = float(p["envio"] o 0)
            cc = p["confirmacion"] o "pendiente"
            est = p["estado"]
            fch = p["ficha"] o ""

            if est=="Enviado": borde="border-left-color:#ff2222"
            elif cc=="revisión": borde="color del borde izquierdo:#1d4ed8"
            elif cc=="cancelado": borde="border-left-color:#dc2626;opacidad:.75"
            elif est=="Confirmado": borde="border-left-color:#16a34a"
            de lo contrario: borde=""

            if est=="Enviado": bdg='<span class="bdg bdg-e">ðŸšš Enviado</span>'
            elif cc=="revision": bdg='<span class="bdg bdg-az" style="background:#dbeafe;color:#1e40af;border:1px solid #3b82f6">ðŸ”µ Revisar costo</span>'
            elif cc=="cancelado": bdg='<span class="bdg bdg-x">â Œ Cancelado</span>'
            elif p["estado"]=="Negado": bdg='<span class="bdg bdg-x">â Œ Negado</span>'
            elif p["estado"]=="Aprobado": bdg='<span class="bdg bdg-c">âœ… Aprobado</span>'
            elif cc=="aceptado": bdg='<span class="bdg bdg-c">âœ… Confirmado</span>'
            else: bdg='<span class="bdg bdg-p">â ³ Pendiente</span>'

            env_banner = ""
            si est=="Aprobado":
                env_banner = '<div style="background:#dcfce7;border:2px solid #16a34a;border-radius:8px;padding:12px;margin:9px 0;text-align:center"><p style="color:#f5c518;font-weight:900">âœ… ¡Pedido aprobado!</p><p style="font-size:.83rem;color:#888;margin-top:4px">Ya puede pasar a recogerlo. Pago al recoger.</p></div>'
            elif est=="Negado":
                motivo_txt = (p["motivo"] o "Sin especificar")
                env_banner = '<div style="background:#fee2e2;border:2px solid #dc2626;border-radius:8px;padding:12px;margin:9px 0"><p style="color:#b91c1c;font-weight:900;margin-bottom:5px">â Œ Pedido no disponible</p><p style="font-size:.84rem;color:#555">Motivo: <strong>%s</strong></p></div>' % motivo_txt

            confirmar_box = ""
            hora_sp = '<span style="color:#16a34a;font-weight:800">â ° Llega: %s</span>' % p["hora_entrega"] if p["hora_entrega"] else ""
            ficha_sp = '<span class="ped-ficha">Ficha #%s</span>' % fch if fch else ""
            mid_tk = "tk_%d" % p["id"]
            modales += """
<div class="superposición" id="%s">
  <div class="modal ancho">
    <button class="modal-x" onclick="cerrarModal('%s')">âœ•</button>
    <div class="modal-titulo">ðŸ§¾ Comprobante</div>
    %s
    <div style="display:flex;gap:9px;margin-top:12px">
      <button class="btn btn-mo" style="flex:1;justify-content:center" onclick="imprimirTicket('%s')">ðŸ–¨ï¸ Imprimir</button>
      <a href="/descargar/%d" class="btn btn-ve" style="flex:1;justify-content:center">â¬‡ï¸ Descargar</a>
    </div>
  </div>
</div>""" % (mid_tk, mid_tk, hacer_ticket(p), mid_tk, p["id"])

            n_items = len(json.loads(p["items"] o "[]"))
            artículos_html += """<div clase="ped-card" estilo="%s">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px">
    <strong>ðŸ Š Pedido #%d — %d producto(s)</strong>%s%s
  </div>
  %s%s
  <div class="ped-meta">
    <span>ðŸ'¤ %s</span><span>ðŸ“± %s</span><span>ðŸ“ %s</span>
    <span style="color:var(--mo);font-weight:800">%s</span>
    <span>%s</span>%s
  </div>
  <div style="margin-top:10px;display:flex;gap:7px;flex-wrap:wrap">
    <button class="btn btn-az" style="font-size:.81rem;padding:5px 12px" onclick="abrirModal('%s')">ðŸ§¾ Comprobante</button>
    <a href="/descargar/%d" class="btn btn-do" style="font-size:.81rem;padding:5px 12px">â¬‡ï¸ Descargar</a>
  </div>
</div>""" % (borde, p["id"], n_items, bdg, ficha_sp,
             env_banner, confirmar_box,
             p["nombre_cliente"], p["celular"], p["direccion"],
             fmt(p["total"]), p["fecha"], hora_sp, mid_tk, p["id"])

    Si peds no es Ninguno:
        si peatones:
            resultado = '<div style="background:#1a1a1a;border-radius:var(--r);padding:20px;border:2px solid #440000;margin-top:16px"><h2 style="font-size:1.1rem;font-weight:900;color:var(--mo);margin-bottom:14px">ðŸ“¦ Tus Pedidos â€” %s (%d)</h2>%s</div>' % (celular, len(peds), items_html)
        demás:
            resultado = '<div class="alerta alerta-in" style="margin-top:16px;text-align:center">No hay pedidos para <strong>%s</strong>.</div>' % celular
    demás:
        resultado = ""

    return nav("mis_pedidos", c) + """
<div class="wrap">
  <div class="héroe">
    <h1>ðŸ“¦ Seguimiento de Pedidos</h1>
    <p>Ingresa tu celular para ver el estado de tus pedidos</p>
  </div>
  <div class="panel" style="ancho máximo: 480px; margen: 0 automático">
    %s
    <form método="POST">
      <div class="fg"><label>ðŸ“± Tu Número de Celular</label>
        <input type="text" name="celular" value="%s" placeholder="8888-8888" required></div>
      <button type="submit" class="btn btn-mo btn-full">ðŸ” Buscar Mis Pedidos</button>
    </form>
  </div>
  %s
%s
""" % (alerta(msg,"ok"), celular o "", resultado, modales) + PIE + JS_CARRITO + "</body></html>"


@app.route("/confirmar/<int:pid>/<accion>/<celular>")
def confirmar(pid, acción, celular):
    db = obtener_db()
    si accion == "aceptar":
        db.execute("ACTUALIZAR pedidos SET confirmacion='aceptado',estado='Confirmado' WHERE id=?",(pid,))
        msg = "âœ… Pedido #%d confirmado." % pid
    demás:
        db.execute("ACTUALIZAR pedidos SET confirmacion='cancelado',estado='Cancelado' WHERE id=?",(pid,))
        msg = "â Œ Pedido #%d cancelado." % pid
    db.commit(); db.close()
    return redirigir(url_for("mis_pedidos", celular=celular, msg=msg))


@app.route("/descargar/<int:pid>")
definición descargar(pid):
    db = obtener_db()
    p = db.execute("SELECT * FROM pedidos WHERE id=?",(pid,)).fetchone()
    db.close()
    si no es p: devolver redireccionamiento(url_para("mis_pedidos"))
    prueba: items = json.loads(p["items"])
    excepto: elementos = []
    ln = ["="*46," MERCADO FRUTAS FRESCAS"," COMPROBANTE DE PEDIDO","="*46,
          " Pedido: #%d" % p["id"],
          " Ficha: %s" % (p["ficha"] o "-"),
          " Fecha: %s" % p["fecha"],"-"*46,
          " Cliente: %s" % p["nombre_cliente"],
          " Celular: %s" % p["celular"],
          " Dir: %s" % p["direccion"],"-"*46," FRUTAS:"]
    para ello en artículos:
        sub = float(it["precio"]) * int(it["cantidad"])
        ln.append(" %sx%d %s = %s" % (it["nombre"][:18], it["cantidad"], it.get("unidad",""), fmt(sub)))
    ln += ["-"*46," Subtotal: %s" % fmt(p["subtotal"])]
    si float(p["envio"] o 0) > 0:
        ln.append(" Envío: + %s" % fmt(p["envio"]))
    ln += [" TOTAL: %s" % fmt(p["total"])," Pago: Contra entrega","-"*46," ¡Gracias! ðŸ Š","="*46]
    devolver Respuesta("\n".join(ln), mimetype="text/plain",
        encabezados={"Content-Disposition":"archivo adjunto; nombre de archivo=pedido_%d.txt" % pid})


# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
# RUTA: ADMIN
# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
@app.route("/admin")
definición admin_panel():
    si no es session.get("admin"): devuelve redirección(url_for("admin_login"))
    db = obtener_db()
    peds = db.execute("SELECT * FROM pedidos ORDER BY id DESC").fetchall()
    productos = db.execute("SELECT * FROM productos ORDER BY id DESC").fetchall()
    db.close()
    devolver render_admin(peds, prods)


def render_admin(peds, prods, grafica=None, msg="", tipo="ok"):
    c = cfg()
    activos = [p for p in peds if p["estado"] in ("Pendiente","Aprobado","Confirmado","En Espera")]
    enviados = [p for p in peds if p["estado"] == "Enviado"]
    ingresos = suma(p["total"] for p in peds if p["estado"] != "Cancelado")

    estadísticas_html = """<div class="estadísticas">
  <div class="stat"><div class="stat-n">%d</div><div class="stat-l">Total</div></div>
  <div class="stat"><div class="stat-n" style="color:#f5a623">%d</div><div class="stat-l">Pendientes</div></div>
  <div class="stat"><div class="stat-n" style="color:#f5a623">%d</div><div class="stat-l">Pago En Espera</div></div>
  <div class="stat"><div class="stat-n" style="color:#22c55e">%d</div><div class="stat-l">Pagos</div></div>
  <div class="stat"><div class="stat-n" style="color:#ef4444">%d</div><div class="stat-l">Negados</div></div>
  <div class="stat"><div class="stat-n">%d</div><div class="stat-l">Productos</div></div>
  <div class="stat"><div class="stat-n" style="font-size:.95rem">%s</div><div class="stat-l">Ingresos</div></div>
</div>""" % (len(peatones),
             suma(1 para p en peds si p["estado"]=="Pendiente"),
             sum(1 for p in peds if p["estado"]=="En Espera"),
             suma(1 para p en peds si p["estado"]=="Pagado"),
             suma(1 para p en peds si p["estado"]=="Negado"),
             len(prods), fmt(ingresos))

    filas_ped = ""; modales_ped = ""
    para p en sorted(activos, clave=lambda x: x["id"]):
        envio = float(p["envio"] o 0)
        fch = p["ficha"] o "—"
        n_it = len(json.loads(p["elementos"] o "[]"))
        mid_o = "ao_%d" % p["id"]
        mid_e = "ae_%d" % p["id"]
        tk = hacer_ticket(p, admin=Verdadero)
        it_tbl = tabla_items(p["items"] o "[]")

        modales_ped += """
<div class="superposición" id="%s">
  <div class="modal ancho">
    <button class="modal-x" onclick="cerrarModal('%s')">âœ•</button>
    <div class="modal-titulo">ðŸ“‹ Pedido #%d</div>
    <div style="font-size:.82rem;color:#888;margin-bottom:11px">
      ðŸ'¤ <strong>%s</strong> · ðŸ“± %s<br>ðŸ“ %s%s
    </div>
    %s%s
    <button class="btn btn-mo btn-full" style="margin-top:12px" onclick="imprimirTicket('%s')">ðŸ–¨ï¸ Imprimir</button>
  </div>
</div>""" % (mid_o, mid_o, p["id"],
             p["nombre_cliente"], p["celular"], p["direccion"],
             (" · " + p["referencia"]) if p["referencia"] else "",
             it_tbl, tk, mid_o)

        sel_p = "seleccionado" if p["estado"]=="Pendiente" else ""
        sel_a = "seleccionado" if p["estado"]=="Aprobado" else ""
        sel_n = "seleccionado" if p["estado"]=="Negado" else ""
        mot_display = "bloquear" if p["estado"]=="Negado" else "none"
        mot_texto = p["motivo"] o ""
        modales_ped += (
            '<div class="overlay" id="' + mid_e + '">'
            '<div class="modal">'
            '<button class="modal-x" onclick="cerrarModal(\'' + mid_e + '\')">âœ•</button>'
            '<div class="modal-titulo">âœ ï¸ Editar Pedido #' + str(p["id"]) + '</div>'
            '<form method="POST" action="/admin/upd-pedido">'
            '<input type="hidden" name="pedido_id" value="' + str(p["id"]) + '">'
            '<div class="fg"><label>Estado del Pedido</label>'
            '<select name="estado" id="est_sel_' + str(p["id"]) + '" onchange="toggleMotivo(' + str(p["id"]) + ',this.value)">'
            '<option value="Pendiente"' + sel_p + '>â ³ Pendiente</option>'
            '<option value="Aprobado"' + sel_a + '>âœ… Aprobado</option>'
            '<option value="Negado"' + sel_n + '>â Œ Negado</option>'
            '</select></div>'
            '<div class="fg" id="motivo_box_' + str(p["id"]) + '" style="display:' + mot_display + '">'
            '<label>Motivo del rechazo</label>'
            '<textarea name="motivo" placeholder="Explica por qué se niega...">' + mot_texto + '</textarea>'
            '</div>'
            '<button type="submit" class="btn btn-mo btn-full">ðŸ'¾ Guardar</button>'
            '</form></div></div>'
        )

        filas_ped += """<tr>
  <td><strong>#%d</strong></td>
  <td><span class="ped-ficha">%s</span></td>
  <td><strong>%s</strong><br><span style="font-size:.73rem;color:#888">ðŸ“± %s</span></td>
  <td><span style="background:#1a0000;color:#cc0000;border:1px solid #ff2222;border-radius:20px;padding:2px 8px;font-size:.73rem;font-weight:800">%d elementos</span></td>
  <td style="color:var(--mo);font-weight:900">%s</td>
  %s
  <td style="display:flex;gap:5px;flex-wrap:wrap">
    <button class="btn btn-do" style="font-size:.76rem;padding:4px 9px" onclick="abrirModal('%s')">âœ ï¸ </button>
    <button class="btn btn-az" style="font-size:.76rem;padding:4px 9px" onclick="abrirModal('%s')">ðŸ“‹</button>
  </td>
</tr>""" % (p["id"], fch, p["nombre_cliente"], p["celular"],
            n_it, fmt(p["total"]), bdg_estado(p["estado"]), mid_e, mid_o)

    filas_env = ""; modales_env = ""
    para p en sorted(enviados, clave=lambda x: x["id"], reverso=Verdadero):
        mid_v = "env_%d" % p["id"]
        tk_e = hacer_ticket(p, admin=Verdadero)
        it_e = tabla_items(p["items"] o "[]")
        modales_env += """
<div class="superposición" id="%s">
  <div class="modal ancho">
    <button class="modal-x" onclick="cerrarModal('%s')">âœ•</button>
    <div class="modal-titulo">ðŸšš Enviado #%d</div>
    <div style="font-size:.82rem;color:#888;margin-bottom:11px">ðŸ'¤ <strong>%s</strong> · ðŸ“± %s</div>
    %s%s
    <button class="btn btn-mo btn-full" style="margin-top:12px" onclick="imprimirTicket('%s')">ðŸ–¨ï¸ Imprimir</button>
  </div>
</div>""" % (mid_v, mid_v, p["id"], p["nombre_cliente"], p["celular"], it_e, tk_e, mid_v)

        filas_env += """<tr style="opacidad:.85">
  <td><strong>#%d</strong></td>
  <td><span class="ped-ficha">%s</span></td>
  <td><strong>%s</strong></td>
  <td style="color:var(--mo);font-weight:900">%s</td>
  %s
  <td><button class="btn btn-mo" style="font-size:.76rem;padding:4px 9px" onclick="abrirModal('%s')">ðŸ“‹</button></td>
</tr>""" % (p["id"], p["ficha"] o "—", p["nombre_cliente"],
            fmt(p["total"]), p["fecha"], mid_v)

    gatos_opts = "".join('<opción valor="%s">%s</opción>' % (gato,gato)
                        para gato en ["Frutas","Tropicales","Cátricos","Berries","Verduras","Otros"])
    filas_prod = ""; modales_prod = ""
    para p en productos:
        mid_ep = "ep_%d" % p["id"]
        co = "".join('<option value="%s"%s>%s</option>' % (gato," seleccionado" si p["categoría"]==gato de lo contrario "", gato)
                     para gato en ["Frutas","Tropicales","Cátricos","Berries","Verduras","Otros"])
        modales_prod += """
<div class="superposición" id="%s">
  <div class="modal">
    <button class="modal-x" onclick="cerrarModal('%s')">âœ•</button>
    <div class="modal-titulo">âœ ï¸ Editar Producto</div>
    <form método="POST" acción="/admin/edit-prod">
      <input tipo="oculto" nombre="pid" valor="%d">
      <div class="fg"><label>Nombre</label><input type="text" name="nombre" value="%s" required></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
        <div class="fg"><label>Precio (€)</label><input type="number" name="precio" value="%g" required min="0" step="50"></div>
        <div class="fg"><label>Categoría</label><select name="categoría">%s</select></div>
        <div class="fg"><label>Unidad de venta</label><input type="text" name="unidad" value="%s" placeholder="kg, unidad, racimo"></div>
      </div>
      <div class="fg"><label>Descripción</label><textarea name="descripcion">%s</textarea></div>
      <button type="submit" class="btn btn-mo btn-full">ðŸ'¾ Guardar</button>
    </form>
  </div>
</div>""" % (mid_ep, mid_ep, p["id"], p["nombre"], p["precio"], co,
             p["unidad"] o "", p["descripcion"] o "")

        filas_prod += """<tr>
  <td><strong>%s</strong><div style="font-size:.73rem;color:#888">%s · %s</div></td>
  <td><span style="background:#1a0000;color:#cc0000;border:1px solid #ff2222;border-radius:20px;padding:2px 8px;font-size:.73rem;font-weight:800">%s</span></td>
  <td style="color:var(--mo);font-weight:900">%s</td>
  <td style="display:flex;gap:5px">
    <button class="btn btn-do" style="font-size:.78rem;padding:4px 9px" onclick="abrirModal('%s')">âœ ï¸ </button>
    <a href="/admin/del-prod/%d" onclick="return confirm('¿Eliminar?')" class="btn btn-ro" style="font-size:.78rem;padding:4px 9px">ðŸ—'ï¸ </a>
  </td>
</tr>""" % (p["nombre"], p["unidad"] o "", (p["descripcion"] o "")[:28],
            p["categoría"], fmt(p["precio"]), mid_ep, p["id"])

    nom_actual = c.get("nombre","Mercado Frutas Frescas")
    logo_actual = c.get("logotipo","")
    logo_prev = ('<img src="data:image/jpeg;base64,%s" class="logo-prev">' % logo_actual) si logo_actual de lo contrario ""
    en = cfg().get("activo","1") == "1"
    estado_box = '<div class="alerta alerta-ok">âœ… MERCADO ABIERTO</div>' if on else '<div class="alerta alerta-er">ðŸ”' MERCADO CERRADO</div>'
    btn_toggle = ""
    caja maestra = ""
    si sesión.get("master"):
        btn_toggle = '<a href="/admin/toggle" clase="btn %s btn-full" estilo="margin-bottom:14px">%s</a>' % (
            ("btn-ro","ðŸ”' Cerrar Mercado") if on else ("btn-ve","âœ… Abrir Mercado"))
        master_box = '<div class="alerta alerta-in"><p style="font-weight:900;margin-bottom:9px">ðŸ”' Panel Maestro</p><a href="/reset-frutas-2024" class="btn btn-ro">ðŸ—'ï¸ Reset del Mes</a></div>'
    elif sesión.get("admin"):
        master_box = '<div style="background:#1a1a1a;border:2px solid #440000;border-radius:var(--r);padding:16px;margin-bottom:16px"><p style="font-weight:900;color:var(--mo);margin-bottom:9px">ðŸ—'ï¸ Resetear Mes</p><a href="/reset-frutas-2024" class="btn btn-ro">ðŸ—'ï¸ Reset del Mes</a></div>'

    tab_config = """<div class="panel">
  <h2>ðŸŽ¨ Configuración del Mercado</h2>
  %s%s%s
  <form método="POST" acción="/admin/config" enctype="multipart/form-data">
    %s
    <div class="fg"><label>Nombre del Mercado</label>
      <input type="text" name="nombre" value="%s" required></div>
    <div class="fg"><label>Logotipo</label>
      <input type="file" name="logo" accept="image/*"></div>
    <button type="submit" class="btn btn-ve btn-full">ðŸ'¾ Guardar</button>
  </form>
</div>""" % (estado_box, btn_toggle, master_box, logo_prev, nom_actual)

    graf_html = ('<div style="text-align:center"><img src="data:image/png;base64,%s" style="max-width:100%%;border-radius:var(--r)"></div>' % grafica) if grafica else '<p style="text-align:center;color:#aaa;padding:20px">Haz clic en Generar Gráfica.</p>'

    html = nav("panel_de_administración", c)
    html += "<div clase='wrap'>"
    html += "<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;flex-wrap:wrap;gap:10px'>"
    html += "<h1 style='font-size:1.9rem;font-weight:900;color:var(--mo)'>âš™ï¸ Administrador del panel</h1>"
    html += "<a href='/admin/logout' class='btn btn-ro'>ðŸšª Salir</a></div>"
    html += alerta(msg, tipo)
    html += banner_activos(activos)
    html += estadísticas_html
    html += "<div style='display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:18px;flex-wrap:wrap'>"
    html += " <div style='display:flex;gap:7px;flex-wrap:wrap'>"
    html += " <button class='btn btn-mo' onclick=\"mostrarTab('pedidos')\">ðŸ“‹ Pedidos</button>"
    html += " <button class='btn' onclick=\"mostrarTab('encargos')\" style='background:linear-gradient(135deg,#7c3aed,#a855f7);color:#fff'>ðŸ“¦ Encargos</button>"
    html += " <button class='btn btn-do' onclick=\"mostrarTab('productos')\">ðŸ Š Productos</button>"
    html += " <button class='btn btn-ve' onclick=\"mostrarTab('config')\">âš™ï¸ Config</button>"
    html += " <button class='btn btn-az' onclick=\"mostrarTab('stats')\">ðŸ“Š Estadísticas</button>"
    html += " </div>"
    html += " <a href='/admin/encargos' style='background:linear-gradient(135deg,#cc0000,#ff4444);color:#8b0000;padding:12px 22px;border-radius:8px;font-weight:900;font-size:.95rem;text-decoration:none;border:none;display:inline-flex;align-items:center;gap:7px;white-space:nowrap;font-family:Nunito,sans-serif'>ðŸ–¨ï¸ Encargos del Día</a>"
    html += "</div>"

    html += "<div id='tab_pedidos'>"
    html += "<div class='panel'><h2>ðŸ“‹ Pedidos Activos (%d)</h2><div class='tabla-wrap'><table><thead><tr><th>#</th><th>Ficha</th><th>Cliente</th><th>Artículos</th><th>Total</th><th>Estado</th><th>Acciones</th></tr></thead><tbody>%s</tbody></table></div></div>" % (
        len(activos), filas_ped or '<tr><td colspan="8" style="text-align:center;padding:18px;color:#aaa">No hay pedidos activos.</td></tr>')
    html += "</div>"

    aprobados_peds = [p for p in peds if p["estado"] in ("Aprobado","Pagado")]
    filas_enc = ""; modales_enc = ""
    para p en ordenado(aprobados_peds, clave=lambda x: x["id"]):
        mid_enc = "enc_%d" % p["id"]
        tk_enc = hacer_ticket(p, admin=True)
        it_enc = tabla_items(p["items"] o "[]")
        modales_enc += """
<div class="superposición" id="%s">
  <div class="modal ancho">
    <button class="modal-x" onclick="cerrarModal('%s')">âœ•</button>
    <div class="modal-titulo">ðŸ“¦ Encarga #%d</div>
    <div style="font-size:.82rem;color:#888;margin-bottom:11px">ðŸ'¤ <strong>%s</strong> · ðŸ“± %s</div>
    %s%s
    <button class="btn btn-mo btn-full" style="margin-top:12px" onclick="imprimirTicket('%s')">ðŸ–¨ï¸ Imprimir</button>
  </div>
</div>""" % (mid_enc, mid_enc, p["id"], p["nombre_cliente"], p["celular"], it_enc, tk_enc, mid_enc)
        si p["estado"] == "Aprobado":
            est_badge = '<span class="bdg bdg-c">âœ… Aprobado</span>'
            btns_enc = ("<a href='/admin/marcar-pagado/%d' class='btn btn-ve' style='font-size:.8rem;padding:5px 12px'>ðŸ'μ Pagado</a>"
                         "<a href='/admin/marcar-nopago/%d' class='btn btn-ro' style='font-size:.8rem;padding:5px 12px'>â Œ No Pagado</a>") % (p["id"], p["id"])
        demás:
            est_badge = '<span class="bdg bdg-c">ðŸ'µ Pagado</span>'
            btns_enc = ""
        filas_enc += ("<tr><td><strong>#%d</strong></td><td><span class='ped-ficha'>%s</span></td>"
            "<td><strong>%s</strong><br><span style='font-size:.73rem;color:#888'>ðŸ“± %s</span></td>"
            "<td style='color:var(--mo);font-weight:900'>%s</td><td>%s</td>"
            "<td style='color:#c8a415;font-size:.8rem'>%s</td>"
            "<td style='display:flex;gap:5px;flex-wrap:wrap'>"
            "<button class='btn btn-az' style='font-size:.76rem;padding:4px 9px' onclick=\"abrirModal('%s')\">ðŸ“‹</button>%s"
            "</td></tr>") % (p["id"], p["ficha"] o "—", p["nombre_cliente"], p["celular"],
                             fmt(p["total"]), est_badge, p["fecha"], mid_enc, btns_enc)
    html += ("<div id='tab_encargos' style='display:none'><div class='panel'><h2>ðŸ“¦ Encargos (%d)</h2>"
             "<div class='tabla-wrap'><tabla><thead><tr>"
             "<th>#</th><th>Ficha</th><th>Cliente</th><th>Total</th><th>Estado</th><th>Fecha</th><th>Acciones</th>"
             "</tr></thead><tbody>%s</tbody></table></div></div></div>") % (
        len(aprobados_peds),
        filas_enc or "<tr><td colspan='7' style='text-align:center;padding:18px;color:#c8a415'>No hay encargos aún.</td></tr>")
    html += modales_enc

    html += "<div id='tab_productos' style='display:none'>"
    html += "<div clase='ag'>"
    html += "<div class='panel'><h2>âž• Agregar producto</h2><form method='POST' action='/admin/add-prod' enctype='multipart/form-data'>"
    html += "<div class='fg'><label>Nombre *</label><input type='text' name='nombre' required placeholder='Mango, Piña...'></div>"
    html += "<div style='display:grid;grid-template-columns:1fr 1fr;gap:10px'>"
    html += "<div class='fg'><label>Precio (€) *</label><input type='number' name='precio' required min='0' step='50'></div>"
    html += "<div class='fg'><label>Categoría</label><select name='categoria'>%s</select></div>" % cats_opts
    html += "<div class='fg'><lab el>Unidad</label><input type='text' name='unidad' placeholder='kg, unidad, racimo, caja'></div>"
    html += "</div>"
    html += "<div class='fg'><label>Descripción</label><textarea name='descripcion' placeholder='Describe la fruta...'></textarea></div>"
    html += "<div class='fg'><label>Imagen</label><input type='file' name='imagen' accept='image/*'></div>"
    html += "<button type='submit' class='btn btn-ve btn-full'>âœ… Agregar</button></form></div>"
    html += "<div class='panel'><h2>ðŸ Š Catálogo</h2><div class='tabla-wrap'><table><thead><tr><th>Producto</th><th>Categoría</th><th>Precio</th><th>Acciones</th></tr></thead><tbody>%s</tbody></table></div></div>" % (
        filas_prod or '<tr><td colspan="4" style="text-align:center;padding:18px;color:#aaa">Sin productos.</td></tr>')
    html += "</div></div>"

    html += "<div id='tab_config' style='display:none'>" + tab_config + "</div>"
    html += "<div id='tab_stats' style='display:none'><div class='panel'><h2>ðŸ“Š Estadísticas</h2>"
    html += "<div style='text-align:center;margin-bottom:14px'><a href='/admin/grafica' class='btn btn-mo'>ðŸ“ˆ Generar Gráfica</a></div>"
    html += graf_html + "</div></div>"
    html += "</div>"
    html += modales_ped + modales_prod
    html += PIE + JS_CARRITO + "</body></html>"
    devolver html


@app.route("/admin/login", métodos=["GET","POST"])
definición admin_login():
    err = ""
    si solicitud.metodo == "POST":
        pw = solicitud.formulario.get("contraseña","")
        si pw == MASTER_PASS:
            sesión["admin"] = Verdadero; sesión["master"] = Verdadero
            retorno redirección(url_para("panel_de_administración"))
        elif pw == CONTRASEÑA DE ADMINISTRADOR:
            sesión["admin"] = Verdadero; sesión["master"] = Falso
            retorno redirección(url_para("panel_de_administración"))
        err = "â Œ Contraseña incorrecta."
    devolver nav("admin_panel") + """
<div class="caja de inicio de sesión">
  <h2>ðŸ Š Administrador del panel</h2>
  %s
  <form método="POST">
    <div class="fg"><label>Contraseña</label>
      <input type="password" name="password" placeholder="â€¢â€¢â€¢â€¢â€¢â€¢â€¢â€¢" enfoque automático requerido></div>
    <button type="submit" class="btn btn-mo btn-full">ðŸ Š Ingresar</button>
  </form>
</div>""" % alerta(err,"er") + PIE + JS_CARRITO + "</body></html>"


@app.route("/admin/cerrar sesión")
def admin_logout():
    sesión.clear()
    retorno redirección(url_para("tienda"))


@app.route("/admin/alternar")
definición admin_toggle():
    si no es session.get("admin"): devuelve redirección(url_for("admin_login"))
    db = obtener_db()
    r = db.execute("SELECT valor FROM configuracion WHERE clave='activo'").fetchone()
    nuevo = "0" si (r y r["valor"]=="1") de lo contrario "1"
    db.execute("INSERT OR REPLACE INTO configuracion VALUES('activo',?)",(nuevo,))
    db.commit(); db.close()
    msg = "âœ… Mercado abierto." if nuevo=="1" else "ðŸ”' Mercado cerrado."
    devolver redirección(url_para("panel_de_administración", msg=msg, tipo="ok"))


@app.route("/admin/config", métodos=["POST"])
definición admin_config():
    si no es session.get("admin"): devuelve redirección(url_for("admin_login"))
    nombre = request.form.get("nombre","").strip() o "Mercado Frutas Frescas"
    db = obtener_db()
    db.execute("INSERT OR REPLACE INTO configuracion VALUES('nombre',?)",(nombre,))
    Si hay "logotipo" en request.files:
        f = solicitud.archivos["logotipo"]
        si f y f.nombre_archivo:
            crudo = f.read()
            si len(raw) < 2_000_000:
                db.execute("INSERTAR O REEMPLAZAR EN los valores de configuración('logo',?)",
                           (base64.b64encode(raw).decode(),))
    db.commit(); db.close()
    return redirección(url_for("admin_panel", msg="âœ… Configuración guardada.", tipo="ok"))


@app.route("/admin/add-prod", métodos=["POST"])
definición admin_add_prod():
    si no es session.get("admin"): devuelve redirección(url_for("admin_login"))
    f = solicitud.formulario; img = Ninguno
    si "imagen" está en request.files:
        fi = solicitud.archivos["imagen"]
        si fi y fi.filename:
            raw = fi.read()
            mime = fi.mimetype o "imagen/jpeg"
            si no mime.startswith("image/"): mime = "image/jpeg"
            si len(raw) < 5_000_000: img = mime + ";" + base64.b64encode(raw).decode()
    db = obtener_db()
    db.execute("INSERT INTO productos(nombre,precio,descripcion,unidad,categoria,imagen) VALUES(?,?,?,?,?,?)",
               (f["nombre"].strip(), float(f["precio"]),
                f.get("descripcion","").strip(),
                f.get("unidad","unidad").strip(),
                f.get("categoria","Frutas"), img))
    db.commit(); db.close()
    return redirección(url_for("admin_panel", msg="âœ… Producto agregado.", tipo="ok"))


@app.route("/admin/edit-prod", métodos=["POST"])
definición admin_edit_prod():
    si no es session.get("admin"): devuelve redirección(url_for("admin_login"))
    f = solicitud.formulario
    db = obtener_db()
    db.execute("ACTUALIZAR productos SET nombre=?,precio=?,descripcion=?,unidad=?,categoria=? WHERE id=?",
               (f["nombre"].strip(), float(f["precio"]),
                f.get("descripcion","").strip(),
                f.get("unidad","unidad").strip(),
                f.get("categoría","Frutas"), f["pid"]))
    db.commit(); db.close()
    return redirección(url_for("admin_panel", msg="âœ… Producto actualizado.", tipo="ok"))


@app.route("/admin/del-prod/<int:pid>")
definición admin_del_prod(pid):
    si no es session.get("admin"): devuelve redirección(url_for("admin_login"))
    db = obtener_db()
    db.execute("ELIMINAR DE productos DONDE id=?",(pid,))
    db.commit(); db.close()
    return redirección(url_for("admin_panel", msg="ðŸ—'ï¸ Producto eliminado.", tipo="ok"))


@app.route("/admin/upd-pedido", métodos=["POST"])
def admin_upd_pedido():
    si no es session.get("admin"): devuelve redirección(url_for("admin_login"))
    f = solicitud.formulario
    pid = f["pedido_id"]
    est = f["estado"]
    motivo = f.get("motivo","").strip()
    db = obtener_db()
    db.execute("ACTUALIZAR pedidos SET estado=?,motivo=? WHERE id=?", (est,motivo,pid))
    db.commit(); db.close()
    if est == "Aprobado": msg = "âœ… Pedido #%s aprobado." % pid
    elif est == "Negado": msg = "â Œ Pedido #%s negado." % pid
    else: msg = "â ³ Pedido #%s pendiente." % pid
    devolver redirección(url_para("panel_de_administración", msg=msg, tipo="ok"))


@app.route("/admin/grafica")
def admin_grafica():
    si no es session.get("admin"): devuelve redirección(url_for("admin_login"))
    db = obtener_db()
    peds = db.execute("SELECT * FROM pedidos").fetchall()
    productos = db.execute("SELECT * FROM productos ORDER BY id DESC").fetchall()
    db.close()
    ventas = {}
    para p en peds:
        intentar:
            para ello en json.loads(p["items"]):
                ventas[it["nombre"]] = ventas.get(it["nombre"],0) + int(it["qty"])
        excepto: pasar
    si no ventas:
        return redirección(url_for("admin_panel", msg="No hay datos para graficar.", tipo="in"))
    nombres = lista(ventas.keys())
    cants = [ventas[n] para n en noms]
    cols = ["#cc0000","#ff2222","#cc0000","#ff4444","#9333ea","#a855f7","#c084fc","#d97706","#fbbf24","#e9d5ff"][:len(noms)]
    fig, (ax1,ax2) = plt.subplots(1,2,figsize=(13,5))
    fig.patch.set_facecolor("#f5f0ff")
    ax1.set_facecolor("#fdf8ff")
    barras = ax1.bar(rango(len(noms)), peraltes, color=cols, edgecolor="#440000", ancho de línea=1.5)
    ax1.set_xticks(rango(longitud(nombres)))
    ax1.set_xticklabels([n[:12] para n en noms], rotación=28, ha="derecha", color="#1a0033", tamaño de fuente=9)
    ax1.set_title("Frutas más pedidas", color="#cc0000", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Unidades", color="#8a6aaa")
    para sp en ax1.spines.values(): sp.set_color("#440000")
    para b,v en zip(barras,cantos):
        ax1.text(b.get_x()+b.get_width()/2, b.get_height()+.05, str(v), ha="centro", color="#cc0000", tamaño de fuente=10, peso de fuente="negrita")
    ax2.set_facecolor("#fdf8ff")
    cuñas,textos,autotextos = ax2.pie(cantidades, colores=columnas, autopct="%1.1f%%", ángulo de inicio=90,
                                      distancia del pct=.8, propiedades de cuña={"color del borde":"#f5f0ff","ancho de línea":2})
    para t en textos: t.set_color("#1a0033")
    para t en autotextos: t.set_color("blanco"); t.set_fontweight("negrita")
    ax2.set_title("Distribución", color="#cc0000", fontsize=12, fontweight="bold")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, formato="png", bbox_inches="ajustado", color de la cara="#f5f0ff", dpi=110)
    buf.seek(0)
    g64 = base64.b64encode(buf.read()).decode()
    plt.close()
    db2 = obtener_db()
    peds2 = db2.execute("SELECT * FROM pedidos ORDER BY id DESC").fetchall()
    prods2= db2.execute("SELECT * FROM productos ORDER BY id DESC").fetchall()
    db2.close()
    devolver render_admin(peds2, prods2, g64)


# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
# RUTA: ENCARGOS DEL DÍA
# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
@app.route("/admin/encargos")
def admin_encargos():
    si no es session.get("admin"): devuelve redirección(url_for("admin_login"))
    c = cfg()
    nom = c.get("nombre","Mercado Frutas Frescas")
    db = obtener_db()
    peds = db.execute("SELECT * FROM pedidos WHERE estado NOT IN ('Negado','Cancelado') ORDER BY id ASC").fetchall()
    db.close()
    hoy = datetime.now().strftime("%d/%m/%Y")
    total_dia = suma(p["total"] para p en peds)

    def hacer_bloque(p):
        prueba: items = json.loads(p["items"])
        excepto: elementos = []
        filas = ""
        para ello en artículos:
            sub = float(it["precio"]) * int(it["cantidad"])
            filas += """<tr>
  <td style="padding:3px 8px;font-size:.74rem;border-bottom:1px solid #ddd">%s</td>
  <td style="padding:3px 8px;font-size:.74rem;text-align:center;border-bottom:1px solid #ddd">%d %s</td>
  %s
</tr>""" % (it["nombre"][:18], it["qty"], it.get("unidad",""), fmt(sub))
        notas = ('<div style="font-size:.68rem;color:#555;padding:3px 8px;font-style:italic">ðŸ“ %s</div>' % p["notas"]) if p["notas"] else ""
        devolver """<div style="border:2px solid #222;border-radius:16px;overflow:hidden;background:#fff;height:100%%">
  <div style="fondo:#111;relleno:8px 12px;alineación del texto:centro;radio del borde:14px 14px 0 0">
    <div style="font-size:.85rem;font-weight:900;color:#fff">ðŸŠ %s</div>
    <div style="font-size:.65rem;color:#ccc;margin-top:1px">ENCARGOS DEL DÍA — %s</div>
  </div>
  <div style="fondo:#f5f5f5;relleno:5px 12px;pantalla:flexible;justificar-contenido:espacio-entre;alinear-elementos:centro;borde-inferior:1px sólido #ddd">
    <strong style="color:#111;font-size:.8rem">Pedido #%d</strong>
    <span style="background:#222;color:#fff;border-radius:20px;padding:1px 9px;font-size:.65rem;font-weight:900">Ficha: %s</span>
  </div>
  <div style="padding:5px 12px;border-bottom:1px solid #eee;font-size:.76rem;color:#111">
    <div><strong>%s</strong> ðŸ“± %s</div>
    <div style="color:#666;font-size:.68rem">%s · %s</div>
  </div>
  <div style="padding:0 0 4px 0">
    <div style="padding:4px 12px;background:#f0f0f0;font-size:.68rem;font-weight:900;color:#333;text-transform:uppercase;letter-spacing:.5px;border-bottom:1px solid #ddd">Productos</div>
    <table style="width:100%%;border-collapse:collapse;color:#111">
      <thead><tr>
        <th style="padding:3px 8px;text-align:left;font-size:.68rem;color:#666;font-weight:700;border-bottom:1px solid #ddd">Producto</th>
        <th style="padding:3px 8px;text-align:center;font-size:.68rem;color:#666;font-weight:700;border-bottom:1px solid #ddd">No se puede.</th>
        Subtotal
      </tr></thead>
      %s
    </tabla>
    %s
  </div>
  <div style="padding:7px 12px;background:#111;border-radius:0 0 14px 14px;display:flex;justify-content:space-between;align-items:center">
    <span style="font-size:.7rem;color:#aaa">ðŸ'µ Pago al recoger</span>
    <strong style="color:#fff;font-size:.95rem">%s</strong>
  </div>
</div>""" % (nombre, hoy,
             p["id"], p["ficha"] o "â€”",
             p["nombre_cliente"], p["celular"],
             p["fecha"], p["estado"],
             filas, notas, fmt(p["total"]))

    filas_de_la_cuadrícula = ""
    para i en rango(0, len(peds), 2):
        b1 = hacer_bloque(peds[i])
        b2 = hacer_bloque(peds[i+1]) si i+1 < len(peds) de lo contrario "<div></div>"
        filas_de_cuadrícula += """<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px;page-break-inside:avoid">
  %s
  %s
</div>""" % (b1, b2)

    si no son peatones:
        grid_rows = '<div style="text-align:center;padding:40px;color:#aaa"><div style="font-size:3rem">ðŸ“‹</div><p>No hay encargos hoy.</p></div>'
        total_html = ""
    demás:
        total_html = """<div style="fondo:#111;radio del borde:12px;relleno:14px 20px;margen superior:12px;pantalla:flexible;justificar contenido:espacio entre;alinear elementos:centro;color:#fff;borde:2px sólido #333">
  <div><div style="font-weight:900;font-size:.95rem">ðŸ“¦ TOTAL DEL DÍA</div><div style="font-size:.75rem;color:#aaa">%d encargo(s)</div></div>
  <div style="font-size:1.5rem;font-weight:900">%s</div>
</div>""" % (len(peds), fmt(total_dia))

    devolver """<!DOCTYPE html>
<html lang="es">
<cabeza>
<meta charset="UTF-8">
<meta name="viewport" content="ancho=ancho-del-dispositivo,escala-inicial=1.0">
<title>Encargos — %s</title>
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800;900&display=swap" rel="hoja de estilo">
<estilo>
*{tamaño de la caja:border-box;margen:0;relleno:0}
cuerpo{font-family:'Nunito',sans-serif;fondo:#0a0a0a;color:#f0f0f0;relleno:16px}
.wrap{ancho máximo: 860 px; margen: 0 automático}
.top-bar{fondo:#111;radio del borde:12px;relleno:16px 20px;alineación del texto:centro;margen inferior:16px;borde:2px sólido #333}
.barra superior h1{tamaño de fuente: 1.3rem;peso de fuente: 900;color: #fff}
.barra superior p{color:#aaa;tamaño de fuente:.82rem;margen superior:3px}
.acciones{display:flex;gap:10px;justify-content:center;margin-bottom:16px}
.btn-dl{fondo:#222;color:#fff;borde:2px sólido #555;radio del borde:8px;relleno:11px 28px;tamaño de fuente:.95rem;peso de fuente:900;cursor:puntero;familia de fuentes:'Nunito',sans-serif;decoración de texto:ninguna;mostrar:bloque en línea}
.btn-dl:hover{fondo:#333}
.btn-back{fondo:transparente;color:#aaa;borde:2px sólido #333;radio del borde:8px;relleno:11px 20px;tamaño de fuente:.95rem;peso de fuente:900;decoración de texto:ninguna;mostrar:bloque en línea}
@media print{
  .acciones{display:ninguno!importante}
  cuerpo{fondo:#fff!importante;relleno:6px;color:#000}
  @page{tamaño:A4;margen:8mm}
}
</estilo>
</cabeza>
<cuerpo>
<div class="wrap">
  <div class="barra superior">
    <h1>ðŸ Š %s — Encargos del Día</h1>
    <p>%s  Â·  %d pedido(s)  Â·  Total: %s</p>
  </div>
  <div class="acciones">
    <a href="/admin/descargar-encargos" class="btn-dl">â¬‡ï¸ Descargar PDF</a>
    <a href="/admin" class="btn-back">â† Volver</a>
  </div>
  %s
  %s
</div>
</cuerpo>
</html>""" % (nombre, nombre, hoy, longitud(peatones), frecuencia(diámetro_total), filas_de_la_cuadrícula, total_html)


@app.route("/reset-frutas-2024")
definición reset_ver():
    db = obtener_db()
    total = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    ingr = db.execute("SELECT SUM(total) FROM pedidos WHERE estado!='Cancelado'").fetchone()[0] o 0
    env = db.execute("SELECT COUNT(*) FROM pedidos WHERE estado='Enviado'").fetchone()[0]
    db.close()
    devolver """<!DOCTYPE html><html lang='es'><head><meta charset='UTF-8'>
<meta name='viewport' content='width=ancho-del-dispositivo,escala-inicial=1.0'>
<title>Restablecer</title>
<link href='https://fonts.googleapis.com/css2?family=Nunito:wght@700;800;900&display=swap' rel='hoja de estilo'>
<style>*{tamaño de la caja:border-box;margen:0;relleno:0}
cuerpo{font-family:'Nunito',sans-serif;fondo:#f5f0ff;altura mínima:100vh;
  pantalla:flexible;alinear elementos:centrar;justificar contenido:centrar;relleno:20px}
.box{fondo:#1a1a1a;borde:3px sólido #cc0000;radio del borde:12px;relleno:38px;
  ancho máximo: 440 px; ancho: 100 %%; alineación del texto: centro; sombra del cuadro: 0 8 px 36 px rgba (180, 0, 0, .18)}
h1{color:#dc2626;tamaño de fuente:1.9rem;margen inferior:6px}
.sub{color:#888;tamaño de fuente:.83rem;margen inferior:22px}
.fila{display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid #440000}
.val{color:#cc0000;peso de fuente:900}
.total{display:flex;justify-content:space-between;padding:13px 0;font-size:1.1rem;font-weight:900}
.verde{color:#cc0000;tamaño de fuente:1.15rem}
.warn{fondo:#fef9c3;borde:2px sólido #ca8a04;radio del borde:8px;relleno:13px;margen:18px 0;color:#92400e;peso de la fuente:800;tamaño de la fuente:.86rem}
.btns{display:flex;gap:11px;margin-top:18px}
.b-del{flex:1;fondo:gradiente-lineal(135deg,#dc2626,#ef4444);color:#fff;relleno:12px;radio-del-borde:8px;decoración-del-texto:ninguna;peso-de-fuente:900;tamaño-de-fuente:.96rem}
.b-can{flex:1;fondo:#f5f0ff;color:#1a0033;relleno:12px;radio del borde:8px;decoración del texto:ninguna;peso de la fuente:900;tamaño de la fuente:.96rem;borde:2px sólido #440000}
.fecha{color:#aaa;font-size:.73rem;margin-top:13px}</style></head><body>
<div class='caja'>
  <div style='font-size:3.5rem;margin-bottom:14px'>âšï¸ </div>
  <h1>Restablecer mes</h1>
  <p class='sub'>Resumen antes de eliminar</p>
  <div class='fila'><span>ðŸ“¦ Pedidos totales</span><span class='val'>%d</span></div>
  <div class='fila'><span>ðŸšš Enviados</span><span class='val'>%d</span></div>
  <div class='total'><span>ðŸ'° Ingresos del mes</span><span class='verde'>%s</span></div>
  <div class='warn'>âš ï¸ Esta acción borrará TODOS los pedidos. No se puede deshacer.</div>
  <div clase='btns'>
    <a href='/reset-frutas-2024/ok' class='b-del'>ðŸ—'ï¸ ELIMINAR TODO</a>
    <a href='/admin' class='b-can'>âœ• Cancelar</a>
  </div>
  <p class='fecha'>%s</p>
</div></body></html>""" % (total, env, fmt(ingr), datetime.now().strftime("%d/%m/%Y %H:%M"))


@app.route("/reset-frutas-2024/ok")
definición reset_ok():
    db = obtener_db()
    total = db.execute("SELECT COUNT(*) FROM pedidos WHERE estado IN ('Pendiente','Negado','Pagado','En Espera','Cancelado')").fetchone()[0]
    ingr = db.execute("SELECT SUM(total) FROM pedidos WHERE estado='Pagado'").fetchone()[0] o 0
    db.execute("BORRAR DE pedidos DONDE estado IN ('Pendiente','Negado','Pagado','En Espera','Cancelado')")
    db.commit(); db.close()
    devolver """<!DOCTYPE html><html lang='es'><head><meta charset='UTF-8'>
<meta name='viewport' content='width=ancho-del-dispositivo,escala-inicial=1.0'>
<title>Restablecer OK</title>
<link href='https://fonts.googleapis.com/css2?family=Nunito:wght@700;800;900&display=swap' rel='hoja de estilo'>
<style>*{tamaño de la caja:border-box;margen:0;relleno:0}
cuerpo{font-family:'Nunito',sans-serif;fondo:#f5f0ff;altura mínima:100vh;
  pantalla:flexible;alinear elementos:centrar;justificar contenido:centrar;relleno:20px}
.box{fondo:#1a1a1a;borde:3px sólido #16a34a;radio del borde:12px;relleno:38px;
  ancho máximo: 440 px; ancho: 100 %%; alineación del texto: centro; sombra del cuadro: 0 8 px 36 px rgba (22,163,74,.15)}
h1{color:#16a34a;tamaño de fuente:1.9rem;margen inferior:6px}
.sub{color:#888;tamaño de fuente:.83rem;margen inferior:22px}
.fila{display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid #440000}
.val{color:#cc0000;peso de fuente:900}
.ok-box{fondo:#dcfce7;borde:2px sólido #16a34a;radio del borde:8px;relleno:13px;margen:18px 0;color:#f5c518;peso de la fuente:900}
a{display:inline-block;margin-top:18px;background:linear-gradient(135deg,#cc0000,#ff2222);
  color: #fff; relleno: 12px 28px; radio del borde: 8px; decoración del texto: ninguna; peso de la fuente: 900}
.fecha{color:#aaa;font-size:.73rem;margin-top:13px}</style></head><body>
<div class='caja'>
  <div style='font-size:3.5rem;margin-bottom:14px'>…</div>
  ¡Reinicio completo!
  <p class='sub'>El mes fue cerrado exitosamente</p>
  <div class='fila'><span>ðŸ“¦ Pedidos eliminados</span><span class='val'>%d</span></div>
  <div class='fila'><span>ðŸ'° Ingresos del mes</span><span class='val'>%s</span></div>
  <div class='ok-box'>âœ… Base de datos limpia — Nuevo mes comenzado</div>
  <a href='/admin'>Administrador del panel Ir al</a>
  <p class='fecha'>%s</p>
</div></body></html>""" % (total, fmt(ingr), datetime.now().strftime("%d/%m/%Y %H:%M"))


@app.route("/admin/descargar-encargos")
def descargar_encargos():
    si no es session.get("admin"): devuelve redirección(url_for("admin_login"))
    c = cfg()
    nom = c.get("nombre","Mercado Frutas Frescas")
    db = obtener_db()
    peds = db.execute("SELECT * FROM pedidos WHERE estado NOT IN ('Negado','Cancelado') ORDER BY id ASC").fetchall()
    db.close()
    hoy = datetime.now().strftime("%d/%m/%Y")
    total_dia = suma(p["total"] para p en peds)

    def bloque_pdf(p):
        prueba: items = json.loads(p["items"])
        excepto: elementos = []
        filas = ""
        para ello en artículos:
            sub = float(it["precio"]) * int(it["cantidad"])
            filas += "<tr><td estilo='padding:2px 6px;tamaño de fuente:8pt;border-bottom:1px sólido #ddd'>%s</td><td estilo='padding:2px 6px;tamaño de fuente:8pt;alineación del texto:centro;border-bottom:1px sólido #ddd'>%d %s</td><td estilo='padding:2px 6px;tamaño de fuente:8pt;alineación del texto:derecha;peso de fuente:bold;border-bottom:1px sólido #ddd'>%s</td></tr>" % (
                it["nombre"][:18], it["cantidad"], it.get("unidad",""), fmt(sub))
        notas = ('<p style="font-size:7pt;color:#555;padding:2px 6px;font-style:italic">ðŸ“ %s</p>' % p["notas"]) if p["notas"] else ""
        devolver """<div style="border:2px solid #222;border-radius:14px;overflow:hidden;background:#fff;display:flex;flex-direction:column">
  <div style="fondo:#111;relleno:7px 10px;alineación del texto:centro;radio del borde:12px 12px 0 0">
    <div style="font-size:9pt;font-weight:900;color:#fff">ðŸŠ %s</div>
    <div style="font-size:7pt;color:#ccc">ENCARGOS DEL DÍA — %s</div>
  </div>
  <div style="fondo:#f5f5f5;relleno:4px 10px;pantalla:flexible;justificar-contenido:espacio-entre;borde-inferior:1px sólido #ddd">
    <strong style="font-size:8pt">Pedido #%d</strong>
    <span style="background:#222;color:#fff;border-radius:10px;padding:1px 7px;font-size:7pt;font-weight:bold">Ficha: %s</span>
  </div>
  <div style="padding:4px 10px;border-bottom:1px solid #eee;font-size:8pt">
    <strong>%s</strong> · ðŸ“± %s<br>
    <span style="font-size:7pt;color:#666">%s · %s</span>
  </div>
  <div style="background:#f0f0f0;padding:3px 10px;font-size:7pt;font-weight:bold;color:#333;text-transform:uppercase;border-bottom:1px solid #ddd">Productos</div>
  <table style="width:100%%;border-collapse:collapse">
    <thead><tr>
      <th style="padding:2px 6px;text-align:left;font-size:7pt;color:#666;border-bottom:1px solid #ddd">Producto</th>
      <th style="padding:2px 6px;text-align:center;font-size:7pt;color:#666;border-bottom:1px solid #ddd">No se puede.</th>
      Total
    </tr></thead>
    %s
  </tabla>
  %s
  <div style="flex:1"></div>
  <div style="padding:5px 10px;background:#111;border-radius:0 0 12px 12px;display:flex;justify-content:space-between;align-items:center">
    <span style="font-size:7pt;color:#aaa">ðŸ'µ Pago al recoger</span>
    %s
  </div>
</div>""" % (nom, hoy, p["id"], p["ficha"] o "—",
             p["nombre_cliente"], p["celular"],
             p["fecha"], p["estado"],
             filas, notas, fmt(p["total"]))

    filas_de_la_cuadrícula = ""
    para i en rango(0, len(peds), 2):
        b1 = bloque_pdf(peds[i])
        b2 = bloque_pdf(peds[i+1]) si i+1 < len(peds) de lo contrario "<div></div>"
        filas_de_cuadrícula += """<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;page-break-inside:avoid">
  %s %s
</div>""" % (b1, b2)

    total_html = ""
    si peatones:
        total_html = "<div style='background:#111;border-radius:10px;padding:12px 16px;margin-top:10px;display:flex;justify-content:space-between;color:#fff'><div><strong>ðŸ“¦ TOTAL DEL DÍA</strong><div style='font-size:8pt;color:#aaa'>%d encargo(s)</div></div><strong style='font-size:14pt'>%s</strong></div>" % (len(peds), fmt(total_dia))

    html = """<!DOCTYPE html>
<html lang="es">
<cabeza>
<meta charset="UTF-8">
<title>Encargos %s</title>
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800;900&display=swap" rel="hoja de estilo">
<estilo>
*{tamaño de la caja: borde-caja; margen: 0; relleno: 0; familia de fuentes: 'Nunito', sans-serif}
cuerpo{fondo:#fff;color:#111;relleno:8px}
@page{tamaño:A4;margen:8mm}
@media screen{body{fondo:#f0f0f0;relleno:20px}.wrap{fondo:#fff;ancho máximo:860px;margen:0 automático;relleno:16px;radio del borde:12px}}
</estilo>
</cabeza>
<cuerpo>
<div class="wrap">
  <div style="text-align:center;border-bottom:2px solid #111;padding-bottom:10px;margin-bottom:14px">
    <h1 style="font-size:14pt;font-weight:900">ðŸ Š %s — Encargos del Día</h1>
    <p style="font-size:9pt;color:#555">%s · %d pedido(s) · Total: %s</p>
  </div>
  %s%s
</div>
<script>ventana.onload=función(){ventana.imprimir()}</script>
</cuerpo>
</html>""" % (nombre, nombre, hoy, longitud(peatones), frecuencia(diámetro_total), filas_de_la_cuadrícula, total_html)
    devolver html


# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
# MARCAR PAGADO
# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
@app.route("/admin/marcar-pagado/<int:pid>")
def marcar_pagado(pid):
    si no es session.get("admin"): devuelve redirección(url_for("admin_login"))
    db = obtener_db()
    db.execute("ACTUALIZAR pedidos SET estado='Pagado' WHERE id=?", (pid,))
    db.commit(); db.close()
    return redirección(url_for("admin_panel", msg="ðŸ'μ Pedido #%d marcado como pagado." % pid, tipo="ok"))


@app.route("/admin/marcar-nopago/<int:pid>")
def marcar_nopago(pid):
    si no es session.get("admin"): devuelve redirección(url_for("admin_login"))
    db = obtener_db()
    db.execute("ACTUALIZAR pedidos SET estado='Aprobado' WHERE id=?", (pid,))
    db.commit(); db.close()
    return redirección(url_for("admin_panel", msg="â†©ï¸ Pedido #%d marcado como No Pagado." % pid, tipo="in"))


# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
# COMPRAS / GASTOS
# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
@app.route("/admin/compras", métodos=["GET","POST"])
definición admin_compras():
    si no es session.get("admin"): devuelve redirección(url_for("admin_login"))
    c = cfg()
    nom = c.get("nombre","Mercado Frutas Frescas")
    mensaje = ""
    si solicitud.metodo == "POST":
        acción = request.form.get("acción","")
        si accion == "agregar":
            db = obtener_db()
            db.execute("INSERT INTO compras(producto,cantidad,costo,fecha,notas) VALUES(?,?,?,?,?)", (
                solicitud.formulario.get("producto","").strip(),
                solicitud.formulario.get("cantidad","").strip(),
                float(solicitud.formulario.get("costo",0)),
                datetime.now().strftime("%d/%m/%Y"),
                solicitud.formulario.get("notas","").strip()
            ))
            db.commit(); db.close()
            msg = "âœ… Compra registrada."
        elif accion == "eliminar":
            pid2 = solicitud.formulario.get("id")
            db = obtener_db()
            db.execute("BORRAR DE compras DONDE id=?", (pid2,))
            db.commit(); db.close()
            msg = "ðŸ—'ï¸ Registro eliminado."

    db = obtener_db()
    compras = db.execute("SELECT * FROM compras ORDER BY id DESC").fetchall()
    ventas = db.execute("SELECT SUM(total) FROM pedidos WHERE estado='Pagado'").fetchone()[0] o 0
    db.close()

    total_gastos = suma(c2["costo"] for c2 en compras)
    ganancia = ventas - total_gastos

    filas = ""
    para c2 en compras:
        filas += """<tr>
  <td><strong>%s</strong></td>
  %s
  %s
  %s
  %s
  <td>
    <form método="POST" estilo="display:inline">
      <input type="hidden" name="accion" value="eliminar">
      <input tipo="oculto" nombre="id" valor="%d">
      <button type="submit" class="btn btn-ro" style="font-size:.75rem;padding:3px 9px" onclick="return confirm('¿Eliminar?')">ðŸ—'ï¸ </button>
    </form>
  </td>
</tr>""" % (c2["producto"], c2["cantidad"], fmt(c2["costo"]),
             c2["fecha"], c2["notas"] o "—", c2["id"])

    gan_color = "#22c55e" si ganancia >= 0 else "#ef4444"
    gan_ico = "ðŸ“ˆ" si ganancia >= 0 else "ðŸ“‰"
    alerta_html = '<div class="alerta alerta-ok">%s</div>' % msg if msg else ""

    devolver nav("admin_panel", c) + """
<div class="wrap">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;flex-wrap:wrap;gap:10px">
    <h1 style="font-size:1.7rem;font-weight:900;color:#f5c518">ðŸ“¦ Gastos y Ganancias</h1>
    <a href="/admin" class="btn btn-ro">â† Volver al Administrador</a>
  </div>
  %s
  <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-bottom:20px">
    <div class="stat">
      <div class="stat-n">%s</div>
      <div class="stat-l">ðŸ'° Total Vendido (Pagado)</div>
    </div>
    <div class="stat">
      <div class="stat-n" style="color:#ef4444">%s</div>
      <div class="stat-l">ðŸ›' Total Gastado en Compras</div>
    </div>
    <div clase="stat" estilo="color-superior-del-borde:%s">
      <div class="stat-n" style="color:%s">%s %s</div>
      <div class="stat-l">%s Ganancia Neta</div>
    </div>
  </div>
  <div class="panel" style="ancho máximo: 600px; margen inferior: 20px">
    <h2>âž• Registrar Compra</h2>
    <form método="POST">
      <input type="hidden" name="accion" value="agregar">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
        <div class="fg"><label>Producto *</label>
          <input type="text" name="producto" required placeholder="Ej: Cajilla de mangos"></div>
        <div class="fg"><label>Cantidad *</label>
          <input type="text" name="cantidad" required placeholder="Ej: 3 cajillas, 10 kg"></div>
        <div class="fg"><label>Costo total (€) *</label>
          <input type="number" name="costo" required min="0" step="100" placeholder="0"></div>
        <div class="fg"><label>Notas</label>
          <input type="text" name="notas" placeholder="Proveedor, observaciones..."></div>
      </div>
      <button type="submit" class="btn btn-mo btn-full" style="margin-top:6px">ðŸ'¾ Guardar Compra</button>
    </form>
  </div>
  <div class="panel">
    <h2>ðŸ“‹ Historial de Compras (%d)</h2>
    <div class="tabla-wrap">
      <tabla>
        <thead><tr>
          <th>Producto</th><th>Cantidad</th><th>Costo</th><th>Fecha</th><th>Notas</th><th>Acción</th>
        </tr></thead>
        %s
      </tabla>
    </div>
  </div>
</div>
""" % (alerta_html,
       fmt(ventas), fmt(total_gastos),
       gan_color, gan_color, gan_ico, fmt(abs(ganancia)),
       gan_ico,
       len(compras), filas or '<tr><td colspan="6" style="text-align:center;padding:18px;color:#c8a415">Sin compras registradas.</td></tr>') + PIE + JS_CARRITO + "</body></html>"


# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
# INICIO
# â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â• â•
si __nombre__ == "__principal__":
    imprimir("\n" + "="*50)
    print(" ðŸ Š Mercado Frutas Frescas")
    imprimir("="*50)
    print("Tienda: http://localhost:5000")
    imprimir("Administrador: http://localhost:5000/admin")
    print("Pass: Admin2026$")
    print(" Maestro: Frutas$Master2006")
    print("Restablecer: http://localhost:5000/reset-frutas-2024")
    imprimir("="*50 + "\n")
    app.run(host="0.0.0.0", puerto=int(os.environ.get("PUERTO",5000)), depuración=Falso)
