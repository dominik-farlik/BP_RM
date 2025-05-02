from solve import solve
from flask import Flask, jsonify, request
from flask_cors import CORS  # type: ignore
from flask_bcrypt import Bcrypt  # type: ignore
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:bprm@localhost/bprm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key'

db = SQLAlchemy(app)
jwt = JWTManager(app)


class User(db.Model):  # type: ignore
    userID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class FormulaHistory(db.Model):  # type: ignore
    __tablename__ = 'formula_history'

    id = db.Column(db.Integer, primary_key=True)
    formula = db.Column(db.Text, nullable=False)
    result = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('user.userID'), nullable=False)
    user = db.relationship('User', backref=db.backref('formulas', lazy=True))


# Inicializace databáze
with app.app_context():
    db.create_all()

"""
@app.route('/api/history', methods=['GET'])
def get_history():
    data = request.get_json()
    username = data.get('username')
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    history = [
        {
            "userID": entry.id,
            "formula": entry.formula,
            "result": entry.result,
            "timestamp": entry.timestamp.isoformat(),
        }
        for entry in user.formulas
    ]

    return jsonify(history), 200
"""



@app.route('/api/solve', methods=['POST'])
def solve_formula():
    try:
        data = request.get_json()
        formula = data.get('formula')
        if not formula:
            return jsonify({"error": "No formula provided."}), 400
        steps, result = solve(formula)
        return jsonify({
            "steps": steps,
            "result": result,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required."}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists."}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required."}), 400

        user = User.query.filter_by(username=username).first()

        if not user or not bcrypt.check_password_hash(user.password, password):
            return jsonify({"error": "Invalid username or password."}), 401

        access_token = create_access_token(identity={'username': user.username})
        return jsonify({
            "message": "Login successful.",
            "access_token": access_token
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
