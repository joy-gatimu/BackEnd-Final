from flask import request, jsonify
from flask_restx import Api, Resource, fields
from .models import db, User, Property, Booking, Review, Image
from datetime import datetime


api = Api(title="Air-bnb API", description="A REST API for an Airbnb-like system", version="1.0")

# Define namespaces
user_ns = api.namespace('users', description="User operations")
property_ns = api.namespace('properties', description="Property operations")
booking_ns = api.namespace('bookings', description="Booking operations")
review_ns = api.namespace('reviews', description="Review operations")
image_ns = api.namespace('images', description="Image operations")


# ----------- Models -----------
user_model = api.model('User', {
    'username': fields.String(required=True, description="Username of the user"),
    'email': fields.String(required=True, description="Email address of the user"),
    'password': fields.String(required=True, description="Password for the user account"),
})

property_model = api.model('Property', {
    'name': fields.String(required=True, description="Name of the property"),
    'description': fields.String(required=True, description="Description of the property"),
    'price_per_night': fields.Float(required=True, description="Price per night for the property"),
    'owner_id': fields.Integer(required=True, description="ID of the property owner"),
})

booking_model = api.model('Booking', {
    'user_id': fields.Integer(required=True, description="ID of the user making the booking"),
    'property_id': fields.Integer(required=True, description="ID of the property being booked"),
    'check_in': fields.String(required=True, description="Check-in date (YYYY-MM-DD)"),
    'check_out': fields.String(required=True, description="Check-out date (YYYY-MM-DD)"),
    'total_price': fields.Float(required=True, description="Total price for the booking"),
})

review_model = api.model('Review', {
    'user_id': fields.Integer(required=True, description="ID of the user writing the review"),
    'property_id': fields.Integer(required=True, description="ID of the property being reviewed"),
    'rating': fields.Integer(required=True, description="Rating for the property (1-5)"),
    'comment': fields.String(description="Optional comment for the review"),
})

image_model = api.model('Image', {
    'property_id': fields.Integer(required=True, description="ID of the property the image belongs to"),
    'url': fields.String(required=True, description="URL of the image"),
    'description': fields.String(description="Optional description of the image"),
})




# ----------- User Routes -----------
# ----------- Login Route -----------
@user_ns.route('/login/')
class Login(Resource):
    def post(self):
        """Login a user"""
        data = request.json
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):  # Check if user exists and password matches
            return {"error": "Invalid credentials"}, 401

     
        return {"message": "Login successful", "email": user}, 200
@user_ns.route('/')
class UserList(Resource):
    def get(self):
        """Get all users"""
        users = User.query.all()
        return [{"id": u.id, "username": u.username, "email": u.email} for u in users]

    @api.expect(user_model)
    def post(self):
        """Create a new user"""
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if User.query.filter_by(email=email).first():
            return {"error": "Email already registered"}, 400

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return {"message": "User created successfully"}, 201

@user_ns.route('/<int:user_id>')
class UserDetail(Resource):
    def get(self, user_id):
        """Get details of a single user"""
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        return {"id": user.id, "username": user.username, "email": user.email}

# ----------- Property Routes -----------
@property_ns.route('/')
class PropertyList(Resource):
    def get(self):
        """Get all properties"""
        properties = Property.query.all()
        return [{"id": p.id, "name": p.name, "description": p.description, "price_per_night": p.price_per_night} for p in properties]

    @api.expect(property_model)
    def post(self):
        """Add a new property"""
        data = request.json
        name = data.get('name')
        description = data.get('description')
        price_per_night = data.get('price_per_night')
        owner_id = data.get('owner_id')

        if not User.query.get(owner_id):
            return {"error": "Owner not found"}, 404

        new_property = Property(name=name, description=description, price_per_night=price_per_night, owner_id=owner_id)
        db.session.add(new_property)
        db.session.commit()
        return {"message": "Property added successfully"}, 201

@property_ns.route('/<int:property_id>')
class PropertyDetail(Resource):
    def get(self, property_id):
        """Get details of a single property"""
        prop = Property.query.get(property_id)
        if not prop:
            return {"error": "Property not found"}, 404

        return {
            "id": prop.id,
            "name": prop.name,
            "description": prop.description,
            "price_per_night": prop.price_per_night,
            "owner": {"id": prop.owner.id, "username": prop.owner.username}
        }

