"""
MercadoFrutas — pip install flask matplotlib pillow — python mercado.py
Admin: http://localhost:5000/admin
Pass admin: Admin2026$   Pass maestra: Frutas$Master2006
"""
from flask import Flask, request, redirect, url_for, session, Response
import sqlite3, base64, io, json, os
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = "mercado_frutas_2026!"
ADMIN_PASS  = "Admin2026$"
MASTER_PASS = "Frutas$Master2006"
DB = "mercado.db"

# ═══════════════════════════════════════════════════════
# BASE DE DATOS
# ═══════════════════════════════════════════════════════
def get_db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS productos(
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT NOT NULL,
            precio      REAL NOT NULL,
            descripcion TEXT DEFAULT '',
            unidad      TEXT DEFAULT 'unidad',
            categoria   TEXT DEFAULT 'Frutas',
            imagen      TEXT,
            activo      INTEGER DEFAULT 1
        )""")
    db.execute("""
        CREATE TABLE IF NOT EXISTS pedidos(
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_cliente TEXT NOT NULL,
            celular        TEXT NOT NULL,
            direccion      TEXT NOT NULL,
            barrio         TEXT DEFAULT '',
            referencia     TEXT DEFAULT '',
            notas          TEXT DEFAULT '',
            items          TEXT NOT NULL,
            subtotal       REAL NOT NULL,
            envio          REAL DEFAULT 0,
            total          REAL NOT NULL,
            estado         TEXT DEFAULT 'Pendiente',
            confirmacion   TEXT DEFAULT 'pendiente',
            hora_entrega   TEXT DEFAULT '',
            motivo         TEXT DEFAULT '',
            fecha          TEXT NOT NULL,
            ficha          TEXT DEFAULT ''
        )""")
    db.execute("""
        CREATE TABLE IF NOT EXISTS configuracion(
            clave TEXT PRIMARY KEY,
            valor TEXT
        )""")
    db.execute("INSERT OR IGNORE INTO configuracion VALUES('nombre','Mercado Frutas Frescas')")
    db.execute("INSERT OR IGNORE INTO configuracion VALUES('logo','')")
    db.execute("INSERT OR IGNORE INTO configuracion VALUES('activo','1')")
    db.execute("""CREATE TABLE IF NOT EXISTS compras(
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        producto TEXT NOT NULL,
        cantidad TEXT NOT NULL,
        costo    REAL NOT NULL,
        fecha    TEXT NOT NULL,
        notas    TEXT DEFAULT ''
    )""")
    # Productos demo
    if db.execute("SELECT COUNT(*) FROM productos").fetchone()[0] == 0:
        demos = [
            ("Mango",     800,  "Mango maduro dulce y jugoso",      "kg",     "Tropicales"),
            ("Piña",      1200, "Piña golden extra dulce",           "unidad", "Tropicales"),
            ("Banano",    600,  "Banano criollo maduro",             "racimo", "Frutas"),
            ("Papaya",    900,  "Papaya hawaiana dulce",             "kg",     "Tropicales"),
            ("Naranja",   700,  "Naranja para jugo o comer",         "kg",     "Cítricos"),
            ("Limón",     500,  "Limón ácido fresco",                "kg",     "Cítricos"),
            ("Sandía",    2500, "Sandía roja grande y dulce",        "unidad", "Frutas"),
            ("Fresa",     1100, "Fresas frescas del día",            "caja",   "Berries"),
            ("Uva Verde", 1800, "Uva verde sin semilla importada",   "kg",     "Berries"),
            ("Melón",     1500, "Melón cantalupo maduro",            "unidad", "Frutas"),
        ]
        for d in demos:
            db.execute("INSERT INTO productos(nombre,precio,descripcion,unidad,categoria) VALUES(?,?,?,?,?)", d)
    db.commit()
    db.close()

def cfg():
    db = get_db()
    rows = db.execute("SELECT clave,valor FROM configuracion").fetchall()
    db.close()
    return {r["clave"]: r["valor"] for r in rows}

def sitio_on():
    db = get_db()
    r = db.execute("SELECT valor FROM configuracion WHERE clave='activo'").fetchone()
    db.close()
    return r["valor"] == "1" if r else True

def fmt(n):
    return "₡ {:,.0f}".format(float(n or 0))

def esc(s):
    return str(s or "").replace("\\","\\\\").replace("'","\\'").replace('"','\\"').replace("\n"," ")

def ficha_nueva():
    n = datetime.now()
    return n.strftime("%H%M%S") + str(n.microsecond)[:3]

# ═══════════════════════════════════════════════════════
# INICIALIZAR DB AL IMPORTAR (FIX RAILWAY/GUNICORN)
# ═══════════════════════════════════════════════════════
init_db()

# ═══════════════════════════════════════════════════════
# ESTILOS
# ═══════════════════════════════════════════════════════
ESTILOS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --mo:#f5c518;
  --mo2:#c8a415;
  --do:#cc0000;
  --do2:#ff4444;
  --bg:#0a0a0a;
  --bl:#f5c518;
  --gr:#c8a415;
  --er:#dc2626;
  --ok:#16a34a;
  --r:10px;
  --sh:0 4px 18px rgba(200,0,0,.18);
}
body{font-family:'Nunito',sans-serif;background:#0a0a0a;color:#f5c518;min-height:100vh}
*{color:inherit}
a,p,span,div,td,th,h1,h2,h3,h4,li{color:inherit}

/* MARCA DE AGUA */
body::before{
  content:"BISMARCK";position:fixed;bottom:18px;right:24px;
  font-size:4.5rem;font-weight:900;letter-spacing:5px;
  color:rgba(200,0,0,.08);pointer-events:none;z-index:0;
}
body::after{
  content:"BISMARCK";position:fixed;top:38%;left:-38px;
  font-size:3rem;font-weight:900;letter-spacing:4px;
  color:rgba(200,0,0,.05);pointer-events:none;z-index:0;
  transform:rotate(-90deg);transform-origin:left center;
}

/* NAV */
nav{
  background:linear-gradient(135deg,#1a0000,#8b0000);
  padding:14px 28px;display:flex;align-items:center;
  justify-content:space-between;position:sticky;top:0;z-index:100;
  box-shadow:0 3px 16px rgba(200,0,0,.4);
}
.logo{font-size:1.5rem;font-weight:900;color:#fff;text-decoration:none;
  display:flex;align-items:center;gap:10px}
.logo img{height:36px;width:36px;border-radius:8px;object-fit:cover;
  border:2px solid rgba(255,255,255,.4)}
.badge-nav{background:var(--do2);color:#8b0000;font-size:.6rem;font-weight:900;
  padding:2px 8px;border-radius:20px;letter-spacing:1px}
.nav-links{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.nav-links a{color:#f5c518;text-decoration:none;padding:6px 14px;
  border-radius:20px;font-size:.84rem;font-weight:700;transition:.2s;
  border:2px solid transparent}
.nav-links a:hover,.nav-links a.on{background:rgba(255,255,255,.18);
  border-color:rgba(255,255,255,.35)}
.btn-carrito{background:#cc0000;color:#fff;border:none;border-radius:20px;
  padding:7px 16px;font-size:.88rem;font-weight:900;cursor:pointer;
  display:flex;align-items:center;gap:6px;transition:.2s;font-family:'Nunito',sans-serif}
.btn-carrito:hover{background:#ff4444;transform:scale(1.04)}
.badge-cnt{background:#1a1a1a;color:#cc0000;border-radius:50%;width:20px;height:20px;
  display:inline-flex;align-items:center;justify-content:center;
  font-size:.72rem;font-weight:900}

/* CONTENEDOR */
.wrap{max-width:1100px;margin:0 auto;padding:26px 18px;position:relative;z-index:1}

/* HERO */
.hero{
  background:linear-gradient(135deg,#1a0000,#8b0000,#cc0000);
  border-radius:var(--r);padding:40px;text-align:center;margin-bottom:24px;
  box-shadow:0 8px 36px rgba(200,0,0,.35);position:relative;overflow:hidden;
}
.hero::before{content:"🍊 🍋 🍇 🍓 🍍 🥭 🍉";position:absolute;top:8px;
  left:0;right:0;font-size:1.8rem;opacity:.12;letter-spacing:16px}
.hero h1{font-size:2.4rem;font-weight:900;color:#f5c518;margin-bottom:8px;
  text-shadow:0 2px 10px rgba(0,0,0,.3)}
.hero p{color:#f5c518;font-size:.98rem;font-weight:600}

/* BUSCADOR */
.buscador-box{background:#1a1a1a;border-radius:var(--r);padding:14px;
  margin-bottom:14px;border:2px solid #440000;box-shadow:var(--sh);
  display:flex;gap:10px;align-items:center}
.buscador-box input{flex:1;border:2px solid #440000;border-radius:8px;
  padding:10px 14px;font-size:.94rem;font-family:'Nunito',sans-serif;
  outline:none;color:var(--bl);transition:.2s}
.buscador-box input:focus{border-color:var(--mo)}
.btn-limpiar{background:#f5f0ff;border:2px solid #440000;border-radius:8px;
  padding:9px 14px;cursor:pointer;color:var(--mo);font-size:.84rem;
  font-weight:800;font-family:'Nunito',sans-serif;transition:.2s}
.btn-limpiar:hover{background:var(--mo);color:#fff}

/* CATEGORIAS */
.cats{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px}
.cat{padding:7px 16px;border-radius:20px;border:2px solid var(--do);
  background:#1a1a1a;color:var(--bl);font-size:.82rem;font-weight:800;
  cursor:pointer;transition:.2s;font-family:'Nunito',sans-serif}
.cat:hover,.cat.sel{background:linear-gradient(135deg,var(--mo),var(--mo2));
  color:#fff;border-color:var(--mo)}

/* CARDS */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:16px}
.card{background:#1a1a1a;border-radius:var(--r);border:2px solid #440000;
  overflow:hidden;transition:.25s;box-shadow:var(--sh)}
.card:hover{transform:translateY(-4px);box-shadow:0 10px 28px rgba(200,0,0,.28);
  border-color:#cc0000}
.card-img{width:100%;height:148px;background:linear-gradient(135deg,#1a0000,#2a0000);
  display:flex;align-items:center;justify-content:center;font-size:3.2rem;
  position:relative;cursor:pointer}
.tag-cat{position:absolute;top:8px;left:8px;background:linear-gradient(135deg,#8b0000,#cc0000);
  color:#fff;font-size:.66rem;font-weight:900;padding:3px 9px;border-radius:20px}
.tag-ver{position:absolute;bottom:8px;right:8px;background:rgba(180,0,0,.85);
  color:#fff;font-size:.68rem;padding:3px 8px;border-radius:6px;font-weight:700}
.card-body{padding:13px}
.card-nombre{font-size:.98rem;font-weight:900;margin-bottom:2px;cursor:pointer;
  color:#f5c518;transition:.2s}
.card-nombre:hover{color:var(--mo)}
.card-desc{font-size:.75rem;color:#c8a415;margin-bottom:5px;line-height:1.4}
.card-unidad{font-size:.73rem;color:var(--mo);font-weight:700;margin-bottom:8px}
.card-precio{font-size:1.22rem;font-weight:900;color:#f5c518;margin-bottom:10px}

/* CANTIDAD */
.qty-row{display:flex;align-items:center;gap:8px;margin-bottom:10px}
.qty-btn{width:30px;height:30px;border-radius:50%;border:2px solid var(--mo);
  background:#1a1a1a;color:var(--mo);font-size:1.15rem;font-weight:900;cursor:pointer;
  display:flex;align-items:center;justify-content:center;transition:.2s}
.qty-btn:hover{background:#cc0000;color:#fff}
.qty-num{width:48px;text-align:center;border:2px solid #440000;border-radius:8px;
  padding:4px;font-size:.95rem;font-weight:800;font-family:'Nunito',sans-serif}
.btn-add{width:100%;padding:10px;border:none;border-radius:8px;
  background:linear-gradient(135deg,var(--mo),var(--mo2));
  color:#fff;font-size:.88rem;font-weight:900;cursor:pointer;
  font-family:'Nunito',sans-serif;transition:.2s}
.btn-add:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(180,0,0,.35)}
.btn-add.ok{background:linear-gradient(135deg,#16a34a,#22c55e)}

/* FORMULARIOS */
.fg{margin-bottom:13px}
.fg label{display:block;font-size:.76rem;color:#c8a415;margin-bottom:4px;
  font-weight:800;text-transform:uppercase;letter-spacing:.4px}
.fg input,.fg select,.fg textarea{width:100%;padding:10px 13px;
  background:#1a1a1a;border:2px solid #440000;border-radius:8px;
  color:#fff;font-size:.92rem;font-family:'Nunito',sans-serif;transition:.2s}
.fg input:focus,.fg select:focus,.fg textarea:focus{outline:none;border-color:#cc0000}
.fg textarea{resize:vertical;min-height:68px}

/* BOTONES */
.btn{display:inline-flex;align-items:center;gap:6px;padding:10px 20px;
  border:none;border-radius:8px;font-size:.87rem;font-weight:800;cursor:pointer;
  transition:.2s;text-decoration:none;font-family:'Nunito',sans-serif}
.btn-mo{background:linear-gradient(135deg,#8b0000,#cc0000);color:#f5c518}
.btn-mo:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(180,0,0,.35)}
.btn-do{background:linear-gradient(135deg,var(--do),var(--do2));color:#8b0000}
.btn-do:hover{transform:translateY(-1px)}
.btn-ve{background:linear-gradient(135deg,#16a34a,#22c55e);color:#f5c518}
.btn-ve:hover{transform:translateY(-1px)}
.btn-ro{background:linear-gradient(135deg,#dc2626,#ef4444);color:#f5c518}
.btn-ro:hover{transform:translateY(-1px)}
.btn-az{background:linear-gradient(135deg,#1d4ed8,#3b82f6);color:#f5c518}
.btn-full{width:100%;justify-content:center}

/* ALERTAS */
.alerta{padding:11px 15px;border-radius:8px;margin-bottom:12px;
  font-size:.87rem;font-weight:700}
.alerta-ok{background:#dcfce7;border:1px solid #16a34a;color:#f5c518}
.alerta-er{background:#fee2e2;border:1px solid #dc2626;color:#b91c1c}
.alerta-in{background:#fef9c3;border:1px solid #ca8a04;color:#92400e}

/* PANEL */
.panel{background:#1a1a1a;border-radius:var(--r);padding:20px;
  border:2px solid #440000;margin-bottom:18px;box-shadow:var(--sh)}
.panel h2{font-size:1.15rem;font-weight:900;color:#f5c518;
  margin-bottom:14px;border-bottom:2px solid #440000;padding-bottom:8px}

/* STATS */
.stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px;margin-bottom:18px}
.stat{background:#1a1a1a;border-radius:var(--r);padding:16px;text-align:center;
  border:2px solid #440000;border-top:4px solid var(--do);box-shadow:var(--sh)}
.stat-n{font-size:1.9rem;font-weight:900;color:#f5c518}
.stat-l{font-size:.7rem;color:#c8a415;margin-top:2px;text-transform:uppercase;
  letter-spacing:.5px;font-weight:700}

/* TABLA */
.tabla-wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse}
th{background:linear-gradient(135deg,#1a0000,#8b0000);padding:10px 12px;
  text-align:left;color:#fff;font-size:.76rem;text-transform:uppercase;letter-spacing:.7px}
td{padding:9px 12px;border-bottom:1px solid #2a0000;font-size:.86rem;vertical-align:middle;color:#f5c518}
tr:hover td{background:#1a0000}

/* BADGES */
.bdg{display:inline-block;padding:3px 10px;border-radius:20px;font-size:.72rem;font-weight:800}
.bdg-p{background:#2a1a00;color:#ffa500;border:1px solid #aa6600}
.bdg-c{background:#002a0a;color:#22c55e;border:1px solid #16a34a}
.bdg-x{background:#2a0000;color:#f5c518;border:1px solid #cc0000}
.bdg-e{background:#001a2a;color:#38bdf8;border:1px solid #0284c7}
.bdg-espera{background:#2a1500;color:#f5a623;border:1px solid #a06010}

/* PEDIDOS PROCESO */
.proceso{background:#1a1a1a;border-radius:var(--r);padding:16px;margin-bottom:20px;
  border:2px solid #440000;border-left:5px solid var(--do);box-shadow:var(--sh)}
.proceso h3{color:var(--mo);font-size:1.05rem;font-weight:900;margin-bottom:10px}
.ped-chip{background:#2a0000;border-radius:8px;padding:8px 13px;
  display:flex;align-items:center;gap:9px;margin-bottom:5px;
  border-left:3px solid var(--mo2);flex-wrap:wrap}
.ped-id{background:var(--mo);color:#fff;border-radius:20px;padding:2px 9px;
  font-weight:900;font-size:.76rem}
.ped-ficha{background:#cc0000;color:#fff;border-radius:20px;padding:2px 9px;
  font-weight:900;font-size:.76rem}

/* MODAL */
.overlay{display:none;position:fixed;top:0;left:0;width:100%;height:100%;
  background:rgba(0,0,0,.58);z-index:9999;justify-content:center;
  align-items:flex-start;padding:28px 14px;overflow-y:auto;backdrop-filter:blur(3px)}
.overlay.abierto{display:flex}
.modal{background:#1a1a1a;border-radius:var(--r);padding:26px;width:100%;
  max-width:520px;border:2px solid #cc0000;position:relative;margin:auto;
  box-shadow:0 18px 54px rgba(180,0,0,.22)}
.modal.ancho{max-width:580px}
.modal-x{position:absolute;top:11px;right:13px;background:rgba(0,0,0,.07);
  border:none;color:var(--bl);font-size:1.25rem;font-weight:900;cursor:pointer;
  border-radius:7px;width:30px;height:30px;display:flex;align-items:center;
  justify-content:center;transition:.2s}
.modal-x:hover{background:var(--er);color:#fff}
.modal-titulo{font-size:1.25rem;font-weight:900;color:var(--mo);
  margin-bottom:16px;padding-right:33px}

/* CARRITO */
.car-item{display:flex;align-items:flex-start;padding:9px 0;
  border-bottom:1px solid #440000;gap:9px}
.car-nombre{font-weight:800;font-size:.89rem;cursor:pointer;color:var(--mo)}
.car-qty{color:#c8a415;font-size:.8rem}
.car-precio{color:var(--mo);font-weight:900;font-size:.89rem}
.car-total-row{display:flex;justify-content:space-between;padding:13px 0;
  font-size:1.08rem;font-weight:900;border-top:2px solid var(--mo);margin-top:7px}
.car-total-row span:last-child{color:#f5c518;font-size:1.2rem}

/* TICKET */
.ticket{background:#1a1a1a;color:#1a0033;border-radius:8px;padding:18px;
  font-family:'Courier New',monospace;border:2px dashed #440000}
.tk-head{text-align:center;border-bottom:2px dashed #440000;
  padding-bottom:9px;margin-bottom:9px}
.tk-row{display:flex;justify-content:space-between;padding:2px 0;font-size:.83rem;color:#f5c518}
.tk-foot{text-align:center;margin-top:9px;border-top:2px dashed #440000;
  padding-top:8px;font-size:.73rem;color:#c8a415}

/* PEDIDO CLIENTE */
.ped-card{background:#1a1a1a;border-radius:var(--r);padding:14px;margin-bottom:11px;
  border:2px solid #440000;border-left:4px solid var(--mo);box-shadow:var(--sh)}
.ped-meta{display:flex;gap:12px;flex-wrap:wrap;margin-top:8px;
  font-size:.81rem;color:#c8a415}
.confirmar-box{background:#1a0000;border:2px solid #cc0000;border-radius:8px;
  padding:14px;margin:9px 0}

/* LOGIN */
.login-box{max-width:370px;margin:68px auto;background:#1a1a1a;border-radius:var(--r);
  padding:38px;border:2px solid #440000;box-shadow:0 8px 36px rgba(180,0,0,.14)}
.login-box h2{text-align:center;margin-bottom:22px;color:#f5c518;
  font-size:1.9rem;font-weight:900}

/* ADMIN GRILLA */
.ag{display:grid;grid-template-columns:1fr 2fr;gap:18px}
@media(max-width:720px){.ag{grid-template-columns:1fr}}

/* ITEMS TABLA */
.it{width:100%;border-collapse:collapse;font-size:.81rem;margin:7px 0}
.it th{background:#2a0000;padding:5px 9px;text-align:left;color:#f5c518;font-size:.73rem}
.it td{padding:5px 9px;border-bottom:1px solid #440000}

/* ENV SECTION */
.env-section{background:#1a1a1a;border-radius:var(--r);padding:20px;margin-bottom:18px;
  border:2px solid #ff2222;box-shadow:var(--sh)}
.env-section h2{font-size:1.1rem;font-weight:900;margin-bottom:14px;
  color:#f5c518;border-bottom:1px solid #1a0000;padding-bottom:8px}

/* TABS */
.tabs{display:flex;gap:7px;margin-bottom:16px;flex-wrap:wrap}

/* CONFIG */
.logo-prev{width:66px;height:66px;object-fit:cover;border-radius:8px;
  border:2px solid var(--do);display:block;margin-bottom:9px}

/* FOOTER */
footer{text-align:center;padding:24px;color:#c8a415;font-size:.76rem;
  border-top:2px solid #440000;margin-top:34px;background:#1a1a1a;
  position:relative;z-index:1;font-weight:700}
footer span{color:var(--mo);font-weight:900}
</style>
"""

