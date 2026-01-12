from flask import Flask, request, jsonify, session, send_file
import bcrypt
from db import get_db
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os

app = Flask(__name__)
app.secret_key = "SICAM_CARDENAS_2025"

# ---------------- LOGIN ----------------
@app.post("/login")
def login():
    data = request.json
    documento = data.get("documento")
    password = data.get("password")

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, password, rol, nombre FROM usuarios WHERE documento=%s", (documento,))
    user = cur.fetchone()

    if not user:
        return jsonify({"ok":False, "msg":"Usuario no existe"}), 404

    if bcrypt.checkpw(password.encode(), user[1].encode()):
        session["user_id"] = user[0]
        session["rol"] = user[2]
        session["nombre"] = user[3]
        return jsonify({"ok":True, "rol":user[2], "nombre":user[3]})

    return jsonify({"ok":False,"msg":"Contraseña incorrecta"}),401

@app.post("/admin/crear_estudiante")
def crear_estudiante():
    if session.get("rol")!="admin":
        return "No autorizado",403

    data=request.json
    documento=data["documento"]
    nombre=data["nombre"]
    password=data["password"]
    grado=data["grado"]
    curso=data["curso"]

    hashed=bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()

    db=get_db()
    cur=db.cursor()
    cur.execute("INSERT INTO usuarios (documento,nombre,password,rol) VALUES (%s,%s,%s,'estudiante') RETURNING id",
                (documento,nombre,hashed))
    user_id=cur.fetchone()[0]

    cur.execute("INSERT INTO estudiantes (usuario_id,grado,curso) VALUES (%s,%s,%s)",
                (user_id,grado,curso))
    db.commit()

    return jsonify({"ok":True})

@app.post("/admin/nota")
def poner_nota():
    if session.get("rol")!="admin":
        return "No autorizado",403

    d=request.json
    db=get_db()
    cur=db.cursor()
    cur.execute("INSERT INTO notas (estudiante_id,actividad_id,nota) VALUES (%s,%s,%s)",
                (d["estudiante_id"],d["actividad_id"],d["nota"]))
    db.commit()
    return jsonify({"ok":True})

@app.get("/estudiante/promedio/<int:est>/<int:materia>/<int:periodo>")
def promedio(est,materia,periodo):
    db=get_db()
    cur=db.cursor()
    cur.execute("""
    SELECT SUM(n.nota*a.porcentaje/100)
    FROM notas n
    JOIN actividades a ON n.actividad_id=a.id
    WHERE n.estudiante_id=%s AND a.materia_id=%s AND a.periodo=%s
    """,(est,materia,periodo))

    prom=cur.fetchone()[0] or 0
    estado="APROBADO" if prom>=3 else "REPROBADO"

    return jsonify({"promedio":round(prom,2),"estado":estado})

@app.get("/boletin/<int:estudiante_id>")
def boletin(estudiante_id):
    db=get_db()
    cur=db.cursor()

    cur.execute("""
    SELECT u.nombre, m.nombre, AVG(n.nota)
    FROM notas n
    JOIN actividades a ON n.actividad_id=a.id
    JOIN materias m ON a.materia_id=m.id
    JOIN estudiantes e ON n.estudiante_id=e.id
    JOIN usuarios u ON e.usuario_id=u.id
    WHERE e.id=%s
    GROUP BY u.nombre, m.nombre
    """,(estudiante_id,))

    data=cur.fetchall()

    os.makedirs("boletines",exist_ok=True)
    archivo=f"boletines/boletin_{estudiante_id}.pdf"
    doc=SimpleDocTemplate(archivo)
    styles=getSampleStyleSheet()
    story=[Paragraph("COLEGIO CÁRDENAS MIRRIÑAO",styles['Title'])]

    for d in data:
        estado="APROBADO" if d[2]>=3 else "REPROBADO"
        story.append(Paragraph(f"{d[1]}: {round(d[2],2)} - {estado}",styles['Normal']))

    doc.build(story)
    return send_file(archivo)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",8080)))
