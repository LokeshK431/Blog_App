from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.db import connection

class PostgresBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM accounts_myuser WHERE email=%s", [email])
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            user = UserModel(id=row[0], email=row[1], password=row[2], is_admin=row[3])
            
            if user.check_password(password):
                return user
            
            return None
        
    def get_user(self, user_id):
        UserModel = get_user_model()
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM blog_myuser WHERE id=%s", [user_id])
            row = cursor.fetchone()
            
            if row is not None:
                return UserModel(id=row[0], email=row[1], password=row[2], is_admin=row[3])
            
            return None