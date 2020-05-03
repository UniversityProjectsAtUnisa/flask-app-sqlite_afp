from flask_restful import Resource, reqparse
from models.user import UserModel

class UserRegister(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("username",
                        type=str, required=True, help="Username should be non-empty string")
    parser.add_argument("password",
                        type=str, required=True, help="Password should be non-empty string")

    def post(self):
        data = UserRegister.parser.parse_args()
        
        if UserModel.find_by_username(data["username"]):
            return {"message":"user with username {} already exists".format(data["username"])}, 400

        user = UserModel(**data)
        user.save_to_db()
        
        return {"message": "User created successfully"}, 201
