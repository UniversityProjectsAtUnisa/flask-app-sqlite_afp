import os

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import UserRegister, User, UserLogin, UserLogout, TokenRefresh
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from blacklist import BLACKLIST

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", 'sqlite:///data.db')
# Turns off flask_sqlalchemy modification tracker in favor of sqlalchemy's one which is better
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]
app.secret_key = "jose"  # app.config["JWT_SECRET_KEY"]
api = Api(app)

jwt = JWTManager(app)  # not creating /auth


@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:  # Instead of hardcoding it you should read it from the database
        return {"is_admin": True}
    return {"is_admin": False}

# funzione che ritorna True se il token inviato è nella Blacklist
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token["jti"] in BLACKLIST

# Chiamata quando scade il token
@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({"description": "The token has expired",
                    "error": "token_expired"}), 401

# Chiamato se il token non è un token JWT
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"description": "Signature verification failed",
                    "error": "invalid_token"}), 401

# Chiamato se non viene inviato un header "Authorization"
@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"description": "Request does not contain an access_token",
                    "error": "authorization_required"}), 401

# Chiamato se viene inviato un token con "fresh"=False, ma è richiesto un token "fresh"=True
@jwt.needs_fresh_token_loader
def fresh_token_callback():
    return jsonify({"description": "The token is not fresh",
                    "error": "fresh_token_required"}), 401

# Chiamato se viene utilizzato un token revoato (ex. dopo logout viene usato lo stesso token)
@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({"description": "The token has been revoked.",
                    "error": "token_revoked"}), 401


@app.before_first_request
def create_tables():
    db.create_all()


api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")
api.add_resource(UserRegister, "/register")
api.add_resource(Store, "/store/<string:name>")
api.add_resource(StoreList, "/stores")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(TokenRefresh, "/refresh")

if __name__ == "__main__":
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)