# ═══════════════════════════════════════════════════════
# JS CARRITO
# ═══════════════════════════════════════════════════════
JS_CARRITO = """
<script>
var carrito = {};

function abrirModal(id){ document.getElementById(id).classList.add('abierto'); document.body.style.overflow='hidden'; }
function cerrarModal(id){ document.getElementById(id).classList.remove('abierto'); document.body.style.overflow=''; }
document.addEventListener('click', function(e){ if(e.target.classList.contains('overlay')){ e.target.classList.remove('abierto'); document.body.style.overflow=''; } });

function mostrarTab(t){
  ['pedidos','enviados','productos','config','stats'].forEach(function(x){
    var el = document.getElementById('tab_'+x);
    if(el) el.style.display = (x===t) ? 'block' : 'none';
  });
}

function cambiarQty(id, delta){
  var inp = document.getElementById('qty_'+id);
  if(!inp) return;
  var v = parseInt(inp.value||0) + delta;
  if(v < 0) v = 0;
  inp.value = v;
}

function actualizarContador(){
  var total=0, n=0;
  for(var k in carrito){ total += carrito[k].precio * carrito[k].qty; n += carrito[k].qty; }
  var el = document.getElementById('cnt-carrito');
  if(el) el.textContent = n;
}

function agregarProducto(id, nombre, precio, img, unidad){
  var inp = document.getElementById('qty_'+id);
  var qty = parseInt(inp ? inp.value : 0);
  if(qty <= 0){ alert('Ingresa una cantidad mayor a 0'); return; }
  if(carrito[id]){ carrito[id].qty += qty; }
  else { carrito[id] = {nombre:nombre, precio:precio, qty:qty, img:img||'', unidad:unidad||'unidad'}; }
  actualizarContador();
  var btn = document.getElementById('btn_'+id);
  if(btn){ btn.textContent='✅ Agregado!'; btn.classList.add('ok');
    setTimeout(function(){ btn.textContent='🛒 Agregar'; btn.classList.remove('ok'); }, 1500); }
}

function agregarDesdeDetalle(id, nombre, precio, img, unidad){
  var inp = document.getElementById('qd'+id);
  var qty = parseInt(inp ? inp.value : 0);
  if(qty <= 0){ alert('Ingresa una cantidad mayor a 0'); return; }
  if(carrito[id]){ carrito[id].qty += qty; }
  else { carrito[id] = {nombre:nombre, precio:precio, qty:qty, img:img||'', unidad:unidad||'unidad'}; }
  actualizarContador();
  var btn = document.getElementById('btn_'+id);
  if(btn){ btn.textContent='✅ Agregado!'; btn.classList.add('ok');
    setTimeout(function(){ btn.textContent='🛒 Agregar'; btn.classList.remove('ok'); }, 1500); }
  cerrarModal('md'+id);
}

function quitarItem(id){ delete carrito[id]; actualizarContador(); renderCarrito(); }

function renderCarrito(){
  var el = document.getElementById('carrito-items');
  if(!el) return;
  var html='', total=0;
  for(var k in carrito){
    var it = carrito[k];
    var sub = it.precio * it.qty;
    total += sub;
    var imgH = it.img
      ? '<img src="'+it.img+'" style="width:50px;height:50px;object-fit:cover;border-radius:7px;border:2px solid #440000;flex-shrink:0">'
      : '<div style="width:50px;height:50px;background:#f5f0ff;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:1.6rem;flex-shrink:0">🍊</div>';
    html += '<div class="car-item">';
    html += imgH;
    html += '<div style="flex:1;min-width:0">';
    html += '<div class="car-nombre" onclick="abrirModal(\"det_'+k+'\")">'+it.nombre+' <span style="font-size:.7rem;color:#aaa">🔍</span></div>';
    html += '<div style="font-size:.73rem;color:#888;margin:1px 0">📦 '+it.unidad+'</div>';
    html += '<div class="car-qty">'+it.qty+' × ₡'+it.precio.toLocaleString('es-CR')+'</div>';
    html += '</div>';
    html += '<div style="display:flex;flex-direction:column;align-items:flex-end;gap:5px">';
    html += '<span class="car-precio">₡'+sub.toLocaleString('es-CR')+'</span>';
    html += '<button onclick="quitarItem('+k+')" style="background:#fee2e2;border:1px solid #fca5a5;border-radius:20px;padding:2px 9px;cursor:pointer;color:#b91c1c;font-size:.78rem;font-weight:800">✕</button>';
    html += '</div></div>';
  }
  if(!html) html = '<div style="text-align:center;padding:28px;color:#aaa"><div style="font-size:2.8rem;margin-bottom:9px">🛒</div><p>El carrito está vacío</p></div>';
  el.innerHTML = html;
  var tt = document.getElementById('carrito-total');
  if(tt) tt.textContent = '₡ '+total.toLocaleString('es-CR');
  var inp = document.getElementById('inp_items');
  if(inp){
    var items=[];
    for(var k in carrito){ items.push({id:k, nombre:carrito[k].nombre, precio:carrito[k].precio, qty:carrito[k].qty, unidad:carrito[k].unidad}); }
    inp.value = JSON.stringify(items);
  }
  var si = document.getElementById('inp_subtotal');
  if(si){ var s=0; for(var k in carrito) s+=carrito[k].precio*carrito[k].qty; si.value=s; }
}

function abrirCarrito(){ renderCarrito(); abrirModal('modal_carrito'); }

function irAPedido(){
  if(Object.keys(carrito).length===0){ alert('Agrega productos al carrito primero'); return; }
  renderCarrito();
  cerrarModal('modal_carrito');
  abrirModal('modal_pedido');
}

function imprimirTicket(id){
  var el = document.getElementById(id);
  if(!el) return;
  var tk = el.querySelector('.ticket');
  if(!tk) return;
  var v = window.open('','_blank','width=460,height:680');
  v.document.write('<!DOCTYPE html><html><head><title>Pedido</title><style>body{font-family:monospace;padding:18px;max-width:400px;margin:0 auto}.tk-row{display:flex;justify-content:space-between;padding:2px 0;font-size:.83rem;color:#f5c518}.tk-head{text-align:center;border-bottom:2px dashed #ccc;padding-bottom:8px;margin-bottom:8px}.tk-foot{text-align:center;margin-top:9px;border-top:2px dashed #ccc;padding-top:8px;font-size:.72rem;color:#888}</style></head><body>');
  v.document.write(tk.outerHTML);
  v.document.write('</body></html>');
  v.document.close(); v.focus();
  setTimeout(function(){ v.print(); }, 350);
}

window.addEventListener('DOMContentLoaded', function(){
  var n = document.querySelectorAll('#grilla .card').length;
  var ct = document.getElementById('cnt-prods');
  if(ct) ct.textContent = '('+n+' productos)';
});
function toggleMotivo(id, val){
  var box = document.getElementById('motivo_box_'+id);
  if(box) box.style.display = (val==='Negado') ? 'block' : 'none';
}
</script>
"""

