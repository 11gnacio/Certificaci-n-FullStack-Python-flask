from flask import render_template, request, redirect, session, flash
from flask_app import app
from flask_app.models.libro import Libro
from flask_app.models.usuario import Usuario

@app.route('/libros')
def mis_libros():
	if 'usuario_id' not in session:
		return redirect('/')

	data = {'usuario_id': session['usuario_id']}
	mis_libros = Libro.get_mis_libros(data)
	libros_comunidad = Libro.get_libros_comunidad(data)
	usuario = Usuario.get_by_id({'id': session['usuario_id']})

	return render_template('mis_libros.html', mis_libros=mis_libros, libros_comunidad=libros_comunidad, usuario=usuario)

@app.route('/libros/nuevo')
def nuevo_libro():
	if 'usuario_id' not in session:
		return redirect('/')
	usuario = Usuario.get_by_id({'id': session['usuario_id']})
	return render_template('nuevo_libro.html', usuario=usuario)

@app.route('/libros/crear', methods=['POST'])
def crear_libro():
	if 'usuario_id' not in session:
		return redirect('/')

	if not Libro.validar_libro(request.form):
		return redirect('/libros/nuevo')

	data = {
		'titulo': request.form['titulo'],
		'autor': request.form['autor'],
		'genero': request.form['genero'],
		'fecha_publicacion': request.form['fecha_publicacion'],
		'descripcion': request.form['descripcion'],
		'usuario_id': session['usuario_id']
	}
	Libro.save(data)
	return redirect('/libros')

@app.route('/libros/<int:id>')
def ver_libro(id):
	if 'usuario_id' not in session:
		return redirect('/')

	libro = Libro.get_by_id({'id': id})
	if not libro:
		return redirect('/libros')

	es_favorito = Libro.check_favorito({'usuario_id': session['usuario_id'], 'libro_id': id})
	usuarios_fav = Libro.get_usuarios_favoritos({'libro_id': id})
	usuario = Usuario.get_by_id({'id': session['usuario_id']})

	return render_template('detalle_libro.html', libro=libro, es_favorito=es_favorito, usuarios_fav=usuarios_fav, usuario=usuario)

@app.route('/libros/editar/<int:id>')
def editar_libro(id):
	if 'usuario_id' not in session:
		return redirect('/')

	libro = Libro.get_by_id({'id': id})
	if not libro or libro.usuario_id != session['usuario_id']:
		return redirect('/libros')

	usuario = Usuario.get_by_id({'id': session['usuario_id']})
	return render_template('editar_libro.html', libro=libro, usuario=usuario)

@app.route('/libros/actualizar/<int:id>', methods=['POST'])
def actualizar_libro(id):
	if 'usuario_id' not in session:
		return redirect('/')

	if not Libro.validar_libro(request.form):
		return redirect(f'/libros/editar/{id}')

	data = {
		'id': id,
		'titulo': request.form['titulo'],
		'autor': request.form['autor'],
		'genero': request.form['genero'],
		'fecha_publicacion': request.form['fecha_publicacion'],
		'descripcion': request.form['descripcion'],
		'usuario_id': session['usuario_id']
	}
	Libro.update(data)
	return redirect('/libros')

@app.route('/libros/borrar/<int:id>')
def borrar_libro(id):
	if 'usuario_id' not in session:
		return redirect('/')

	Libro.delete({'id': id, 'usuario_id': session['usuario_id']})
	return redirect('/libros')

@app.route('/favoritos/agregar/<int:id>')
def agregar_favorito(id):
	if 'usuario_id' not in session:
		return redirect('/')

	Libro.add_favorito({'usuario_id': session['usuario_id'], 'libro_id': id})
	return redirect(f'/libros/{id}')

@app.route('/favoritos')
def mis_favoritos():
	if 'usuario_id' not in session:
		return redirect('/')

	data = {'usuario_id': session['usuario_id']}
	favoritos = Libro.get_favoritos_por_usuario(data)
	usuario = Usuario.get_by_id({'id': session['usuario_id']})

	return render_template('favoritos.html', favoritos=favoritos, usuario=usuario)
