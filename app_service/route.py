from flask.blueprints import Blueprint

from app_service import manager_book_route, social_book_route, user_route

manager_book_bp: Blueprint = Blueprint("manager_book_bp", __name__, "/api/book/manager")
social_book_bp: Blueprint = Blueprint("social_book_bp", __name__, "/api/book/social")
user_bp: Blueprint = Blueprint("user_bp", __name__, "/api/user")


manager_book_bp.add_url_rule("/create", view_func=manager_book_route.create_book, methods=["POST"])
manager_book_bp.add_url_rule("/delete", view_func=manager_book_route.delete_book, methods=["POST"])
manager_book_bp.add_url_rule("/get-book", view_func=manager_book_route.get_book, methods=["GET"])
manager_book_bp.add_url_rule("/get-book-list", view_func=manager_book_route.get_book_list, methods=["GET"])

social_book_bp.add_url_rule("/comment-book", view_func=social_book_route.comment_book, methods=["POST"])
social_book_bp.add_url_rule("/like-book", view_func=social_book_route.like_book, methods=["POST"])
social_book_bp.add_url_rule("/get-book-likes", view_func=social_book_route.get_book_likes, methods=["GET"])
social_book_bp.add_url_rule("/get-book-comment", view_func=social_book_route.get_book_comment, methods=["GET"])

user_bp.add_url_rule("/create", view_func=user_route.create_user, methods=["POST"])
user_bp.add_url_rule("/delete", view_func=user_route.delete_user, methods=["POST"])
user_bp.add_url_rule("/login", view_func=user_route.login_route, methods=["POST"])
user_bp.add_url_rule("/logout", view_func=user_route.logout_route, methods=["POST"])