# ═══════════════════════════════════════════════════════
# HELPERS HTML
# ═══════════════════════════════════════════════════════
def nav(activo="tienda", c=None):
    if c is None: c = cfg()
    nom = c.get("nombre","Mercado Frutas Frescas")
    logo = c.get("logo","")
    if logo:
        if ";" in logo:
            lmime, lb64 = logo.split(";", 1)
        else:
            lmime, lb64 = "image/jpeg", logo
        logo_tag = '<img src="data:%s;base64,%s">' % (lmime, lb64)
    else:
        logo_tag = "🍊"
    links = [("tienda","/","🍊 Tienda"),("mis_pedidos","/mis-pedidos","📦 Mis Pedidos"),("admin_panel","/admin","⚙️ Admin")]
    li = "".join('<a href="%s" class="%s">%s</a>' % (u, "on" if activo==k else "", l) for k,u,l in links)
    return """<!DOCTYPE html><html lang="es"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<title>%s</title>%s</head><body>
<nav>
  <a class="logo" href="/">%s %s <span class="badge-nav">MERCADO FRESCO</span></a>
  <div class="nav-links">%s
    <button class="btn-carrito" onclick="abrirCarrito()">
      🛒 Carrito <span class="badge-cnt" id="cnt-carrito">0</span>
    </button>
  </div>
</nav>""" % (nom, ESTILOS, logo_tag, nom, li)

PIE = '<footer><p>🍊 <span>Mercado Frutas Frescas</span> — Powered by <span>Bismarck</span></p></footer>'

def alerta(msg, tipo="ok"):
    if not msg: return ""
    cls = {"ok":"alerta-ok","er":"alerta-er","in":"alerta-in"}.get(tipo,"alerta-in")
    return '<div class="alerta %s">%s</div>' % (cls, msg)

def bdg_estado(e):
    m = {"Pendiente":("bdg-p","⏳"),"Aprobado":("bdg-c","✅"),"En Espera":("bdg-espera","💰"),"Pagado":("bdg-c","💵"),"Negado":("bdg-x","❌"),"Confirmado":("bdg-c","✅"),"Cancelado":("bdg-x","❌"),"Enviado":("bdg-e","🚚")}
    cls, ico = m.get(e, ("bdg-p","⏳"))
    return '<span class="bdg %s">%s %s</span>' % (cls, ico, e)

def tabla_items(items_json):
    try: items = json.loads(items_json)
    except: return "<p>—</p>"
    rows = ""
    for it in items:
        sub = float(it["precio"]) * int(it["qty"])
        rows += "<tr><td>%s</td><td>%d %s</td><td>%s</td><td><strong>%s</strong></td></tr>" % (
            it["nombre"], it["qty"], it.get("unidad",""), fmt(it["precio"]), fmt(sub))
    return "<table class='it'><thead><tr><th>Producto</th><th>Cantidad</th><th>Precio</th><th>Subtotal</th></tr></thead><tbody>%s</tbody></table>" % rows

def hacer_ticket(p, admin=False):
    try: items = json.loads(p["items"])
    except: items = []
    rows = ""
    for it in items:
        sub = float(it["precio"]) * int(it["qty"])
        rows += '<div class="tk-row"><span>%s x%d %s</span><span>%s</span></div>' % (
            it["nombre"][:18], it["qty"], it.get("unidad",""), fmt(sub))
    env_row = ""
    if float(p["envio"] or 0) > 0:
        env_row = '<div class="tk-row"><span>🚚 Envío:</span><span style="color:var(--do)">+ %s</span></div>' % fmt(p["envio"])
    hora_row = ('<div class="tk-row"><span>⏰ Llega:</span><strong>%s</strong></div>' % p["hora_entrega"]) if p["hora_entrega"] else ""
    pie_txt = "Panel Admin" if admin else "¡Gracias por tu compra! 🍊"
    return """<div class="ticket">
  <div class="tk-head">
    <strong style="font-size:1rem;color:#cc0000">🍊 Mercado Frutas Frescas</strong><br>
    <span style="font-size:.7rem;color:#888">%s — Pedido #%d · Ficha: %s</span>
  </div>
  <div class="tk-row"><span>👤 Cliente:</span><span>%s</span></div>
  <div class="tk-row"><span>📱 Celular:</span><span>%s</span></div>
  <div style="font-size:.77rem;color:#888;padding:2px 0 5px">📍 %s</div>
  <hr style="border:none;border-top:1px dashed #440000;margin:6px 0">
  %s
  <hr style="border:none;border-top:1px dashed #440000;margin:6px 0">
  <div class="tk-row"><span>Subtotal:</span><span>%s</span></div>
  %s
  <div class="tk-row" style="font-size:1rem;font-weight:900"><span>TOTAL:</span><span style="color:#cc0000">%s</span></div>
  %s
  <div class="tk-foot">%s</div>
</div>""" % (p["fecha"], p["id"], p["ficha"] or "—",
             p["nombre_cliente"], p["celular"], p["direccion"],
             rows, fmt(p["subtotal"]), env_row, fmt(p["total"]), hora_row, pie_txt)

def banner_activos(peds):
    activos = [p for p in peds if p["estado"] in ("Pendiente","Aprobado","Confirmado","En Espera")]
    activos = sorted(activos, key=lambda x: x["id"])
    if not activos: return ""
    chips = ""
    for p in activos[:10]:
        fch = ('<span class="ped-ficha">Ficha #%s</span>' % p["ficha"]) if p["ficha"] else ""
        n = len(json.loads(p["items"] or "[]"))
        chips += '<div class="ped-chip"><span class="ped-id">#%d</span>%s<strong>%s</strong><span style="color:#888;font-size:.8rem">— %d items</span>%s</div>' % (
            p["id"], fch, p["nombre_cliente"], n, bdg_estado(p["estado"]))
    extra = " (%d total)" % len(activos) if len(activos) > 10 else ""
    return '<div class="proceso"><h3>🍊 Pedidos en Proceso%s</h3>%s</div>' % (extra, chips)


# ═══════════════════════════════════════════════════════
# RUTA: TIENDA
# ═══════════════════════════════════════════════════════
@app.route("/")
def tienda():
    if not sitio_on():
        return "<h1 style='text-align:center;padding:80px;font-family:sans-serif'>🍊 El mercado está temporalmente cerrado.</h1>"
    c = cfg()
    db = get_db()
    prods = db.execute("SELECT * FROM productos WHERE activo=1 ORDER BY categoria,nombre").fetchall()
    peds  = db.execute("SELECT * FROM pedidos WHERE estado IN ('Pendiente','Confirmado') ORDER BY id LIMIT 15").fetchall()
    db.close()
    msg  = request.args.get("msg","")
    tipo = request.args.get("tipo","ok")
    nom  = c.get("nombre","Mercado Frutas Frescas")

    cats_set = sorted(set(p["categoria"] for p in prods))
    cats_html = '<button class="cat sel" data-cat="todos" onclick="filtrarCat(this,\'todos\')">🍊 Todos</button>'
    iconos = {"Tropicales":"🌴","Cítricos":"🍋","Berries":"🍓","Frutas":"🍎","Verduras":"🥬","Otros":"🛒"}
    for cat in cats_set:
        ico = iconos.get(cat, "🍊")
        cats_html += '<button class="cat" data-cat="%s" onclick="filtrarCat(this,\'%s\')">%s %s</button>' % (esc(cat),esc(cat),ico,cat)

    cards_html = ""
    modales_det = ""
    for p in prods:
        raw_img  = p["imagen"] or ""
        if raw_img:
            if ";" in raw_img:
                mime_part, b64_part = raw_img.split(";", 1)
            else:
                mime_part, b64_part = "image/jpeg", raw_img
            img_src = "data:%s;base64,%s" % (mime_part, b64_part)
        else:
            img_src = ""
        img_card = '<img src="%s" style="width:100%%;height:100%%;object-fit:cover">' % img_src if img_src else "🍊"
        img_modal = ('<img src="%s" style="width:100%%;max-height:250px;object-fit:cover;border-radius:8px;margin-bottom:14px">' % img_src) if img_src else '<div style="text-align:center;font-size:5rem;padding:18px 0">🍊</div>'
        desc  = p["descripcion"] or ""
        unid  = p["unidad"] or "unidad"
        mid   = "md%d" % p["id"]

        modales_det += """
<div class="overlay" id="%s">
  <div class="modal">
    <button class="modal-x" onclick="cerrarModal('%s')">✕</button>
    %s
    <div class="modal-titulo">%s</div>
    <div style="background:#150000;border-radius:8px;padding:10px 13px;margin-bottom:13px;font-size:.84rem;color:#555">
      %s
      <div style="margin-top:5px;color:var(--mo);font-weight:700">📦 Unidad: %s &nbsp;·&nbsp; 📂 %s</div>
    </div>
    <div style="text-align:center;background:linear-gradient(135deg,#150000,#1a0000);border-radius:8px;padding:13px;margin-bottom:13px">
      <div style="font-size:1.9rem;font-weight:900;color:var(--mo)">%s</div>
      <div style="font-size:.76rem;color:#888">Por %s · Pago contra entrega</div>
    </div>
    <div class="qty-row" style="justify-content:center;margin-bottom:11px">
      <button class="qty-btn" onclick="cambiarQty('md%d',-1)">−</button>
      <input type="number" class="qty-num" id="qd%d" value="0" min="0">
      <button class="qty-btn" onclick="cambiarQty('md%d',1)">+</button>
    </div>
    <button class="btn btn-mo btn-full" onclick="agregarDesdeDetalle(%d,'%s',%g,'%s','%s')">🛒 Agregar al pedido</button>
  </div>
</div>""" % (mid, mid, img_modal, p["nombre"],
             desc, unid, p["categoria"],
             fmt(p["precio"]), unid,
             p["id"], p["id"], p["id"],
             p["id"], esc(p["nombre"]), p["precio"], esc(img_src), esc(unid))

        cards_html += """<div class="card" data-cat="%s" data-nombre="%s">
  <div class="card-img" onclick="abrirModal('%s')">
    <span class="tag-cat">%s</span>%s<span class="tag-ver">🔍 Ver más</span>
  </div>
  <div class="card-body">
    <div class="card-nombre" onclick="abrirModal('%s')">%s</div>
    %s
    <div class="card-unidad">📦 Por %s</div>
    <div class="card-precio">%s</div>
    <div class="qty-row">
      <button class="qty-btn" onclick="cambiarQty(%d,-1)">−</button>
      <input type="number" class="qty-num" id="qty_%d" value="0" min="0">
      <button class="qty-btn" onclick="cambiarQty(%d,1)">+</button>
    </div>
    <button class="btn-add" id="btn_%d" onclick="agregarProducto(%d,'%s',%g,'%s','%s')">🛒 Agregar</button>
  </div>
</div>""" % (esc(p["categoria"]), esc(p["nombre"]),
             mid, p["categoria"], img_card,
             mid, p["nombre"],
             ('<div class="card-desc">%s</div>' % desc[:55]+("..." if len(desc)>55 else "")) if desc else "",
             unid, fmt(p["precio"]),
             p["id"], p["id"], p["id"],
             p["id"], p["id"], esc(p["nombre"]), p["precio"], esc(img_src), esc(unid))

    grid = '<div class="grid" id="grilla">%s</div>' % cards_html if cards_html else '<div class="alerta alerta-in">No hay productos disponibles.</div>'

    modal_carrito = """
<div class="overlay" id="modal_carrito">
  <div class="modal ancho">
    <button class="modal-x" onclick="cerrarModal('modal_carrito')">✕</button>
    <div class="modal-titulo">🛒 Tu Carrito</div>
    <div id="carrito-items"></div>
    <div class="car-total-row"><span>Total:</span><span id="carrito-total">₡ 0</span></div>
    <button class="btn btn-mo btn-full" style="margin-top:13px" onclick="irAPedido()">✅ Hacer Pedido</button>
  </div>
</div>"""

    modal_pedido = """
<div class="overlay" id="modal_pedido">
  <div class="modal ancho">
    <button class="modal-x" onclick="cerrarModal('modal_pedido')">✕</button>
    <div class="modal-titulo">👤 Datos del Cliente</div>
    <form method="POST" action="/hacer-pedido">
      <input type="hidden" name="items_json" id="inp_items">
      <input type="hidden" name="subtotal"   id="inp_subtotal">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:11px">
        <div class="fg"><label>Nombre Completo *</label>
          <input type="text" name="nombre" required placeholder="Juan García"></div>
        <div class="fg"><label>Celular *</label>
          <input type="text" name="celular" required placeholder="8888-8888"></div>
      </div>
      <div class="fg"><label>Notas del pedido</label>
        <textarea name="notas" placeholder="Ej: frutas bien maduras, sin golpes..."></textarea></div>
      <div style="background:#150000;border:2px solid #440000;border-radius:8px;padding:11px;margin-bottom:13px;font-size:.82rem;color:#888">
        📍 Su pedido quedará listo para <strong>recoger</strong> en el mercado.<br>
        💵 Pago <strong>contra entrega</strong> al momento de recoger.
      </div>
      <button type="submit" class="btn btn-mo btn-full">✅ Confirmar Pedido</button>
    </form>
  </div>
</div>"""

    return nav("tienda", c) + """
<div class="wrap">
  <div class="hero">
    <h1>%s</h1>
    <p>Frutas frescas del mercado directo a tu puerta 🍋</p>
  </div>
  %s%s
  <div class="buscador-box">
    <span style="font-size:1.2rem">🔍</span>
    <input type="text" id="inp-buscar" placeholder="Buscar fruta o categoría... (ej: mango, fresa, cítricos)" oninput="buscar(this.value)">
    <button class="btn-limpiar" onclick="limpiar()">✕ Limpiar</button>
  </div>
  <div class="cats">%s</div>
  <h2 style="font-size:1.5rem;font-weight:900;color:var(--mo);margin-bottom:14px">
    🍋 Productos Frescos <span id="cnt-prods" style="font-size:.88rem;color:#888;font-weight:700"></span>
  </h2>
  %s
  <div id="sin-resultados" style="display:none;text-align:center;padding:38px;color:#aaa">
    <div style="font-size:2.8rem;margin-bottom:10px">🔍</div><p>No se encontraron productos.</p>
  </div>
</div>
%s%s%s
<script>
function filtrarCat(btn, cat){
  document.querySelectorAll('.cat').forEach(function(b){ b.classList.remove('sel'); });
  btn.classList.add('sel');
  btn.dataset.catActiva = cat;
  buscarYFiltrar(cat, document.getElementById('inp-buscar').value.toLowerCase());
}
function buscar(txt){
  var btn = document.querySelector('.cat.sel');
  var cat = btn ? (btn.dataset.catActiva || btn.dataset.cat || 'todos') : 'todos';
  buscarYFiltrar(cat, txt.toLowerCase());
}
function buscarYFiltrar(cat, txt){
  var cards = document.querySelectorAll('#grilla .card');
  var vis = 0;
  cards.forEach(function(c){
    var mc = (cat==='todos' || c.dataset.cat===cat);
    var mb = !txt || (c.dataset.nombre||'').toLowerCase().includes(txt) || (c.dataset.cat||'').toLowerCase().includes(txt);
    c.style.display = (mc && mb) ? '' : 'none';
    if(mc && mb) vis++;
  });
  document.getElementById('sin-resultados').style.display = vis===0 ? 'block' : 'none';
  var ct = document.getElementById('cnt-prods');
  if(ct) ct.textContent = '('+vis+' productos)';
}
function limpiar(){
  document.getElementById('inp-buscar').value = '';
  var btns = document.querySelectorAll('.cat');
  btns.forEach(function(b){ b.classList.remove('sel'); });
  btns[0].classList.add('sel');
  buscarYFiltrar('todos','');
}
</script>
""" % (nom, alerta(msg,tipo), "", cats_html, grid,
       modal_carrito, modal_pedido, modales_det) + PIE + JS_CARRITO + "</body></html>"


