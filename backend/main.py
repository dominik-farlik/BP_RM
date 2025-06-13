from datetime import timedelta

from solve import solve
from flask import Flask, jsonify, request
from flask_cors import CORS  # type: ignore
from flask_bcrypt import Bcrypt  # type: ignore
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:bprm@db:3306/bprm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

db = SQLAlchemy(app)
jwt = JWTManager(app)


class User(db.Model):  # type: ignore
    __tablename__ = 'user'
    userID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Formula(db.Model):  # type: ignore
    __tablename__ = 'formula'

    FormulaID = db.Column(db.Integer, primary_key=True)
    premise = db.Column(db.String(300), nullable=False)
    conclusion = db.Column(db.String(100), nullable=True)

    __table_args__ = (
        db.UniqueConstraint('premise', 'conclusion', name='unique_premise_conclusion'),
    )

    user_id = db.Column(db.Integer, db.ForeignKey('user.userID'), nullable=False)
    user = db.relationship('User', backref=db.backref('formulas', lazy=True, cascade='all, delete-orphan'))


with app.app_context():
    db.create_all()


@app.route('/api/history', methods=['POST'])
@jwt_required()
def history():
    try:
        user_id = get_jwt_identity()
        formulas = db.session.query(Formula).filter_by(user_id=user_id).limit(10).all()

        formulas_list = []
        for f in formulas:
            formulas_list.append({
                "premise": f.premise,
                "conclusion": f.conclusion,
            })

        return jsonify({"formulas": formulas_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/solve', methods=['POST'])
@jwt_required()
def solve_formula():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        formula = data.get('formula')
        conclusion = data.get('conclusion')
        if not formula and not conclusion:
            return jsonify({"error": "No input provided."}), 400
        elif formula and not conclusion:
            existing = db.session.query(Formula).filter_by(premise=formula, user_id=user_id).first()
            if not existing:
                db.session.add(Formula(premise=formula, user_id=user_id))
                db.session.commit()
            steps, result = solve(formula.upper(), False)
        elif formula and conclusion:
            existing = db.session.query(Formula).filter_by(premise=formula, conclusion=conclusion, user_id=user_id).first()
            if not existing:
                db.session.add(Formula(premise=formula, conclusion=conclusion, user_id=user_id))
                db.session.commit()
            steps, result = solve(("(" + formula + ") ∧ ¬(" + conclusion + ")").upper(), True)
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
        print(user.userID)
        access_token = create_access_token(identity=user.userID)
        return jsonify({
            "message": "Login successful.",
            "access_token": access_token
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
