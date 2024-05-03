from flask_login import UserMixin
from flask import url_for

class UserLogin():

    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user['id'])

    def getName(self):
        return self.__user['name'] if self.__user else ""

    def getEmail(self):
        return self.__user['email'] if self.__user else ""

    def getAvatar(self, app):
        img = None
        if not self.__user['file']:
            try:
                with app.open_resource(app.root_path + url_for('static', filename='images/default.png'), "rb") as f:
                    img = f.read()
            except FileNotFoundError as e:
                print("no avatar" + str(e))
        else:
            img = self.__user['file']
        return img

    def verifyExt(self, filename):
        ext = filename.rsplit('.', 1)[1]
        if ext == "png" or ext == "PNG":
            return True
        return False

    def files(self):
        files = None
        if not self.__user['folder']:
            return ""
        else:
            files = self.__user['folder']
        return files

