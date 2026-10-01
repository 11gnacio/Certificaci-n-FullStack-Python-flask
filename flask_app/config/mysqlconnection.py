import pymysql.cursors
import os

class MySQLConnection:
	def __init__(self, db):
		connection = pymysql.connect(
			host=os.environ.get("DB_HOST", "localhost"),
			user=os.environ.get("DB_USER", "root"),
			password=os.environ.get("DB_PASSWORD", ""),
			db=db,
			charset='utf8mb4',
			cursorclass=pymysql.cursors.DictCursor,
			autocommit=True
		)
		self.connection = connection

	def query_db(self, query, data=None):
		with self.connection.cursor() as cursor:
			try:
				query = cursor.mogrify(query, data)
				cursor.execute(query, data)
				if query.lower().find("insert") >= 0:
					self.connection.commit()
					return cursor.lastrowid
				elif query.lower().find("select") >= 0:
					return cursor.fetchall()
				else:
					self.connection.commit()
					return True
			except Exception as e:
				print("Error en base de datos:", e)
				return False
			finally:
				self.connection.close()

def connectToMySQL(db):
	return MySQLConnection(db)
