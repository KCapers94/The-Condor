from flask import Flask, request, make_response, session
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User, Category, Activity, Date

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
CORS(app)

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

@app.route('/')
def index():
    return '<h1>Project Server</h1>'

class Signup(Resource):
    def post(self):
        new_user = User(
            name=request.json['name'],
            password=generate_password_hash(request.json['password']),
        )
        db.session.add(new_user)
        db.session.commit()

        response_dict = new_user.to_dict()
        response = make_response(response_dict, 201)
        return response

api.add_resource(Signup, '/signup')

class Login(Resource):
    def post(self):
        name = request.json.get('name')
        password = request.json.get('password') 
    
        user = User.query.filter_by(name=name).first()

        if not user or not check_password_hash(user.password, password):
            return {'error': 'Invalid username or password'}, 401

        session['user_id'] = user.id
        return user.to_dict()

api.add_resource(Login, '/login')

class CheckSession(Resource):
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            return user.to_dict()
        else:
            return {'message': '401: Not Authorized'}, 401

api.add_resource(CheckSession, '/check_session')

class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        return {'message': '204: No Content'}, 204

api.add_resource(Logout, '/logout')

class Categories(Resource):
    # def get(self):
    #     user_id = session.get('user_id')
    #     if not user_id:
    #         return {'error': 'User not logged in'}, 401

    #     categories = set(
    #         category for date in Date.query.filter_by(user_id=user_id).all()
    #         for category in [date.category] if category
    #     )

    #     response_dict_list = [category.to_dict() for category in categories]
    #     response = make_response(response_dict_list, 200)
    #     return response
    
    
    def get(self):
    #     # Fetch all categories
            categories = Category.query.all()

    #     # Serialize and return the categories
            response_dict_list = [category.to_dict() for category in categories]
            return make_response(response_dict_list, 200)

    def post(self):
        new_record = Category(
            name=request.json['name'],
        )
        db.session.add(new_record)
        db.session.commit()

        response_dict = new_record.to_dict()
        response = make_response(response_dict, 201)
        return response

api.add_resource(Categories, '/categories')

class Activities(Resource):
    def get(self):
        response_dict_list = [n.to_dict() for n in Activity.query.all()]
        response = make_response(response_dict_list, 200)
        return response

    def post(self):
        new_record = Activity(
            name=request.json['name'],
            date_id=request.json['date_id'],
        )
        db.session.add(new_record)
        db.session.commit()

        response_dict = new_record.to_dict()
        response = make_response(response_dict, 201)
        return response

api.add_resource(Activities, '/activities')

class Dates(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'User not logged in'}, 401

        dates = Date.query.filter_by(user_id=user_id).all()
        response_dict_list = [date.to_dict() for date in dates]
        response = make_response(response_dict_list, 200)
        return response
    
    #  def get(self):
    #     user_id = session.get('user_id')
    #     if not user_id:
    #         return {'error': 'User not logged in'}, 401

    #     # Fetch dates specific to the logged-in user
    #     dates = Date.query.filter_by(user_id=user_id).all()

    #     # Serialize the dates
    #     response_dict_list = [date.to_dict() for date in dates]
    #     return make_response(response_dict_list, 200)

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'User not logged in'}, 401

        new_record = Date(
            name=request.json['name'],
            date=request.json['date'],
            time=request.json['time'],
            description=request.json['description'],
            user_id=user_id,
            category_id=request.json['category_id']
        )

        db.session.add(new_record)
        db.session.commit()

        response_dict = new_record.to_dict()
        response = make_response(response_dict, 201)
        return response

api.add_resource(Dates, '/dates')

class DatesByID(Resource):
    def get(self, id):
        record = Date.query.filter_by(id=id).first()
        if not record:
            return {'error': 'Date not found'}, 404
        
        category_id = record.category_id
        if not category_id:
            return {'error': 'This date is not associated with a category'}


        dates_in_category = Date.query.filter_by(category_id=category_id).all()

        response = [date.to_dict() for date in dates_in_category]
        return make_response(response, 200)

    def patch(self, id):
        record = Date.query.filter_by(id=id).first()
        if not record:
            return {'error': 'Date not found'}, 404

        data = request.json
        for attr, value in data.items():
            setattr(record, attr, value)

        if 'category_id' in data:
            category = Category.query.filter_by(id=data['category_id']).first()
            if category:
                record.category = category

        db.session.commit()
        return make_response(record.to_dict(), 200)

    def delete(self, id):
        record = Date.query.filter_by(id=id).first()
        if not record:
            return {'error': 'Date not found'}, 404

        db.session.delete(record)
        db.session.commit()
        return make_response({'message': 'Record successfully deleted'}, 200)

api.add_resource(DatesByID, '/dates/<int:id>')

class UserCategoriesWithDates(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'User not logged in'}, 401

        categories = Category.query.join(Date).filter(Date.user_id == user_id).all()

        # Serialize categories with nested dates
        result = [
            {
                "id": category.id,
                "name": category.name,
                "dates": [date.to_dict() for date in category.dates if date.user_id == user_id]
            }
            for category in categories
        ]

        return make_response(result, 200)

api.add_resource(UserCategoriesWithDates, '/categories_with_dates')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