# ═══════════════════════════════════════════════════════
# RUTA: HACER PEDIDO
# ═══════════════════════════════════════════════════════
@app.route("/hacer-pedido", methods=["POST"])
def hacer_pedido():
    if not sitio_on(): return redirect(url_for("tienda"))
    f         = request.form
    items_raw = f.get("items_json","[]")
    subtotal  = float(f.get("subtotal",0))
    nombre    = f.get("nombre","").strip()
    celular   = f.get("celular","").strip()
    notas     = f.get("notas","").strip()
    fecha     = datetime.now().strftime("%d/%m/%Y %H:%M")
    fch       = ficha_nueva()
    db = get_db()
    db.execute("""INSERT INTO pedidos(nombre_cliente,celular,direccion,barrio,referencia,
        notas,items,subtotal,envio,total,fecha,ficha)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (nombre,celular,'','','',notas,items_raw,subtotal,0,subtotal,fecha,fch))
    db.commit(); db.close()
    return redirect(url_for("tienda",
        msg="✅ Pedido realizado. Ficha #%s — Ve a 'Mis Pedidos' con tu celular para seguimiento." % fch,
        tipo="ok"))


# ═══════════════════════════════════════════════════════
# RUTA: MIS PEDIDOS
# ═══════════════════════════════════════════════════════
@app.route("/mis-pedidos", methods=["GET","POST"])
def mis_pedidos():
    c = cfg()
    celular = None; peds = None; msg = None
    if request.method == "POST":
        celular = request.form.get("celular","").strip()
    elif request.args.get("celular"):
        celular = request.args.get("celular","").strip()
        msg = request.args.get("msg","")
    if celular:
        db   = get_db()
        peds = db.execute("SELECT * FROM pedidos WHERE celular=? ORDER BY id DESC",(celular,)).fetchall()
        db.close()

    items_html = ""; modales = ""
    if peds:
        for p in peds:
            envio = float(p["envio"] or 0)
            cc    = p["confirmacion"] or "pendiente"
            est   = p["estado"]
            fch   = p["ficha"] or ""

            if est=="Enviado":       borde="border-left-color:#ff2222"
            elif cc=="revision":     borde="border-left-color:#1d4ed8"
            elif cc=="cancelado":    borde="border-left-color:#dc2626;opacity:.75"
            elif est=="Confirmado":  borde="border-left-color:#16a34a"
            else: borde=""

            if est=="Enviado":       bdg='<span class="bdg bdg-e">🚚 Enviado</span>'
            elif cc=="revision":     bdg='<span class="bdg bdg-az" style="background:#dbeafe;color:#1e40af;border:1px solid #3b82f6">🔵 Revisar costo</span>'
            elif cc=="cancelado":    bdg='<span class="bdg bdg-x">❌ Cancelado</span>'
            elif p["estado"]=="Negado": bdg='<span class="bdg bdg-x">❌ Negado</span>'
            elif cc=="aceptado":     bdg='<span class="bdg bdg-c">✅ Confirmado</span>'
            else:                    bdg='<span class="bdg bdg-p">⏳ Pendiente</span>'

            env_banner = ""
            if est=="Aprobado":
                env_banner = '<div style="background:#dcfce7;border:2px solid #16a34a;border-radius:8px;padding:12px;margin:9px 0;text-align:center"><p style="color:#f5c518;font-weight:900">✅ ¡Pedido aprobado!</p><p style="font-size:.83rem;color:#888;margin-top:4px">Ya puede pasar a recogerlo. Pago al recoger.</p></div>'
            elif est=="Negado":
                motivo_txt = (p["motivo"] or "Sin especificar")
                env_banner = '<div style="background:#fee2e2;border:2px solid #dc2626;border-radius:8px;padding:12px;margin:9px 0"><p style="color:#b91c1c;font-weight:900;margin-bottom:5px">❌ Pedido no disponible</p><p style="font-size:.84rem;color:#555">Motivo: <strong>%s</strong></p></div>' % motivo_txt

            confirmar_box = ""
            hora_sp  = '<span style="color:#16a34a;font-weight:800">⏰ Llega: %s</span>' % p["hora_entrega"] if p["hora_entrega"] else ""
            ficha_sp = '<span class="ped-ficha">Ficha #%s</span>' % fch if fch else ""
            mid_tk   = "tk_%d" % p["id"]
            modales += """
<div class="overlay" id="%s">
  <div class="modal ancho">
    <button class="modal-x" onclick="cerrarModal('%s')">✕</button>
    <div class="modal-titulo">🧾 Comprobante</div>
    %s
    <div style="display:flex;gap:9px;margin-top:12px">
      <button class="btn btn-mo" style="flex:1;justify-content:center" onclick="imprimirTicket('%s')">🖨️ Imprimir</button>
      <a href="/descargar/%d" class="btn btn-ve" style="flex:1;justify-content:center">⬇️ Descargar</a>
    </div>
  </div>
</div>""" % (mid_tk, mid_tk, hacer_ticket(p), mid_tk, p["id"])

            n_items = len(json.loads(p["items"] or "[]"))
            items_html += """<div class="ped-card" style="%s">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px">
    <strong>🍊 Pedido #%d — %d producto(s)</strong>%s%s
  </div>
  %s%s
  <div class="ped-meta">
    <span>👤 %s</span><span>📱 %s</span><span>📍 %s</span>
    <span style="color:var(--mo);font-weight:800">%s</span>
    <span>%s</span>%s
  </div>
  <div style="margin-top:10px;display:flex;gap:7px;flex-wrap:wrap">
    <button class="btn btn-az" style="font-size:.81rem;padding:5px 12px" onclick="abrirModal('%s')">🧾 Comprobante</button>
    <a href="/descargar/%d" class="btn btn-do" style="font-size:.81rem;padding:5px 12px">⬇️ Descargar</a>
  </div>
</div>""" % (borde, p["id"], n_items, bdg, ficha_sp,
             env_banner, confirmar_box,
             p["nombre_cliente"], p["celular"], p["direccion"],
             fmt(p["total"]), p["fecha"], hora_sp, mid_tk, p["id"])

    if peds is not None:
        if peds:
            resultado = '<div style="background:#1a1a1a;border-radius:var(--r);padding:20px;border:2px solid #440000;margin-top:16px"><h2 style="font-size:1.1rem;font-weight:900;color:var(--mo);margin-bottom:14px">📦 Tus Pedidos — %s (%d)</h2>%s</div>' % (celular, len(peds), items_html)
        else:
            resultado = '<div class="alerta alerta-in" style="margin-top:16px;text-align:center">No hay pedidos para <strong>%s</strong>.</div>' % celular
    else:
        resultado = ""

    return nav("mis_pedidos", c) + """
<div class="wrap">
  <div class="hero">
    <h1>📦 Seguimiento de Pedidos</h1>
    <p>Ingresa tu celular para ver el estado de tus pedidos</p>
  </div>
  <div class="panel" style="max-width:480px;margin:0 auto">
    %s
    <form method="POST">
      <div class="fg"><label>📱 Tu Número de Celular</label>
        <input type="text" name="celular" value="%s" placeholder="8888-8888" required></div>
      <button type="submit" class="btn btn-mo btn-full">🔍 Buscar Mis Pedidos</button>
    </form>
  </div>
  %s
</div>%s
""" % (alerta(msg,"ok"), celular or "", resultado, modales) + PIE + JS_CARRITO + "</body></html>"


@app.route("/confirmar/<int:pid>/<accion>/<celular>")
def confirmar(pid, accion, celular):
    db = get_db()
    if accion == "aceptar":
        db.execute("UPDATE pedidos SET confirmacion='aceptado',estado='Confirmado' WHERE id=?",(pid,))
        msg = "✅ Pedido #%d confirmado." % pid
    else:
        db.execute("UPDATE pedidos SET confirmacion='cancelado',estado='Cancelado' WHERE id=?",(pid,))
        msg = "❌ Pedido #%d cancelado." % pid
    db.commit(); db.close()
    return redirect(url_for("mis_pedidos", celular=celular, msg=msg))


@app.route("/descargar/<int:pid>")
def descargar(pid):
    db = get_db()
    p  = db.execute("SELECT * FROM pedidos WHERE id=?",(pid,)).fetchone()
    db.close()
    if not p: return redirect(url_for("mis_pedidos"))
    try: items = json.loads(p["items"])
    except: items = []
    ln = ["="*46,"  MERCADO FRUTAS FRESCAS","  COMPROBANTE DE PEDIDO","="*46,
          "  Pedido: #%d" % p["id"],
          "  Ficha:  %s" % (p["ficha"] or "-"),
          "  Fecha:  %s" % p["fecha"],"-"*46,
          "  Cliente: %s" % p["nombre_cliente"],
          "  Celular: %s" % p["celular"],
          "  Dir:     %s" % p["direccion"],"-"*46,"  FRUTAS:"]
    for it in items:
        sub = float(it["precio"]) * int(it["qty"])
        ln.append("  %s x%d %s = %s" % (it["nombre"][:18], it["qty"], it.get("unidad",""), fmt(sub)))
    ln += ["-"*46,"  Subtotal: %s" % fmt(p["subtotal"])]
    if float(p["envio"] or 0) > 0:
        ln.append("  Envio:    + %s" % fmt(p["envio"]))
    ln += ["  TOTAL:   %s" % fmt(p["total"]),"  Pago: Contra entrega","-"*46,"  Gracias! 🍊","="*46]
    return Response("\n".join(ln), mimetype="text/plain",
        headers={"Content-Disposition":"attachment; filename=pedido_%d.txt" % pid})


# ═══════════════════════════════════════════════════════
# RUTA: ADMIN
# ═══════════════════════════════════════════════════════
@app.route("/admin")
def admin_panel():
    if not session.get("admin"): return redirect(url_for("admin_login"))
    db    = get_db()
    peds  = db.execute("SELECT * FROM pedidos ORDER BY id DESC").fetchall()
    prods = db.execute("SELECT * FROM productos ORDER BY id DESC").fetchall()
    db.close()
    return render_admin(peds, prods)


def render_admin(peds, prods, grafica=None, msg="", tipo="ok"):
    c = cfg()
    activos  = [p for p in peds if p["estado"] in ("Pendiente","Aprobado","Confirmado","En Espera")]
    enviados = [p for p in peds if p["estado"] == "Enviado"]
    ingresos = sum(p["total"] for p in peds if p["estado"] != "Cancelado")

    stats_html = """<div class="stats">
  <div class="stat"><div class="stat-n">%d</div><div class="stat-l">Total</div></div>
  <div class="stat"><div class="stat-n" style="color:#f5a623">%d</div><div class="stat-l">Pendientes</div></div>
  <div class="stat"><div class="stat-n" style="color:#f5a623">%d</div><div class="stat-l">En Espera Pago</div></div>
  <div class="stat"><div class="stat-n" style="color:#22c55e">%d</div><div class="stat-l">Pagados</div></div>
  <div class="stat"><div class="stat-n" style="color:#ef4444">%d</div><div class="stat-l">Negados</div></div>
  <div class="stat"><div class="stat-n">%d</div><div class="stat-l">Productos</div></div>
  <div class="stat"><div class="stat-n" style="font-size:.95rem">%s</div><div class="stat-l">Ingresos</div></div>
</div>""" % (len(peds),
             sum(1 for p in peds if p["estado"]=="Pendiente"),
             sum(1 for p in peds if p["estado"]=="En Espera"),
             sum(1 for p in peds if p["estado"]=="Pagado"),
             sum(1 for p in peds if p["estado"]=="Negado"),
             len(prods), fmt(ingresos))

    filas_ped = ""; modales_ped = ""
    for p in sorted(activos, key=lambda x: x["id"]):
        envio  = float(p["envio"] or 0)
        fch    = p["ficha"] or "—"
        n_it   = len(json.loads(p["items"] or "[]"))
        mid_o  = "ao_%d" % p["id"]
        mid_e  = "ae_%d" % p["id"]
        tk     = hacer_ticket(p, admin=True)
        it_tbl = tabla_items(p["items"] or "[]")

        modales_ped += """
<div class="overlay" id="%s">
  <div class="modal ancho">
    <button class="modal-x" onclick="cerrarModal('%s')">✕</button>
    <div class="modal-titulo">📋 Pedido #%d</div>
    <div style="font-size:.82rem;color:#888;margin-bottom:11px">
      👤 <strong>%s</strong> · 📱 %s<br>📍 %s%s
    </div>
    %s%s
    <button class="btn btn-mo btn-full" style="margin-top:12px" onclick="imprimirTicket('%s')">🖨️ Imprimir</button>
  </div>
</div>""" % (mid_o, mid_o, p["id"],
             p["nombre_cliente"], p["celular"], p["direccion"],
             (" · " + p["referencia"]) if p["referencia"] else "",
             it_tbl, tk, mid_o)

        sel_p = " selected" if p["estado"]=="Pendiente" else ""
        sel_a = " selected" if p["estado"]=="Aprobado" else ""
        sel_n = " selected" if p["estado"]=="Negado" else ""
        mot_display = "block" if p["estado"]=="Negado" else "none"
        mot_texto = p["motivo"] or ""
        modales_ped += (
            '<div class="overlay" id="' + mid_e + '">'
            '<div class="modal">'
            '<button class="modal-x" onclick="cerrarModal(\'' + mid_e + '\')">✕</button>'
            '<div class="modal-titulo">✏️ Editar Pedido #' + str(p["id"]) + '</div>'
            '<form method="POST" action="/admin/upd-pedido">'
            '<input type="hidden" name="pedido_id" value="' + str(p["id"]) + '">'
            '<div class="fg"><label>Estado del Pedido</label>'
            '<select name="estado" id="est_sel_' + str(p["id"]) + '" onchange="toggleMotivo(' + str(p["id"]) + ',this.value)">'
            '<option value="Pendiente"' + sel_p + '>⏳ Pendiente</option>'
            '<option value="Aprobado"' + sel_a + '>✅ Aprobado</option>'
            '<option value="Negado"' + sel_n + '>❌ Negado</option>'
            '</select></div>'
            '<div class="fg" id="motivo_box_' + str(p["id"]) + '" style="display:' + mot_display + '">'
            '<label>Motivo del rechazo</label>'
            '<textarea name="motivo" placeholder="Explica por qué se niega...">' + mot_texto + '</textarea>'
            '</div>'
            '<button type="submit" class="btn btn-mo btn-full">💾 Guardar</button>'
            '</form></div></div>'
        )

        filas_ped += """<tr>
  <td><strong>#%d</strong></td>
  <td><span class="ped-ficha">%s</span></td>
  <td><strong>%s</strong><br><span style="font-size:.73rem;color:#888">📱 %s</span></td>
  <td><span style="background:#1a0000;color:#cc0000;border:1px solid #ff2222;border-radius:20px;padding:2px 8px;font-size:.73rem;font-weight:800">%d items</span></td>
  <td style="color:var(--mo);font-weight:900">%s</td>
  <td>%s</td>
  <td style="display:flex;gap:5px;flex-wrap:wrap">
    <button class="btn btn-do" style="font-size:.76rem;padding:4px 9px" onclick="abrirModal('%s')">✏️</button>
    <button class="btn btn-az" style="font-size:.76rem;padding:4px 9px" onclick="abrirModal('%s')">📋</button>
  </td>
</tr>""" % (p["id"], fch, p["nombre_cliente"], p["celular"],
            n_it, fmt(p["total"]), bdg_estado(p["estado"]), mid_e, mid_o)

    filas_env = ""; modales_env = ""
    for p in sorted(enviados, key=lambda x: x["id"], reverse=True):
        mid_v = "env_%d" % p["id"]
        tk_e  = hacer_ticket(p, admin=True)
        it_e  = tabla_items(p["items"] or "[]")
        modales_env += """
<div class="overlay" id="%s">
  <div class="modal ancho">
    <button class="modal-x" onclick="cerrarModal('%s')">✕</button>
    <div class="modal-titulo">🚚 Enviado #%d</div>
    <div style="font-size:.82rem;color:#888;margin-bottom:11px">👤 <strong>%s</strong> · 📱 %s</div>
    %s%s
    <button class="btn btn-mo btn-full" style="margin-top:12px" onclick="imprimirTicket('%s')">🖨️ Imprimir</button>
  </div>
</div>""" % (mid_v, mid_v, p["id"], p["nombre_cliente"], p["celular"], it_e, tk_e, mid_v)

        filas_env += """<tr style="opacity:.85">
  <td><strong>#%d</strong></td>
  <td><span class="ped-ficha">%s</span></td>
  <td><strong>%s</strong></td>
  <td style="color:var(--mo);font-weight:900">%s</td>
  <td style="font-size:.78rem;color:#888">%s</td>
  <td><button class="btn btn-mo" style="font-size:.76rem;padding:4px 9px" onclick="abrirModal('%s')">📋</button></td>
</tr>""" % (p["id"], p["ficha"] or "—", p["nombre_cliente"],
            fmt(p["total"]), p["fecha"], mid_v)

    cats_opts = "".join('<option value="%s">%s</option>' % (cat,cat)
                        for cat in ["Frutas","Tropicales","Cítricos","Berries","Verduras","Otros"])
    filas_prod = ""; modales_prod = ""
    for p in prods:
        mid_ep = "ep_%d" % p["id"]
        co = "".join('<option value="%s"%s>%s</option>' % (cat," selected" if p["categoria"]==cat else "",cat)
                     for cat in ["Frutas","Tropicales","Cítricos","Berries","Verduras","Otros"])
        modales_prod += """
<div class="overlay" id="%s">
  <div class="modal">
    <button class="modal-x" onclick="cerrarModal('%s')">✕</button>
    <div class="modal-titulo">✏️ Editar Producto</div>
    <form method="POST" action="/admin/edit-prod">
      <input type="hidden" name="pid" value="%d">
      <div class="fg"><label>Nombre</label><input type="text" name="nombre" value="%s" required></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
        <div class="fg"><label>Precio (₡)</label><input type="number" name="precio" value="%g" required min="0" step="50"></div>
        <div class="fg"><label>Categoría</label><select name="categoria">%s</select></div>
        <div class="fg"><label>Unidad de venta</label><input type="text" name="unidad" value="%s" placeholder="kg, unidad, racimo"></div>
      </div>
      <div class="fg"><label>Descripción</label><textarea name="descripcion">%s</textarea></div>
      <button type="submit" class="btn btn-mo btn-full">💾 Guardar</button>
    </form>
  </div>
</div>""" % (mid_ep, mid_ep, p["id"], p["nombre"], p["precio"], co,
             p["unidad"] or "", p["descripcion"] or "")

        filas_prod += """<tr>
  <td><strong>%s</strong><div style="font-size:.73rem;color:#888">%s · %s</div></td>
  <td><span style="background:#1a0000;color:#cc0000;border:1px solid #ff2222;border-radius:20px;padding:2px 8px;font-size:.73rem;font-weight:800">%s</span></td>
  <td style="color:var(--mo);font-weight:900">%s</td>
  <td style="display:flex;gap:5px">
    <button class="btn btn-do" style="font-size:.78rem;padding:4px 9px" onclick="abrirModal('%s')">✏️</button>
    <a href="/admin/del-prod/%d" onclick="return confirm('¿Eliminar?')" class="btn btn-ro" style="font-size:.78rem;padding:4px 9px">🗑️</a>
  </td>
</tr>""" % (p["nombre"], p["unidad"] or "", (p["descripcion"] or "")[:28],
            p["categoria"], fmt(p["precio"]), mid_ep, p["id"])

    nom_actual  = c.get("nombre","Mercado Frutas Frescas")
    logo_actual = c.get("logo","")
    if logo_actual:
        if ";" in logo_actual:
            lm, lb = logo_actual.split(";", 1)
        else:
            lm, lb = "image/jpeg", logo_actual
        logo_prev = '<img src="data:%s;base64,%s" class="logo-prev">' % (lm, lb)
    else:
        logo_prev = ""
    on = cfg().get("activo","1") == "1"
    estado_box = '<div class="alerta alerta-ok">✅ MERCADO ABIERTO</div>' if on else '<div class="alerta alerta-er">🔒 MERCADO CERRADO</div>'
    btn_toggle = ""
    master_box = ""
    if session.get("master"):
        btn_toggle = '<a href="/admin/toggle" class="btn %s btn-full" style="margin-bottom:14px">%s</a>' % (
            ("btn-ro","🔒 Cerrar Mercado") if on else ("btn-ve","✅ Abrir Mercado"))
        master_box = '<div class="alerta alerta-in"><p style="font-weight:900;margin-bottom:9px">🔑 Panel Maestro</p><a href="/reset-frutas-2024" class="btn btn-ro">🗑️ Reset del Mes</a></div>'
    elif session.get("admin"):
        master_box = '<div style="background:#1a1a1a;border:2px solid #440000;border-radius:var(--r);padding:16px;margin-bottom:16px"><p style="font-weight:900;color:var(--mo);margin-bottom:9px">🗑️ Resetear Mes</p><a href="/reset-frutas-2024" class="btn btn-ro">🗑️ Reset del Mes</a></div>'

    tab_config = """<div class="panel">
  <h2>🎨 Configuración del Mercado</h2>
  %s%s%s
  <form method="POST" action="/admin/config" enctype="multipart/form-data">
    %s
    <div class="fg"><label>Nombre del Mercado</label>
      <input type="text" name="nombre" value="%s" required></div>
    <div class="fg"><label>Logo</label>
      <input type="file" name="logo" accept="image/*"></div>
    <button type="submit" class="btn btn-ve btn-full">💾 Guardar</button>
  </form>
</div>""" % (estado_box, btn_toggle, master_box, logo_prev, nom_actual)

    graf_html = ('<div style="text-align:center"><img src="data:image/png;base64,%s" style="max-width:100%%;border-radius:var(--r)"></div>' % grafica) if grafica else '<p style="text-align:center;color:#aaa;padding:20px">Haz clic en Generar Gráfica.</p>'

    html = nav("admin_panel", c)
    html += "<div class='wrap'>"
    html += "<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;flex-wrap:wrap;gap:10px'>"
    html += "<h1 style='font-size:1.9rem;font-weight:900;color:var(--mo)'>⚙️ Panel Admin</h1>"
    html += "<a href='/admin/logout' class='btn btn-ro'>🚪 Salir</a></div>"
    html += alerta(msg, tipo)
    html += banner_activos(activos)
    html += stats_html
    html += "<div style='display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:18px;flex-wrap:wrap'>"
    html += "  <div style='display:flex;gap:7px;flex-wrap:wrap'>"
    html += "    <button class='btn btn-mo' onclick=\"mostrarTab('pedidos')\">📋 Pedidos</button>"
    html += "    <button class='btn' onclick=\"mostrarTab('enviados')\" style='background:linear-gradient(135deg,#cc0000,#ff2222);color:#fff'>🚚 Enviados</button>"
    html += "    <button class='btn btn-do' onclick=\"mostrarTab('productos')\">🍊 Productos</button>"
    html += "    <button class='btn btn-ve' onclick=\"mostrarTab('config')\">⚙️ Config</button>"
    html += "    <button class='btn btn-az' onclick=\"mostrarTab('stats')\">📊 Stats</button>"
    html += "  </div>"
    html += "  <a href='/admin/encargos' style='background:linear-gradient(135deg,#cc0000,#ff4444);color:#8b0000;padding:12px 22px;border-radius:8px;font-weight:900;font-size:.95rem;text-decoration:none;border:none;display:inline-flex;align-items:center;gap:7px;white-space:nowrap;font-family:Nunito,sans-serif'>🖨️ Encargos del Día</a>"
    html += "</div>"

    html += "<div id='tab_pedidos'>"
    html += "<div class='panel'><h2>📋 Pedidos Activos (%d)</h2><div class='tabla-wrap'><table><thead><tr><th>#</th><th>Ficha</th><th>Cliente</th><th>Items</th><th>Total</th><th>Estado</th><th>Acciones</th></tr></thead><tbody>%s</tbody></table></div></div>" % (
        len(activos), filas_ped or '<tr><td colspan="8" style="text-align:center;padding:18px;color:#aaa">No hay pedidos activos.</td></tr>')
    html += "</div>"

    espera_peds  = [p for p in peds if p["estado"] == "En Espera"]
    pagados_peds = [p for p in peds if p["estado"] == "Pagado"]

    if espera_peds:
        nombres = ", ".join("<strong>%s</strong> (%s)" % (p["nombre_cliente"], fmt(p["total"])) for p in espera_peds)
        deudores_banner = '<div class="alerta alerta-in" style="margin-bottom:14px">⚠️ Pendientes de pago: ' + nombres + '</div>'
    else:
        deudores_banner = '<div class="alerta alerta-ok">✅ Todos los pedidos aprobados han sido pagados.</div>'

    filas_espera = ""
    for p in espera_peds:
        filas_espera += (
            "<tr style='background:#1a0a00'>"
            "<td><strong style='color:#f5a623'>#%d</strong></td>"
            "<td><span class='ped-ficha'>%s</span></td>"
            "<td><strong>%s</strong><br><span style='font-size:.73rem;color:#c8a415'>%s</span></td>"
            "<td style='color:#f5c518;font-weight:900'>%s</td>"
            "<td style='color:#c8a415;font-size:.8rem'>%s</td>"
            "<td><a href='/admin/marcar-pagado/%d' class='btn btn-ve' style='font-size:.8rem;padding:5px 12px'>Pagado</a></td>"
            "</tr>"
        ) % (p["id"], p["ficha"] or "—", p["nombre_cliente"], p["celular"],
             fmt(p["total"]), p["fecha"], p["id"])

    filas_pagados = ""
    for p in pagados_peds:
        filas_pagados += (
            "<tr>"
            "<td><strong>#%d</strong></td>"
            "<td><span class='ped-ficha'>%s</span></td>"
            "<td><strong>%s</strong></td>"
            "<td style='color:#22c55e;font-weight:900'>%s</td>"
            "<td style='color:#c8a415;font-size:.8rem'>%s</td>"
            "</tr>"
        ) % (p["id"], p["ficha"] or "—", p["nombre_cliente"], fmt(p["total"]), p["fecha"])

    html += (
        "<div id='tab_espera' style='display:none'>"
        "<div class='panel'><h2>En Espera del Pago (%d)</h2>%s"
        "<div class='tabla-wrap'><table><thead><tr><th>#</th><th>Ficha</th><th>Cliente</th><th>Total</th><th>Fecha</th><th>Accion</th></tr></thead>"
        "<tbody>%s</tbody></table></div></div>"
        "<div class='panel' style='margin-top:16px'><h2>Pagados (%d)</h2>"
        "<div class='tabla-wrap'><table><thead><tr><th>#</th><th>Ficha</th><th>Cliente</th><th>Total</th><th>Fecha</th></tr></thead>"
        "<tbody>%s</tbody></table></div></div>"
        "</div>"
    ) % (
        len(espera_peds), deudores_banner,
        filas_espera or "<tr><td colspan='6' style='text-align:center;padding:18px;color:#c8a415'>No hay pedidos en espera.</td></tr>",
        len(pagados_peds),
        filas_pagados or "<tr><td colspan='5' style='text-align:center;padding:18px;color:#c8a415'>Sin pagos aun.</td></tr>"
    )

    html += "<div id='tab_enviados' style='display:none'>"
    html += "<div class='env-section'><h2>🚚 Historial de Enviados (%d)</h2><div class='tabla-wrap'><table><thead><tr><th>#</th><th>Ficha</th><th>Cliente</th><th>Total</th><th>Fecha</th><th>Ver</th></tr></thead><tbody>%s</tbody></table></div></div>" % (
        len(enviados), filas_env or '<tr><td colspan="6" style="text-align:center;padding:18px;color:#aaa">Sin enviados.</td></tr>')
    html += modales_env + "</div>"

    html += "<div id='tab_productos' style='display:none'>"
    html += "<div class='ag'>"
    html += "<div class='panel'><h2>➕ Agregar Producto</h2><form method='POST' action='/admin/add-prod' enctype='multipart/form-data'>"
    html += "<div class='fg'><label>Nombre *</label><input type='text' name='nombre' required placeholder='Mango, Piña...'></div>"
    html += "<div style='display:grid;grid-template-columns:1fr 1fr;gap:10px'>"
    html += "<div class='fg'><label>Precio (₡) *</label><input type='number' name='precio' required min='0' step='50'></div>"
    html += "<div class='fg'><label>Categoría</label><select name='categoria'>%s</select></div>" % cats_opts
    html += "<div class='fg'><label>Unidad</label><input type='text' name='unidad' placeholder='kg, unidad, racimo, caja'></div>"
    html += "</div>"
    html += "<div class='fg'><label>Descripción</label><textarea name='descripcion' placeholder='Describe la fruta...'></textarea></div>"
    html += "<div class='fg'><label>Imagen</label><input type='file' name='imagen' accept='image/*'></div>"
    html += "<button type='submit' class='btn btn-ve btn-full'>✅ Agregar</button></form></div>"
    html += "<div class='panel'><h2>🍊 Catálogo</h2><div class='tabla-wrap'><table><thead><tr><th>Producto</th><th>Categoría</th><th>Precio</th><th>Acciones</th></tr></thead><tbody>%s</tbody></table></div></div>" % (
        filas_prod or '<tr><td colspan="4" style="text-align:center;padding:18px;color:#aaa">Sin productos.</td></tr>')
    html += "</div></div>"

    html += "<div id='tab_config' style='display:none'>" + tab_config + "</div>"
    html += "<div id='tab_stats' style='display:none'><div class='panel'><h2>📊 Estadísticas</h2>"
    html += "<div style='text-align:center;margin-bottom:14px'><a href='/admin/grafica' class='btn btn-mo'>📈 Generar Gráfica</a></div>"
    html += graf_html + "</div></div>"
    html += "</div>"
    html += modales_ped + modales_prod
    html += PIE + JS_CARRITO + "</body></html>"
    return html


@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    err = ""
    if request.method == "POST":
        pw = request.form.get("password","")
        if pw == MASTER_PASS:
            session["admin"] = True; session["master"] = True
            return redirect(url_for("admin_panel"))
        elif pw == ADMIN_PASS:
            session["admin"] = True; session["master"] = False
            return redirect(url_for("admin_panel"))
        err = "❌ Contraseña incorrecta."
    return nav("admin_panel") + """
<div class="login-box">
  <h2>🍊 Panel Admin</h2>
  %s
  <form method="POST">
    <div class="fg"><label>Contraseña</label>
      <input type="password" name="password" placeholder="••••••••" required autofocus></div>
    <button type="submit" class="btn btn-mo btn-full">🍊 Ingresar</button>
  </form>
</div>""" % alerta(err,"er") + PIE + JS_CARRITO + "</body></html>"


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("tienda"))


@app.route("/admin/toggle")
def admin_toggle():
    if not session.get("admin"): return redirect(url_for("admin_login"))
    db = get_db()
    r  = db.execute("SELECT valor FROM configuracion WHERE clave='activo'").fetchone()
    nuevo = "0" if (r and r["valor"]=="1") else "1"
    db.execute("INSERT OR REPLACE INTO configuracion VALUES('activo',?)",(nuevo,))
    db.commit(); db.close()
    msg = "✅ Mercado abierto." if nuevo=="1" else "🔒 Mercado cerrado."
    return redirect(url_for("admin_panel", msg=msg, tipo="ok"))


@app.route("/admin/config", methods=["POST"])
def admin_config():
    if not session.get("admin"): return redirect(url_for("admin_login"))
    nombre = request.form.get("nombre","").strip() or "Mercado Frutas Frescas"
    db = get_db()
    db.execute("INSERT OR REPLACE INTO configuracion VALUES('nombre',?)",(nombre,))
    if "logo" in request.files:
        f = request.files["logo"]
        if f and f.filename:
            raw = f.read()
            mime = f.mimetype or "image/jpeg"
            if not mime.startswith("image/"): mime = "image/jpeg"
            if len(raw) < 2_000_000:
                logo_data = mime + ";" + base64.b64encode(raw).decode()
                db.execute("INSERT OR REPLACE INTO configuracion VALUES('logo',?)",
                           (logo_data,))
    db.commit(); db.close()
    return redirect(url_for("admin_panel", msg="✅ Configuración guardada.", tipo="ok"))


@app.route("/admin/add-prod", methods=["POST"])
def admin_add_prod():
    if not session.get("admin"): return redirect(url_for("admin_login"))
    f = request.form; img = None
    if "imagen" in request.files:
        fi = request.files["imagen"]
        if fi and fi.filename:
            raw = fi.read()
            mime = fi.mimetype or "image/jpeg"
            if not mime.startswith("image/"): mime = "image/jpeg"
            if len(raw) < 2_000_000:
                img = mime + ";" + base64.b64encode(raw).decode()
    db = get_db()
    db.execute("INSERT INTO productos(nombre,precio,descripcion,unidad,categoria,imagen) VALUES(?,?,?,?,?,?)",
               (f["nombre"].strip(), float(f["precio"]),
                f.get("descripcion","").strip(),
                f.get("unidad","unidad").strip(),
                f.get("categoria","Frutas"), img))
    db.commit(); db.close()
    return redirect(url_for("admin_panel", msg="✅ Producto agregado.", tipo="ok"))


@app.route("/admin/edit-prod", methods=["POST"])
def admin_edit_prod():
    if not session.get("admin"): return redirect(url_for("admin_login"))
    f = request.form
    db = get_db()
    db.execute("UPDATE productos SET nombre=?,precio=?,descripcion=?,unidad=?,categoria=? WHERE id=?",
               (f["nombre"].strip(), float(f["precio"]),
                f.get("descripcion","").strip(),
                f.get("unidad","unidad").strip(),
                f.get("categoria","Frutas"), f["pid"]))
    if "imagen" in request.files:
        fi = request.files["imagen"]
        if fi and fi.filename:
            raw = fi.read()
            mime = fi.mimetype or "image/jpeg"
            if not mime.startswith("image/"): mime = "image/jpeg"
            if len(raw) < 2_000_000:
                img = mime + ";" + base64.b64encode(raw).decode()
                db.execute("UPDATE productos SET imagen=? WHERE id=?", (img, f["pid"]))
    db.commit(); db.close()
    return redirect(url_for("admin_panel", msg="✅ Producto actualizado.", tipo="ok"))


@app.route("/admin/del-prod/<int:pid>")
def admin_del_prod(pid):
    if not session.get("admin"): return redirect(url_for("admin_login"))
    db = get_db()
    db.execute("DELETE FROM productos WHERE id=?",(pid,))
    db.commit(); db.close()
    return redirect(url_for("admin_panel", msg="🗑️ Producto eliminado.", tipo="ok"))


@app.route("/admin/upd-pedido", methods=["POST"])
def admin_upd_pedido():
    if not session.get("admin"): return redirect(url_for("admin_login"))
    f      = request.form
    pid    = f["pedido_id"]
    est    = f["estado"]
    motivo = f.get("motivo","").strip()
    if est == "Aprobado": est = "En Espera"
    db     = get_db()
    db.execute("UPDATE pedidos SET estado=?,motivo=? WHERE id=?", (est,motivo,pid))
    db.commit(); db.close()
    if est == "En Espera": msg = "✅ Pedido #%s aprobado — en espera del pago." % pid
    elif est == "Negado":  msg = "❌ Pedido #%s negado." % pid
    else:                  msg = "⏳ Pedido #%s en pendiente." % pid
    return redirect(url_for("admin_panel", msg=msg, tipo="ok"))


@app.route("/admin/grafica")
def admin_grafica():
    if not session.get("admin"): return redirect(url_for("admin_login"))
    db    = get_db()
    peds  = db.execute("SELECT * FROM pedidos").fetchall()
    prods = db.execute("SELECT * FROM productos ORDER BY id DESC").fetchall()
    db.close()
    ventas = {}
    for p in peds:
        try:
            for it in json.loads(p["items"]):
                ventas[it["nombre"]] = ventas.get(it["nombre"],0) + int(it["qty"])
        except: pass
    if not ventas:
        return redirect(url_for("admin_panel", msg="No hay datos para graficar.", tipo="in"))
    noms  = list(ventas.keys())
    cants = [ventas[n] for n in noms]
    cols  = ["#cc0000","#ff2222","#cc0000","#ff4444","#9333ea","#a855f7","#c084fc","#d97706","#fbbf24","#e9d5ff"][:len(noms)]
    fig, (ax1,ax2) = plt.subplots(1,2,figsize=(13,5))
    fig.patch.set_facecolor("#f5f0ff")
    ax1.set_facecolor("#fdf8ff")
    bars = ax1.bar(range(len(noms)), cants, color=cols, edgecolor="#440000", linewidth=1.5)
    ax1.set_xticks(range(len(noms)))
    ax1.set_xticklabels([n[:12] for n in noms], rotation=28, ha="right", color="#1a0033", fontsize=9)
    ax1.set_title("Frutas más pedidas", color="#cc0000", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Unidades", color="#8a6aaa")
    for sp in ax1.spines.values(): sp.set_color("#440000")
    for b,v in zip(bars,cants):
        ax1.text(b.get_x()+b.get_width()/2, b.get_height()+.05, str(v), ha="center", color="#cc0000", fontsize=10, fontweight="bold")
    ax2.set_facecolor("#fdf8ff")
    wedges,texts,autotexts = ax2.pie(cants, colors=cols, autopct="%1.1f%%", startangle=90,
                                      pctdistance=.8, wedgeprops={"edgecolor":"#f5f0ff","linewidth":2})
    for t in texts: t.set_color("#1a0033")
    for t in autotexts: t.set_color("white"); t.set_fontweight("bold")
    ax2.set_title("Distribución", color="#cc0000", fontsize=12, fontweight="bold")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", facecolor="#f5f0ff", dpi=110)
    buf.seek(0)
    g64 = base64.b64encode(buf.read()).decode()
    plt.close()
    db2   = get_db()
    peds2 = db2.execute("SELECT * FROM pedidos ORDER BY id DESC").fetchall()
    prods2= db2.execute("SELECT * FROM productos ORDER BY id DESC").fetchall()
    db2.close()
    return render_admin(peds2, prods2, g64)


# ═══════════════════════════════════════════════════════
# RUTA: ENCARGOS DEL DÍA
# ═══════════════════════════════════════════════════════
@app.route("/admin/encargos")
def admin_encargos():
    if not session.get("admin"): return redirect(url_for("admin_login"))
    c    = cfg()
    nom  = c.get("nombre","Mercado Frutas Frescas")
    db   = get_db()
    peds = db.execute("SELECT * FROM pedidos WHERE estado NOT IN ('Negado','Cancelado') ORDER BY id ASC").fetchall()
    db.close()
    hoy       = datetime.now().strftime("%d/%m/%Y")
    total_dia = sum(p["total"] for p in peds)

    def hacer_bloque(p):
        try: items = json.loads(p["items"])
        except: items = []
        rows = ""
        for it in items:
            sub = float(it["precio"]) * int(it["qty"])
            rows += """<tr>
  <td style="padding:3px 8px;font-size:.74rem;border-bottom:1px solid #ddd">%s</td>
  <td style="padding:3px 8px;font-size:.74rem;text-align:center;border-bottom:1px solid #ddd">%d %s</td>
  <td style="padding:3px 8px;font-size:.74rem;text-align:right;font-weight:800;border-bottom:1px solid #ddd">%s</td>
</tr>""" % (it["nombre"][:18], it["qty"], it.get("unidad",""), fmt(sub))
        notas = ('<div style="font-size:.68rem;color:#555;padding:3px 8px;font-style:italic">📝 %s</div>' % p["notas"]) if p["notas"] else ""
        return """<div style="border:2px solid #222;border-radius:16px;overflow:hidden;background:#fff;height:100%%">
  <div style="background:#111;padding:8px 12px;text-align:center;border-radius:14px 14px 0 0">
    <div style="font-size:.85rem;font-weight:900;color:#fff">🍊 %s</div>
    <div style="font-size:.65rem;color:#ccc;margin-top:1px">ENCARGOS DEL DÍA — %s</div>
  </div>
  <div style="background:#f5f5f5;padding:5px 12px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #ddd">
    <strong style="color:#111;font-size:.8rem">Pedido #%d</strong>
    <span style="background:#222;color:#fff;border-radius:20px;padding:1px 9px;font-size:.65rem;font-weight:900">Ficha: %s</span>
  </div>
  <div style="padding:5px 12px;border-bottom:1px solid #eee;font-size:.76rem;color:#111">
    <div><strong>%s</strong> &nbsp;·&nbsp; 📱 %s</div>
    <div style="color:#666;font-size:.68rem">%s · %s</div>
  </div>
  <div style="padding:0 0 4px 0">
    <div style="padding:4px 12px;background:#f0f0f0;font-size:.68rem;font-weight:900;color:#333;text-transform:uppercase;letter-spacing:.5px;border-bottom:1px solid #ddd">Productos</div>
    <table style="width:100%%;border-collapse:collapse;color:#111">
      <thead><tr>
        <th style="padding:3px 8px;text-align:left;font-size:.68rem;color:#666;font-weight:700;border-bottom:1px solid #ddd">Producto</th>
        <th style="padding:3px 8px;text-align:center;font-size:.68rem;color:#666;font-weight:700;border-bottom:1px solid #ddd">Cant.</th>
        <th style="padding:3px 8px;text-align:right;font-size:.68rem;color:#666;font-weight:700;border-bottom:1px solid #ddd">Subtotal</th>
      </tr></thead>
      <tbody>%s</tbody>
    </table>
    %s
  </div>
  <div style="padding:7px 12px;background:#111;border-radius:0 0 14px 14px;display:flex;justify-content:space-between;align-items:center">
    <span style="font-size:.7rem;color:#aaa">💵 Pago al recoger</span>
    <strong style="color:#fff;font-size:.95rem">%s</strong>
  </div>
</div>""" % (nom, hoy,
             p["id"], p["ficha"] or "—",
             p["nombre_cliente"], p["celular"],
             p["fecha"], p["estado"],
             rows, notas, fmt(p["total"]))

    grid_rows = ""
    for i in range(0, len(peds), 2):
        b1 = hacer_bloque(peds[i])
        b2 = hacer_bloque(peds[i+1]) if i+1 < len(peds) else "<div></div>"
        grid_rows += """<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px;page-break-inside:avoid">
  %s
  %s
</div>""" % (b1, b2)

    if not peds:
        grid_rows = '<div style="text-align:center;padding:40px;color:#aaa"><div style="font-size:3rem">📋</div><p>No hay encargos hoy.</p></div>'
        total_html = ""
    else:
        total_html = """<div style="background:#111;border-radius:12px;padding:14px 20px;margin-top:12px;display:flex;justify-content:space-between;align-items:center;color:#fff;border:2px solid #333">
  <div><div style="font-weight:900;font-size:.95rem">📦 TOTAL DEL DÍA</div><div style="font-size:.75rem;color:#aaa">%d encargo(s)</div></div>
  <div style="font-size:1.5rem;font-weight:900">%s</div>
</div>""" % (len(peds), fmt(total_dia))

    return """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Encargos — %s</title>
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800;900&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Nunito',sans-serif;background:#0a0a0a;color:#f0f0f0;padding:16px}
.wrap{max-width:860px;margin:0 auto}
.top-bar{background:#111;border-radius:12px;padding:16px 20px;text-align:center;margin-bottom:16px;border:2px solid #333}
.top-bar h1{font-size:1.3rem;font-weight:900;color:#fff}
.top-bar p{color:#aaa;font-size:.82rem;margin-top:3px}
.acciones{display:flex;gap:10px;justify-content:center;margin-bottom:16px}
.btn-dl{background:#222;color:#fff;border:2px solid #555;border-radius:8px;padding:11px 28px;font-size:.95rem;font-weight:900;cursor:pointer;font-family:'Nunito',sans-serif;text-decoration:none;display:inline-block}
.btn-dl:hover{background:#333}
.btn-back{background:transparent;color:#aaa;border:2px solid #333;border-radius:8px;padding:11px 20px;font-size:.95rem;font-weight:900;text-decoration:none;display:inline-block}
@media print{
  .acciones{display:none!important}
  body{background:#fff!important;padding:6px;color:#000}
  @page{size:A4;margin:8mm}
}
</style>
</head>
<body>
<div class="wrap">
  <div class="top-bar">
    <h1>🍊 %s — Encargos del Día</h1>
    <p>%s &nbsp;·&nbsp; %d pedido(s) &nbsp;·&nbsp; Total: %s</p>
  </div>
  <div class="acciones">
    <a href="/admin/descargar-encargos" class="btn-dl">⬇️ Descargar PDF</a>
    <a href="/admin" class="btn-back">← Volver</a>
  </div>
  %s
  %s
</div>
</body>
</html>""" % (nom, nom, hoy, len(peds), fmt(total_dia), grid_rows, total_html)


@app.route("/reset-frutas-2024")
def reset_ver():
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    ingr  = db.execute("SELECT SUM(total) FROM pedidos WHERE estado!='Cancelado'").fetchone()[0] or 0
    env   = db.execute("SELECT COUNT(*) FROM pedidos WHERE estado='Enviado'").fetchone()[0]
    db.close()
    return """<!DOCTYPE html><html lang='es'><head><meta charset='UTF-8'>
<meta name='viewport' content='width=device-width,initial-scale=1.0'>
<title>Reset</title>
<link href='https://fonts.googleapis.com/css2?family=Nunito:wght@700;800;900&display=swap' rel='stylesheet'>
<style>*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Nunito',sans-serif;background:#f5f0ff;min-height:100vh;
  display:flex;align-items:center;justify-content:center;padding:20px}
.box{background:#1a1a1a;border:3px solid #cc0000;border-radius:12px;padding:38px;
  max-width:440px;width:100%%;text-align:center;box-shadow:0 8px 36px rgba(180,0,0,.18)}
h1{color:#dc2626;font-size:1.9rem;margin-bottom:6px}
.sub{color:#888;font-size:.83rem;margin-bottom:22px}
.fila{display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid #440000}
.val{color:#cc0000;font-weight:900}
.total{display:flex;justify-content:space-between;padding:13px 0;font-size:1.1rem;font-weight:900}
.verde{color:#cc0000;font-size:1.15rem}
.warn{background:#fef9c3;border:2px solid #ca8a04;border-radius:8px;padding:13px;margin:18px 0;color:#92400e;font-weight:800;font-size:.86rem}
.btns{display:flex;gap:11px;margin-top:18px}
.b-del{flex:1;background:linear-gradient(135deg,#dc2626,#ef4444);color:#fff;padding:12px;border-radius:8px;text-decoration:none;font-weight:900;font-size:.96rem}
.b-can{flex:1;background:#f5f0ff;color:#1a0033;padding:12px;border-radius:8px;text-decoration:none;font-weight:900;font-size:.96rem;border:2px solid #440000}
.fecha{color:#aaa;font-size:.73rem;margin-top:13px}</style></head><body>
<div class='box'>
  <div style='font-size:3.5rem;margin-bottom:14px'>⚠️</div>
  <h1>Resetear Mes</h1>
  <p class='sub'>Resumen antes de eliminar</p>
  <div class='fila'><span>📦 Total pedidos</span><span class='val'>%d</span></div>
  <div class='fila'><span>🚚 Enviados</span><span class='val'>%d</span></div>
  <div class='total'><span>💰 Ingresos del mes</span><span class='verde'>%s</span></div>
  <div class='warn'>⚠️ Esta acción borrará TODOS los pedidos. No se puede deshacer.</div>
  <div class='btns'>
    <a href='/reset-frutas-2024/ok' class='b-del'>🗑️ ELIMINAR TODO</a>
    <a href='/admin' class='b-can'>✕ Cancelar</a>
  </div>
  <p class='fecha'>%s</p>
</div></body></html>""" % (total, env, fmt(ingr), datetime.now().strftime("%d/%m/%Y %H:%M"))


@app.route("/reset-frutas-2024/ok")
def reset_ok():
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    ingr  = db.execute("SELECT SUM(total) FROM pedidos WHERE estado!='Cancelado'").fetchone()[0] or 0
    db.execute("DELETE FROM pedidos")
    db.commit(); db.close()
    return """<!DOCTYPE html><html lang='es'><head><meta charset='UTF-8'>
<meta name='viewport' content='width=device-width,initial-scale=1.0'>
<title>Reset OK</title>
<link href='https://fonts.googleapis.com/css2?family=Nunito:wght@700;800;900&display=swap' rel='stylesheet'>
<style>*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Nunito',sans-serif;background:#f5f0ff;min-height:100vh;
  display:flex;align-items:center;justify-content:center;padding:20px}
.box{background:#1a1a1a;border:3px solid #16a34a;border-radius:12px;padding:38px;
  max-width:440px;width:100%%;text-align:center;box-shadow:0 8px 36px rgba(22,163,74,.15)}
h1{color:#16a34a;font-size:1.9rem;margin-bottom:6px}
.sub{color:#888;font-size:.83rem;margin-bottom:22px}
.fila{display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid #440000}
.val{color:#cc0000;font-weight:900}
.ok-box{background:#dcfce7;border:2px solid #16a34a;border-radius:8px;padding:13px;margin:18px 0;color:#f5c518;font-weight:900}
a{display:inline-block;margin-top:18px;background:linear-gradient(135deg,#cc0000,#ff2222);
  color:#fff;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:900}
.fecha{color:#aaa;font-size:.73rem;margin-top:13px}</style></head><body>
<div class='box'>
  <div style='font-size:3.5rem;margin-bottom:14px'>✅</div>
  <h1>¡Reset Completo!</h1>
  <p class='sub'>El mes fue cerrado exitosamente</p>
  <div class='fila'><span>📦 Pedidos eliminados</span><span class='val'>%d</span></div>
  <div class='fila'><span>💰 Ingresos del mes</span><span class='val'>%s</span></div>
  <div class='ok-box'>✅ Base de datos limpia — Nuevo mes comenzado</div>
  <a href='/admin'>Ir al Panel Admin</a>
  <p class='fecha'>%s</p>
</div></body></html>""" % (total, fmt(ingr), datetime.now().strftime("%d/%m/%Y %H:%M"))


@app.route("/admin/descargar-encargos")
def descargar_encargos():
    if not session.get("admin"): return redirect(url_for("admin_login"))
    c    = cfg()
    nom  = c.get("nombre","Mercado Frutas Frescas")
    db   = get_db()
    peds = db.execute("SELECT * FROM pedidos WHERE estado NOT IN ('Negado','Cancelado') ORDER BY id ASC").fetchall()
    db.close()
    hoy       = datetime.now().strftime("%d/%m/%Y")
    total_dia = sum(p["total"] for p in peds)

    def bloque_pdf(p):
        try: items = json.loads(p["items"])
        except: items = []
        rows = ""
        for it in items:
            sub = float(it["precio"]) * int(it["qty"])
            rows += "<tr><td style='padding:2px 6px;font-size:8pt;border-bottom:1px solid #ddd'>%s</td><td style='padding:2px 6px;font-size:8pt;text-align:center;border-bottom:1px solid #ddd'>%d %s</td><td style='padding:2px 6px;font-size:8pt;text-align:right;font-weight:bold;border-bottom:1px solid #ddd'>%s</td></tr>" % (
                it["nombre"][:18], it["qty"], it.get("unidad",""), fmt(sub))
        notas = ('<p style="font-size:7pt;color:#555;padding:2px 6px;font-style:italic">📝 %s</p>' % p["notas"]) if p["notas"] else ""
        return """<div style="border:2px solid #222;border-radius:14px;overflow:hidden;background:#fff;display:flex;flex-direction:column">
  <div style="background:#111;padding:7px 10px;text-align:center;border-radius:12px 12px 0 0">
    <div style="font-size:9pt;font-weight:900;color:#fff">🍊 %s</div>
    <div style="font-size:7pt;color:#ccc">ENCARGOS DEL DÍA — %s</div>
  </div>
  <div style="background:#f5f5f5;padding:4px 10px;display:flex;justify-content:space-between;border-bottom:1px solid #ddd">
    <strong style="font-size:8pt">Pedido #%d</strong>
    <span style="background:#222;color:#fff;border-radius:10px;padding:1px 7px;font-size:7pt;font-weight:bold">Ficha: %s</span>
  </div>
  <div style="padding:4px 10px;border-bottom:1px solid #eee;font-size:8pt">
    <strong>%s</strong> · 📱 %s<br>
    <span style="font-size:7pt;color:#666">%s · %s</span>
  </div>
  <div style="background:#f0f0f0;padding:3px 10px;font-size:7pt;font-weight:bold;color:#333;text-transform:uppercase;border-bottom:1px solid #ddd">Productos</div>
  <table style="width:100%%;border-collapse:collapse">
    <thead><tr>
      <th style="padding:2px 6px;text-align:left;font-size:7pt;color:#666;border-bottom:1px solid #ddd">Producto</th>
      <th style="padding:2px 6px;text-align:center;font-size:7pt;color:#666;border-bottom:1px solid #ddd">Cant.</th>
      <th style="padding:2px 6px;text-align:right;font-size:7pt;color:#666;border-bottom:1px solid #ddd">Total</th>
    </tr></thead>
    <tbody>%s</tbody>
  </table>
  %s
  <div style="flex:1"></div>
  <div style="padding:5px 10px;background:#111;border-radius:0 0 12px 12px;display:flex;justify-content:space-between;align-items:center">
    <span style="font-size:7pt;color:#aaa">💵 Pago al recoger</span>
    <strong style="color:#fff;font-size:9pt">%s</strong>
  </div>
</div>""" % (nom, hoy, p["id"], p["ficha"] or "—",
             p["nombre_cliente"], p["celular"],
             p["fecha"], p["estado"],
             rows, notas, fmt(p["total"]))

    grid_rows = ""
    for i in range(0, len(peds), 2):
        b1 = bloque_pdf(peds[i])
        b2 = bloque_pdf(peds[i+1]) if i+1 < len(peds) else "<div></div>"
        grid_rows += """<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px;page-break-inside:avoid">
  %s %s
</div>""" % (b1, b2)

    total_html = ""
    if peds:
        total_html = "<div style='background:#111;border-radius:10px;padding:12px 16px;margin-top:10px;display:flex;justify-content:space-between;color:#fff'><div><strong>📦 TOTAL DEL DÍA</strong><div style='font-size:8pt;color:#aaa'>%d encargo(s)</div></div><strong style='font-size:14pt'>%s</strong></div>" % (len(peds), fmt(total_dia))

    html = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Encargos %s</title>
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800;900&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:'Nunito',sans-serif}
body{background:#fff;color:#111;padding:8px}
@page{size:A4;margin:8mm}
@media screen{body{background:#f0f0f0;padding:20px}.wrap{background:#fff;max-width:860px;margin:0 auto;padding:16px;border-radius:12px}}
</style>
</head>
<body>
<div class="wrap">
  <div style="text-align:center;border-bottom:2px solid #111;padding-bottom:10px;margin-bottom:14px">
    <h1 style="font-size:14pt;font-weight:900">🍊 %s — Encargos del Día</h1>
    <p style="font-size:9pt;color:#555">%s &nbsp;·&nbsp; %d pedido(s) &nbsp;·&nbsp; Total: %s</p>
  </div>
  %s%s
</div>
<script>window.onload=function(){window.print()}</script>
</body>
</html>""" % (nom, nom, hoy, len(peds), fmt(total_dia), grid_rows, total_html)
    return html


# ═══════════════════════════════════════════════════════
# MARCAR PAGADO
# ═══════════════════════════════════════════════════════
@app.route("/admin/marcar-pagado/<int:pid>")
def marcar_pagado(pid):
    if not session.get("admin"): return redirect(url_for("admin_login"))
    db = get_db()
    db.execute("UPDATE pedidos SET estado='Pagado' WHERE id=?", (pid,))
    db.commit(); db.close()
    return redirect(url_for("admin_panel", msg="💵 Pedido #%d marcado como pagado." % pid, tipo="ok"))


# ═══════════════════════════════════════════════════════
# COMPRAS / GASTOS
# ═══════════════════════════════════════════════════════
@app.route("/admin/compras", methods=["GET","POST"])
def admin_compras():
    if not session.get("admin"): return redirect(url_for("admin_login"))
    c   = cfg()
    nom = c.get("nombre","Mercado Frutas Frescas")
    msg = ""
    if request.method == "POST":
        accion = request.form.get("accion","")
        if accion == "agregar":
            db = get_db()
            db.execute("INSERT INTO compras(producto,cantidad,costo,fecha,notas) VALUES(?,?,?,?,?)", (
                request.form.get("producto","").strip(),
                request.form.get("cantidad","").strip(),
                float(request.form.get("costo",0)),
                datetime.now().strftime("%d/%m/%Y"),
                request.form.get("notas","").strip()
            ))
            db.commit(); db.close()
            msg = "✅ Compra registrada."
        elif accion == "eliminar":
            pid2 = request.form.get("id")
            db = get_db()
            db.execute("DELETE FROM compras WHERE id=?", (pid2,))
            db.commit(); db.close()
            msg = "🗑️ Registro eliminado."

    db    = get_db()
    compras = db.execute("SELECT * FROM compras ORDER BY id DESC").fetchall()
    ventas  = db.execute("SELECT SUM(total) FROM pedidos WHERE estado='Pagado'").fetchone()[0] or 0
    db.close()

    total_gastos = sum(c2["costo"] for c2 in compras)
    ganancia     = ventas - total_gastos

    filas = ""
    for c2 in compras:
        filas += """<tr>
  <td><strong>%s</strong></td>
  <td>%s</td>
  <td style="color:#f5c518;font-weight:800">%s</td>
  <td style="color:#c8a415;font-size:.8rem">%s</td>
  <td>%s</td>
  <td>
    <form method="POST" style="display:inline">
      <input type="hidden" name="accion" value="eliminar">
      <input type="hidden" name="id" value="%d">
      <button type="submit" class="btn btn-ro" style="font-size:.75rem;padding:3px 9px" onclick="return confirm('¿Eliminar?')">🗑️</button>
    </form>
  </td>
</tr>""" % (c2["producto"], c2["cantidad"], fmt(c2["costo"]),
             c2["fecha"], c2["notas"] or "—", c2["id"])

    gan_color = "#22c55e" if ganancia >= 0 else "#ef4444"
    gan_ico   = "📈" if ganancia >= 0 else "📉"
    alerta_html = '<div class="alerta alerta-ok">%s</div>' % msg if msg else ""

    return nav("admin_panel", c) + """
<div class="wrap">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;flex-wrap:wrap;gap:10px">
    <h1 style="font-size:1.7rem;font-weight:900;color:#f5c518">📦 Gastos y Ganancias</h1>
    <a href="/admin" class="btn btn-ro">← Volver al Admin</a>
  </div>
  %s
  <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-bottom:20px">
    <div class="stat">
      <div class="stat-n">%s</div>
      <div class="stat-l">💰 Total Vendido (Pagado)</div>
    </div>
    <div class="stat">
      <div class="stat-n" style="color:#ef4444">%s</div>
      <div class="stat-l">🛒 Total Gastado en Compras</div>
    </div>
    <div class="stat" style="border-top-color:%s">
      <div class="stat-n" style="color:%s">%s %s</div>
      <div class="stat-l">%s Ganancia Neta</div>
    </div>
  </div>
  <div class="panel" style="max-width:600px;margin-bottom:20px">
    <h2>➕ Registrar Compra</h2>
    <form method="POST">
      <input type="hidden" name="accion" value="agregar">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
        <div class="fg"><label>Producto *</label>
          <input type="text" name="producto" required placeholder="Ej: Cajilla de mangos"></div>
        <div class="fg"><label>Cantidad *</label>
          <input type="text" name="cantidad" required placeholder="Ej: 3 cajillas, 10 kg"></div>
        <div class="fg"><label>Costo Total (₡) *</label>
          <input type="number" name="costo" required min="0" step="100" placeholder="0"></div>
        <div class="fg"><label>Notas</label>
          <input type="text" name="notas" placeholder="Proveedor, observaciones..."></div>
      </div>
      <button type="submit" class="btn btn-mo btn-full" style="margin-top:6px">💾 Guardar Compra</button>
    </form>
  </div>
  <div class="panel">
    <h2>📋 Historial de Compras (%d)</h2>
    <div class="tabla-wrap">
      <table>
        <thead><tr>
          <th>Producto</th><th>Cantidad</th><th>Costo</th><th>Fecha</th><th>Notas</th><th>Acción</th>
        </tr></thead>
        <tbody>%s</tbody>
      </table>
    </div>
  </div>
</div>
""" % (alerta_html,
       fmt(ventas), fmt(total_gastos),
       gan_color, gan_color, gan_ico, fmt(abs(ganancia)),
       gan_ico,
       len(compras), filas or '<tr><td colspan="6" style="text-align:center;padding:18px;color:#c8a415">Sin compras registradas.</td></tr>') + PIE + JS_CARRITO + "</body></html>"


# ═══════════════════════════════════════════════════════
# INICIO
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "="*50)
    print("  🍊  Mercado Frutas Frescas")
    print("="*50)
    print("  Tienda:  http://localhost:5000")
    print("  Admin:   http://localhost:5000/admin")
    print("  Pass:    Admin2026$")
    print("  Master:  Frutas$Master2006")
    print("  Reset:   http://localhost:5000/reset-frutas-2024")
    print("="*50 + "\n")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)), debug=False)
