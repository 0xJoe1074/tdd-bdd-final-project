from flask import jsonify, request, abort, url_for
from service.models import Product, Category  # Category hinzugefügt
from service.common import status
from . import app

# ... (Health Check, Index und check_content_type bleiben gleich)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )

######################################################################
# C R E A T E   A   N E W   P R O D U C T
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    app.logger.info("Request to Create a Product...")
    check_content_type("application/json")
    data = request.get_json()
    product = Product()
    product.deserialize(data)
    product.create()
    
    message = product.serialize()
    # Location URL fix:
    location_url = url_for("get_products", product_id=product.id, _external=True)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}

######################################################################
# R E A D   A   P R O D U C T
######################################################################
@app.route("/products/<int:product_id>", methods=["GET"])
def get_products(product_id):
    app.logger.info("Request to Retrieve a product with id [%s]", product_id)
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")
    return jsonify(product.serialize()), status.HTTP_200_OK

######################################################################
# U P D A T E   A   P R O D U C T
######################################################################
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_products(product_id):
    app.logger.info("Request to Update a product with id [%s]", product_id)
    check_content_type("application/json")
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")
    product.deserialize(request.get_json())
    product.id = product_id
    product.update()
    return jsonify(product.serialize()), status.HTTP_200_OK

######################################################################
# D E L E T E   A   P R O D U C T
######################################################################
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_products(product_id):
    app.logger.info("Request to Delete a product with id [%s]", product_id)
    product = Product.find(product_id)
    if product:
        product.delete()
    return "", status.HTTP_204_NO_CONTENT

######################################################################
# L I S T   P R O D U C T S
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    app.logger.info("Request to list Products...")
    products = []
    name = request.args.get("name")
    category = request.args.get("category")
    available = request.args.get("available")

    if name:
        products = Product.find_by_name(name)
    elif category:
        category_value = getattr(Category, category.upper())
        products = Product.find_by_category(category_value)
    elif available:
        available_value = available.lower() in ["true", "yes", "1"]
        products = Product.find_by_availability(available_value)
    else:
        products = Product.all()

    results = [product.serialize() for product in products]
    return jsonify(results), status.HTTP_200_OK

@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="OK"), status.HTTP_200_OK

@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")