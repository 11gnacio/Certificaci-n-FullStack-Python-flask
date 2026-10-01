from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from datetime import datetime

class Libro:
	DB = "esquema_bookhub"

	def __init__(self, data):
		self.id = data['id']
		self.titulo = data['titulo']
		self.autor = data['autor']
		self.genero = data['genero']
		self.fecha_publicacion = data['fecha_publicacion']
		self.descripcion = data['descripcion']
		self.usuario_id = data['usuario_id']
		self.created_at = data['created_at']
		self.updated_at = data['updated_at']
		self.creador_nombre = data.get('creador_nombre', '')
		self.favoritos_count = data.get('favoritos_count', 0)

	@classmethod
	def save(cls, data):
		query = """
			INSERT INTO libros (titulo, autor, genero, fecha_publicacion, descripcion, usuario_id)
			VALUES (%(titulo)s, %(autor)s, %(genero)s, %(fecha_publicacion)s, %(descripcion)s, %(usuario_id)s);
		"""
		return connectToMySQL(cls.DB).query_db(query, data)

	@classmethod
	def get_mis_libros(cls, data):
		query = """
			SELECT l.*, COUNT(f.usuario_id) AS favoritos_count 
			FROM libros l 
			LEFT JOIN favoritos f ON l.id = f.libro_id 
			WHERE l.usuario_id = %(usuario_id)s 
			GROUP BY l.id;
		"""
		results = connectToMySQL(cls.DB).query_db(query, data)
		libros = []
		if results:
			for row in results:
				libros.append(cls(row))
		return libros

	@classmethod
	def get_libros_comunidad(cls, data):
		query = """
			SELECT l.*, CONCAT(u.nombre, ' ', u.apellido) AS creador_nombre, COUNT(f.usuario_id) AS favoritos_count 
			FROM libros l 
			JOIN usuarios u ON l.usuario_id = u.id 
			LEFT JOIN favoritos f ON l.id = f.libro_id 
			WHERE l.usuario_id != %(usuario_id)s 
			GROUP BY l.id;
		"""
		results = connectToMySQL(cls.DB).query_db(query, data)
		libros = []
		if results:
			for row in results:
				libros.append(cls(row))
		return libros

	@classmethod
	def get_by_id(cls, data):
		query = """
			SELECT l.*, CONCAT(u.nombre, ' ', u.apellido) AS creador_nombre, COUNT(f.usuario_id) AS favoritos_count 
			FROM libros l 
			JOIN usuarios u ON l.usuario_id = u.id 
			LEFT JOIN favoritos f ON l.id = f.libro_id 
			WHERE l.id = %(id)s 
			GROUP BY l.id;
		"""
		result = connectToMySQL(cls.DB).query_db(query, data)
		if not result:
			return False
		return cls(result[0])

	@classmethod
	def update(cls, data):
		query = """
			UPDATE libros 
			SET titulo = %(titulo)s, autor = %(autor)s, genero = %(genero)s, 
				fecha_publicacion = %(fecha_publicacion)s, descripcion = %(descripcion)s 
			WHERE id = %(id)s AND usuario_id = %(usuario_id)s;
		"""
		return connectToMySQL(cls.DB).query_db(query, data)

	@classmethod
	def delete(cls, data):
		query = "DELETE FROM libros WHERE id = %(id)s AND usuario_id = %(usuario_id)s;"
		return connectToMySQL(cls.DB).query_db(query, data)

	@classmethod
	def add_favorito(cls, data):
		query = "INSERT IGNORE INTO favoritos (usuario_id, libro_id) VALUES (%(usuario_id)s, %(libro_id)s);"
		return connectToMySQL(cls.DB).query_db(query, data)

	@classmethod
	def check_favorito(cls, data):
		query = "SELECT * FROM favoritos WHERE usuario_id = %(usuario_id)s AND libro_id = %(libro_id)s;"
		result = connectToMySQL(cls.DB).query_db(query, data)
		return len(result) > 0

	@classmethod
	def get_usuarios_favoritos(cls, data):
		query = """
			SELECT u.nombre, u.apellido FROM usuarios u 
			JOIN favoritos f ON u.id = f.usuario_id 
			WHERE f.libro_id = %(libro_id)s;
		"""
		return connectToMySQL(cls.DB).query_db(query, data)

	@classmethod
	def get_favoritos_por_usuario(cls, data):
		query = """
			SELECT l.*, CONCAT(u.nombre, ' ', u.apellido) AS creador_nombre 
			FROM libros l 
			JOIN favoritos f ON l.id = f.libro_id 
			JOIN usuarios u ON l.usuario_id = u.id 
			WHERE f.usuario_id = %(usuario_id)s;
		"""
		results = connectToMySQL(cls.DB).query_db(query, data)
		libros = []
		if results:
			for row in results:
				libros.append(cls(row))
		return libros

	@staticmethod
	def validar_libro(libro):
		is_valid = True

		if len(libro['titulo'].strip()) < 2:
			flash("El título debe tener al menos 2 caracteres.", "libro")
			is_valid = False

		if len(libro['autor'].strip()) < 2:
			flash("El autor debe tener al menos 2 caracteres.", "libro")
			is_valid = False

		if not libro.get('genero') or libro['genero'] == "":
			flash("Debes seleccionar un género.", "libro")
			is_valid = False

		if not libro.get('fecha_publicacion'):
			flash("La fecha de publicación es obligatoria.", "libro")
			is_valid = False
		else:
			fecha_pub = datetime.strptime(libro['fecha_publicacion'], '%Y-%m-%d').date()
			if fecha_pub > datetime.now().date():
				flash("La fecha de publicación no puede ser una fecha futura.", "libro")
				is_valid = False

		if len(libro['descripcion'].strip()) < 10:
			flash("La descripción debe tener al menos 10 caracteres.", "libro")
			is_valid = False

		return is_valid
