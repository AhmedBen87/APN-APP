from flask import render_template, request, jsonify, send_from_directory, current_app, abort
from sqlalchemy import func, or_
from models import CP, APN
from extensions import db
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def register_routes(app):
    @app.route('/aptiv_logo')
    def serve_aptiv_logo():
        try:
            return send_from_directory('attached_assets', 'aptiv-logo.svg')
        except Exception as e:
            logging.error(f"Error serving APTIV logo: {str(e)}")
            abort(500)

    @app.route('/cp_image/<path:filename>')
    def serve_cp_image(filename):
        try:
            image_path = os.path.join(current_app.config['CP_IMAGES_FOLDER'], filename)
            if not os.path.exists(image_path):
                logging.error(f"CP image not found: {image_path}")
                abort(404)
            logging.info(f"Serving CP image: {filename}")
            return send_from_directory(current_app.config['CP_IMAGES_FOLDER'], filename)
        except Exception as e:
            logging.error(f"Error serving CP image {filename}: {str(e)}")
            abort(500)

    @app.route('/cp_sub51_image/<path:filename>')
    def serve_cp_sub51_image(filename):
        try:
            image_path = os.path.join(current_app.config['CP_SUB51_IMAGES_FOLDER'], filename)
            if not os.path.exists(image_path):
                logging.error(f"CP_SUB51 image not found: {image_path}")
                abort(404)
            logging.info(f"Serving CP_SUB51 image: {filename}")
            return send_from_directory(current_app.config['CP_SUB51_IMAGES_FOLDER'], filename)
        except Exception as e:
            logging.error(f"Error serving CP_SUB51 image {filename}: {str(e)}")
            abort(500)

    @app.route('/search_suggestions')
    def search_suggestions():
        customer = request.args.get('customer')
        carline = request.args.get('carline')
        term = request.args.get('term', '').lower()
        
        query = CP.query.filter(
            func.lower(CP.Client_ID_1) == func.lower(customer),
            func.lower(CP.PRJ_ID1) == func.lower(carline),
            func.lower(CP.CP).contains(func.lower(term))
        ).limit(10)
        
        suggestions = [{'cp': cp.CP} for cp in query.all()]
        return jsonify(suggestions)

    @app.route('/')
    def index():
        """Render the landing page with customer selection"""
        # Get unique customers (Client_ID_1 values)
        customers = db.session.query(CP.Client_ID_1).distinct().order_by(CP.Client_ID_1).all()
        customers = [c[0] for c in customers if c[0]]  # Extract values and filter out None/empty values
        
        return render_template('index.html', customers=customers)

    @app.route('/get_carlines/<customer>')
    def get_carlines(customer):
        """Get car lines for a specific customer"""
        carlines = db.session.query(CP.PRJ_ID1)\
            .filter(CP.Client_ID_1 == customer)\
            .distinct()\
            .order_by(CP.PRJ_ID1)\
            .all()
        
        carlines = [c[0] for c in carlines if c[0]]  # Extract values and filter out None/empty values
        
        return jsonify(carlines)

    @app.route('/search')
    def search():
        """Search for a CP and return the results"""
        customer = request.args.get('customer')
        carline = request.args.get('carline')
        cp_name = request.args.get('cp_name')
        
        if not all([customer, carline, cp_name]):
            return render_template('results.html', error="All search parameters are required.")
        
        # Normalize the search terms
        customer = customer.strip().upper()
        carline = carline.strip().upper()
        cp_name = cp_name.strip().upper()
        
        # Search for the CP with matching criteria
        cp_results = CP.query.filter(
            func.upper(CP.Client_ID_1) == customer,
            func.upper(CP.PRJ_ID1) == carline,
            or_(
                func.upper(CP.CP).startswith(cp_name),
                func.upper(CP.CP).startswith(cp_name + ' L/R'),
                func.upper(CP.CP).startswith(cp_name + ' L_R')
            )
        ).all()
        
        if not cp_results:
            return render_template('results.html', error="No matching CP found.")
        
        # Import the get_apn_details function
        from helpers import get_apn_details
        
        # Return all matching results
        return render_template(
            'results.html',
            cps=cp_results,
            get_apn_details=get_apn_details,  # Pass the function to the template
            error=None
        )

    @app.route('/apn_image/<path:filename>')
    def serve_apn_image(filename):
        try:
            image_path = os.path.join(current_app.config['APN_IMAGES_FOLDER'], filename)
            if not os.path.exists(image_path):
                logging.error(f"APN image not found: {image_path}")
                abort(404)
            logging.info(f"Serving APN image: {filename}")
            return send_from_directory(current_app.config['APN_IMAGES_FOLDER'], filename)
        except Exception as e:
            logging.error(f"Error serving APN image {filename}: {str(e)}")
            abort(500)

    @app.route('/apn_pin_image/<path:filename>')
    def serve_apn_pin_image(filename):
        try:
            image_path = os.path.join(current_app.config['APN_PIN_IMAGES_FOLDER'], filename)
            if not os.path.exists(image_path):
                logging.error(f"APN PIN image not found: {image_path}")
                abort(404)
            logging.info(f"Serving APN PIN image: {filename}")
            return send_from_directory(current_app.config['APN_PIN_IMAGES_FOLDER'], filename)
        except Exception as e:
            logging.error(f"Error serving APN PIN image {filename}: {str(e)}")
            abort(500)

    @app.route('/customer_logo/<path:filename>')
    def serve_customer_logo(filename):
        try:
            image_path = os.path.join('attached_assets', 'CUSTOMER', filename)
            if not os.path.exists(image_path):
                logging.error(f"Customer logo not found: {image_path}")
                abort(404)
            logging.info(f"Serving customer logo: {filename}")
            return send_from_directory(os.path.join('attached_assets', 'CUSTOMER'), filename)
        except Exception as e:
            logging.error(f"Error serving customer logo {filename}: {str(e)}")
            abort(500)

    @app.route('/static/images/<path:filename>')
    def serve_profile_image(filename):
        try:
            return send_from_directory('static/images', filename)
        except Exception as e:
            logging.error(f"Error serving profile image {filename}: {str(e)}")
            abort(404)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('index.html', error="Page not found."), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('index.html', error="An internal server error occurred."), 500