# ----------- Booking Routes -----------
@booking_ns.route('/')
class BookingList(Resource):
    def get(self):
        """Get all bookings"""
        try:
            bookings = Booking.query.all()
            return [
                {"id": b.id, "user_id": b.user_id, "property_id": b.property_id, "check_in": b.check_in, "check_out": b.check_out, "total_price": b.total_price}
                for b in bookings
            ], 200
        except Exception as e:
            return {"message": "Error fetching bookings", "error": str(e)}, 500

    @api.expect(booking_model)
    def post(self):
        """Create a new booking"""
        data = request.json
        
        # Extract booking data
        user_id = data.get('user_id')
        property_id = data.get('property_id')
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        total_price = data.get('total_price')  # This could be auto-calculated if not provided
        
        try:
            # Validate if the user and property exist
            user = User.query.get(user_id)
            property = Property.query.get(property_id)
            
            if not user:
                return {"error": "User not found"}, 404
            if not property:
                return {"error": "Property not found"}, 404

            # Validate the date format (YYYY-MM-DD)
            try:
                check_in = datetime.strptime(check_in, '%Y-%m-%d').date()
                check_out = datetime.strptime(check_out, '%Y-%m-%d').date()
            except ValueError:
                return {"error": "Invalid date format. Use YYYY-MM-DD."}, 400

           
            if check_out <= check_in:
                return {"error": "Check-out date must be after check-in date."}, 400

 
            if not total_price:
                days = (check_out - check_in).days
                if days <= 0:
                    return {"error": "Check-out date must be later than check-in date."}, 400
                total_price = property.price_per_night * days

            # Create the booking
            new_booking = Booking(
                user_id=user_id,
                property_id=property_id,
                check_in=check_in,
                check_out=check_out,
                total_price=total_price
            )

            db.session.add(new_booking)
            db.session.commit()

            # Return the response with the created booking details
            return {"message": "Booking created successfully", "booking_id": new_booking.id}, 201

        except Exception as e:
            db.session.rollback()  # Rollback the session in case of any error
            return {"message": "Error creating booking", "error": str(e)}, 500


# ----------- Review Routes -----------
@review_ns.route('/')
class ReviewList(Resource):
    def get(self):
        """Get all reviews"""
        reviews = Review.query.all()
        return [
            {
                "id": r.id,
                "property_id": r.property_id,
                "user_id": r.user_id,
                "rating": r.rating,
                "comment": r.comment,
            }
            for r in reviews
        ]

    @api.expect(review_model)
    def post(self):
        """Create a new review"""
        data = request.json
        property_id = data.get('property_id')
        user_id = data.get('user_id')
        rating = data.get('rating')
        comment = data.get('comment')

        if not Property.query.get(property_id):
            return {"error": "Property not found"}, 404
        if not User.query.get(user_id):
            return {"error": "User not found"}, 404

        if rating < 1 or rating > 5:
            return {"error": "Rating must be between 1 and 5"}, 400

        new_review = Review(
            property_id=property_id, user_id=user_id, rating=rating, comment=comment
        )
        db.session.add(new_review)
        db.session.commit()
        return {"message": "Review created successfully"}, 201


@review_ns.route('/<int:review_id>')
class ReviewDetail(Resource):
    def get(self, review_id):
        """Get details of a single review"""
        review = Review.query.get(review_id)
        if not review:
            return {"error": "Review not found"}, 404

        return {
            "id": review.id,
            "property_id": review.property_id,
            "user_id": review.user_id,
            "rating": review.rating,
            "comment": review.comment,
        }


# ----------- Image Routes -----------
@image_ns.route('/')
class ImageList(Resource):
    def get(self):
        """Get all images"""
        images = Image.query.all()
        return [
            {
                "id": img.id,
                "property_id": img.property_id,
                "url": img.url,
                "description": img.description,
            }
            for img in images
        ]

    @api.expect(image_model)
    def post(self):
        """Add a new image"""
        data = request.json
        property_id = data.get('property_id')
        url = data.get('url')
        description = data.get('description')

        if not Property.query.get(property_id):
            return {"error": "Property not found"}, 404

        new_image = Image(property_id=property_id, url=url, description=description)
        db.session.add(new_image)
        db.session.commit()
        return {"message": "Image added successfully"}, 201


@image_ns.route('/<int:image_id>')
class ImageDetail(Resource):
    def get(self, image_id):
        """Get details of a single image"""
        image = Image.query.get(image_id)
        if not image:
            return {"error": "Image not found"}, 404
    



        return {
            "id": image.id,
            "property_id": image.property_id,
            "url": image.url,
            "description": image.description,
        }
# Add namespaces to the API
api.add_namespace(user_ns)
api.add_namespace(property_ns)
api.add_namespace(booking_ns)
api.add_namespace(review_ns)
api.add_namespace(image_ns)