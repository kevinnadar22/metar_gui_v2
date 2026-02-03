import jwt, datetime, os
from functools import wraps
from flask import Blueprint, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, UserActivity
from .config import Config

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

ROLE_ORDER = {"user": 1, "admin": 2, "super_admin": 3}


@auth_bp.route("/me", methods=["GET"])
def me():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify({
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "station": user.station_code,
            "active": user.is_active
        }
    }), 200



def create_token(user, tab_id=None):
    """Create JWT token with tab_id for tab-scoped authentication"""
    # Ensure tab_id is provided and not None
    if not tab_id:
        import uuid
        tab_id = f"tab_{uuid.uuid4().hex[:12]}"
    
    payload = {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "station": user.station_code,
        "tab_id": tab_id,  # Unique per tab
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


def get_client_ip():
    """Get client IP address from request"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ.get('HTTP_X_FORWARDED_FOR').split(',')[0].strip()
    return request.environ.get('REMOTE_ADDR')


def log_activity(user, activity_type, page_or_route=None, tab_id=None, details=None):
    """Log user activity to database"""
    try:
        activity = UserActivity(
            user_id=user.id,
            activity_type=activity_type,
            page_or_route=page_or_route,
            ip_address=get_client_ip(),
            tab_id=tab_id,
            details=details
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")
        db.session.rollback()


def get_current_user():
    """Get current user from JWT token and verify tab_id"""
    token = request.cookies.get("auth_token")
    if not token:
        return None
    try:
        data = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
        user = User.query.get(data["id"])
        
        request_tab_id = request.headers.get("X-Tab-ID", None)
        token_tab_id = data.get("tab_id")
        
        if request_tab_id:
            if token_tab_id != request_tab_id:
               
                if token_tab_id and token_tab_id != "default":
                    print(f"Tab ID mismatch: {token_tab_id} != {request_tab_id}")
                    return None
            
        
        return user
    except Exception as e:
        print(f"Auth error: {e}")
        return None


def require_role(role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user or not user.is_active:
                return jsonify({"error": "Unauthorized"}), 401
            if ROLE_ORDER[user.role] < ROLE_ORDER[role]:
                return jsonify({"error": "Forbidden"}), 403
            return fn(*args, **kwargs, current_user=user)
        return wrapper
    return decorator


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Username and password required"}), 400

    username = data["username"].strip().upper()
    password = data["password"]

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400

    user = User(
        username=username,
        station_code=username,
        password_hash=generate_password_hash(password),
        role="user",              # 🔒 enforced
        is_active=True
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Username and password required"}), 400

    username = data["username"].strip().upper()
    password = data["password"]
    tab_id = data.get("tab_id", "default")  # Get tab_id from request

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.is_active:
        return jsonify({"error": "Account disabled"}), 403

    token = create_token(user, tab_id)  # Include tab_id in token
    
    log_activity(user, "login", page_or_route="/auth/login", tab_id=tab_id)
    
    resp = make_response(jsonify({
        "message": "Login successful",
        "role": user.role
    }))
    resp.set_cookie(
        "auth_token",
        token,
        httponly=True,
        samesite="Lax"
    )
    return resp, 200



@auth_bp.route("/admins", methods=["GET"])
@require_role("super_admin")
def list_admins(current_user):
    admins = User.query.filter_by(role="admin").all()
    print(admins[0].role)
    return jsonify([
        {"id": u.id, "username": u.username, "role": u.role, "active": u.is_active}
        for u in admins
    ])


@auth_bp.route("/admins/<int:user_id>", methods=["DELETE"])
@require_role("super_admin")
def disable_admin(user_id, current_user):
    user = User.query.get_or_404(user_id)
    user.is_active = False
    db.session.commit()
    return jsonify({"message": "Admin disabled"})


@auth_bp.route("/users", methods=["GET"])
@require_role("admin")
def list_users(current_user):
    users = User.query.filter_by(role="user").all()
    return jsonify([
        {
            "id": u.id,
            "username": u.username,
            "station": u.station_code,
            "active": u.is_active
        }
        for u in users
    ])

@auth_bp.route("/admins/<int:admin_id>", methods=["PUT"])
@require_role("super_admin")
def update_admin(admin_id, current_user):
    admin = User.query.get_or_404(admin_id)

    if admin.role != "admin":
        return jsonify({"error": "Only admins can be modified here"}), 403

    if admin.id == current_user.id:
        return jsonify({"error": "You cannot modify your own admin status"}), 403

    data = request.json or {}

    if "is_active" in data:
        admin.is_active = bool(data["is_active"])

    db.session.commit()

    return jsonify({
        "message": "Admin updated",
        "admin_id": admin.id,
        "is_active": admin.is_active
    }), 200

@auth_bp.route("/users/<int:user_id>", methods=["PUT"])
@require_role("admin")
def update_user(user_id, current_user):
    user = User.query.get_or_404(user_id)

    if user.role != "user":
        return jsonify({"error": "Only users can be modified"}), 403

    data = request.json

    if "password" in data:
        user.password_hash = generate_password_hash(data["password"])

    if "is_active" in data:
        user.is_active = bool(data["is_active"])

    db.session.commit()
    return jsonify({"message": "User updated"})


@auth_bp.route("/users/<int:user_id>", methods=["DELETE"])
@require_role("admin")
def delete_user(user_id, current_user):
    user = User.query.get_or_404(user_id)

    if user.role != "user":
        return jsonify({"error": "Admins cannot delete admins"}), 403

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})

@auth_bp.route("/all", methods=["GET"])
@require_role("super_admin")
def list_all(current_user):
    users = User.query.filter_by(role="user").all()
    admins = User.query.filter_by(role="admin").all()

    return jsonify({
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "station": u.station_code,
                "active": u.is_active
            } for u in users
        ],
        "admins": [
            {
                "id": a.id,
                "username": a.username,
                "active": a.is_active
            } for a in admins
        ]
    })

@auth_bp.route("/remove/<int:user_id>", methods=["DELETE"])
@require_role("super_admin")
def remove_any(user_id, current_user):
    user = User.query.get_or_404(user_id)

    if user.role == "super_admin":
        return jsonify({"error": "Cannot delete super admin"}), 400

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"{user.role} deleted"})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    user = get_current_user()
    tab_id = request.headers.get("X-Tab-ID", "default")
    
    # Log the logout activity
    if user:
        log_activity(user, "logout", page_or_route="/auth/logout", tab_id=tab_id)
    
    resp = make_response(jsonify({"message": "Logged out successfully"}))
    resp.delete_cookie("auth_token")
    return resp, 200


@auth_bp.route("/change-password", methods=["POST"])
@require_role("user")
def change_password(current_user):
    data = request.json or {}
    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        return jsonify({"error": "Both current_password and new_password are required"}), 400

    if not check_password_hash(current_user.password_hash, current_password):
        return jsonify({"error": "Current password is incorrect"}), 401

    if len(new_password) < 6:
        return jsonify({"error": "New password must be at least 6 characters"}), 400

    current_user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    log_activity(current_user, "change_password", page_or_route="/auth/change-password")

    return jsonify({"message": "Password changed successfully"}), 200


def create_super_admin():
    if User.query.filter_by(role="super_admin").first():
        return  # already exists

    super_admin = User(
        username="VABB",
        station_code="VABB",
        password_hash=generate_password_hash("Vabb@123"),
        role="super_admin",
        is_active=True
    )

    db.session.add(super_admin)
    db.session.commit()

@auth_bp.route("/create-admin", methods=["POST"])
@require_role("super_admin")
def create_admin(current_user):
    data = request.json or {}

    username = (data.get("username") or "").strip()
    station = (data.get("station_code") or "").strip().upper()

    username_upper = username.upper()
    if not username_upper:
        return jsonify({"error": "Username is required"}), 400

    if User.query.filter_by(username=username_upper).first():
        return jsonify({"error": "User exists"}), 400

    # If station_code not provided, use username as station_code
    if not station:
        station = username_upper

    default_password = f"{station}@123"

    admin = User(
        username=username_upper,
        station_code=station,
        password_hash=generate_password_hash(default_password),
        role="admin",
        is_active=True
    )

    db.session.add(admin)
    db.session.commit()

    log_activity(current_user, "create_admin", page_or_route="/auth/create-admin", details=f"created:{username_upper},station:{station}")

    return jsonify({"message": "Admin created", "default_password": default_password}), 201


@auth_bp.route("/create-user", methods=["POST"])
@require_role("admin")
def create_user(current_user):
    data = request.json or {}
    username = (data.get("username") or "").strip()
    station = (data.get("station_code") or "").strip().upper()

    username_upper = username.upper()

    if not username_upper:
        return jsonify({"error": "Username is required"}), 400

    if User.query.filter_by(username=username_upper).first():
        return jsonify({"error": "User exists"}), 400

    # if station_code not provided, default to username
    if not station:
        station = username_upper

    default_password = f"{station}@123"

    user = User(
        username=username_upper,
        station_code=station,
        password_hash=generate_password_hash(default_password),
        role="user",
        is_active=True
    )

    db.session.add(user)
    db.session.commit()

    log_activity(current_user, "create_user", page_or_route="/auth/create-user", details=f"created:{username_upper},station:{station}")

    return jsonify({"message": "User created", "default_password": default_password}), 201
