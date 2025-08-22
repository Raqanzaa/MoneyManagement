import os
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, request, jsonify, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager

# Load environment variables from .env file
load_dotenv()

# Initialize libraries
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()

# Define Database Models


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(
            password).decode('utf8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship(
        'User', backref=db.backref('transactions', lazy=True))


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Secret key for signing JWTs
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

    # Connect libraries to the Flask app
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # === Routes for serving HTML pages ===

    @app.route('/')
    def index():
        # Redirect the main page to the login page
        return redirect(url_for('login_page'))

    @app.route('/login')
    def login_page():
        return render_template('login.html')

    @app.route('/dashboard')
    def dashboard_page():
        return render_template('dashboard.html')

    # === API Endpoints for Authentication ===

    @app.route('/api/register', methods=['POST'])
    def register():
        """Registers a new user."""
        try:
            data = request.json
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return jsonify({"msg": "Email and password are required"}), 400

            if User.query.filter_by(email=email).first():
                return jsonify({"msg": "Email already exists"}), 409

            new_user = User(email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            return jsonify({"msg": "User created successfully"}), 201
        except Exception as e:
            print(e)
            return jsonify({"msg": "Internal server error", "error": str(e)}), 500

    @app.route('/api/login', methods=['POST'])
    def login():
        """Logs in an existing user and returns a JWT token."""
        try:
            data = request.json
            email = data.get('email')
            password = data.get('password')

            user = User.query.filter_by(email=email).first()

            if user and user.check_password(password):
                access_token = create_access_token(identity=str(user.id))
                # Added success message
                return jsonify({"access_token": access_token, "msg": "Login successful"}), 200

            return jsonify({"msg": "Invalid email or password"}), 401
        except Exception as e:
            print(e)
            return jsonify({"msg": "Internal server error", "error": str(e)}), 500

    # === Protected Endpoint ===

    @app.route('/api/profile')
    @jwt_required()
    def my_profile():
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if user is None:
                return jsonify({"msg": "User not found"}), 404

            return jsonify({"id": user.id, "email": user.email}), 200
        except Exception as e:
            print(e)
            return jsonify({"msg": "Internal server error", "error": str(e)}), 500

    # === API Endpoints untuk Data Transaksi ===

    @app.route('/api/transactions', methods=['GET'])
    @jwt_required()
    def get_transactions():
        """Mengambil semua transaksi milik pengguna yang sedang login."""
        current_user_id = get_jwt_identity()
        user_transactions = Transaction.query.filter_by(
            user_id=current_user_id).order_by(Transaction.id.desc()).all()

        # Konversi objek SQLAlchemy ke format dictionary
        result = []
        for t in user_transactions:
            result.append({
                'id': t.id,
                'description': t.description,
                'amount': t.amount,
                'category': t.category
            })
        return jsonify(result), 200

    @app.route('/api/transactions', methods=['POST'])
    @jwt_required()
    def add_transaction():
        """Menambahkan transaksi baru untuk pengguna yang sedang login."""
        current_user_id = get_jwt_identity()
        data = request.json

        new_transaction = Transaction(
            description=data['description'],
            amount=float(data['amount']),
            category=data['category'],
            user_id=current_user_id
        )
        db.session.add(new_transaction)
        db.session.commit()

        return jsonify({"msg": "Transaction added successfully"}), 201

    return app


app = create_app()
