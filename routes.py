from flask import render_template, request, jsonify, send_from_directory, current_app, abort
from sqlalchemy import func, or_
from models import CP, APN
from extensions import db
import os
import logging
from collections import defaultdict

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

    @app.route('/search_apn', methods=['GET'])
    def search_apn_form():
        """Display the form to search by APN."""
        return render_template('search_apn_form.html')

    @app.route('/search_apn_results', methods=['GET'])
    def search_apn_results():
        """Search for CPs containing a specific APN and display results."""
        apn_query = request.args.get('apn_dpn', '').strip()
        
        if not apn_query:
            return render_template('search_apn_form.html', error="Please enter an APN (DPN) to search.")
        
        # Find the APN record by DPN (case-insensitive search)
        target_apn = APN.query.filter(func.lower(APN.DPN) == func.lower(apn_query)).first()
        
        if not target_apn:
            return render_template('search_apn_form.html', error=f"APN with DPN '{apn_query}' not found.")
        
        target_pin_id = target_apn.PIN_id
        
        # Define the mapping between PIN fields and their corresponding quantity fields
        pin_to_qty_map = {
            CP.PIN1_ID: CP.Qte_1,
            CP.PIN2_ID: CP.Qte_2,
            CP.PIN3_ID: CP.Qte_3,
            CP.PIN4_ID: CP.QTE_4,
            CP.TIGE_1_ID: CP.Qte_Tige_1,
            CP.TIGE_2_ID: CP.Qte_Tige_2,
            # RESSORT fields might not have quantities, handle appropriately if needed
            # CP.RESSORT_1_ID: ?, 
            # CP.RESSORT_2_ID: ?
        }
        
        # Find all CPs that reference this APN's PIN_id
        cp_results = CP.query.filter(
            or_(
                CP.PIN1_ID == target_pin_id,
                CP.PIN2_ID == target_pin_id,
                CP.PIN3_ID == target_pin_id,
                CP.PIN4_ID == target_pin_id,
                CP.TIGE_1_ID == target_pin_id,
                CP.TIGE_2_ID == target_pin_id,
                CP.RESSORT_1_ID == target_pin_id,
                CP.RESSORT_2_ID == target_pin_id
            )
        ).order_by(CP.Client_ID_1, CP.PRJ_ID1, CP.CP).all()
        
        total_cps_found = len(cp_results)
        total_apn_quantity = 0
        cp_data_with_qty = [] # Store CP data along with the quantity of the searched APN
        found_in_carlines_set = set() # Use a set to store unique carlines

        # Calculate total quantity and quantity per CP
        for cp in cp_results:
            quantity_in_this_cp = 0
            if cp.PIN1_ID == target_pin_id and cp.Qte_1 is not None: quantity_in_this_cp += cp.Qte_1
            if cp.PIN2_ID == target_pin_id and cp.Qte_2 is not None: quantity_in_this_cp += cp.Qte_2
            if cp.PIN3_ID == target_pin_id and cp.Qte_3 is not None: quantity_in_this_cp += cp.Qte_3
            if cp.PIN4_ID == target_pin_id and cp.QTE_4 is not None: quantity_in_this_cp += cp.QTE_4 # Check column name
            if cp.TIGE_1_ID == target_pin_id and cp.Qte_Tige_1 is not None: quantity_in_this_cp += cp.Qte_Tige_1
            if cp.TIGE_2_ID == target_pin_id and cp.Qte_Tige_2 is not None: quantity_in_this_cp += cp.Qte_Tige_2
            # Add checks for RESSORT if they have quantities
            
            total_apn_quantity += quantity_in_this_cp
            cp_data_with_qty.append({'cp': cp, 'quantity': quantity_in_this_cp})
            
            # Add carline to the set
            if cp.PRJ_ID1:
                found_in_carlines_set.add(cp.PRJ_ID1)

        # Convert set to sorted list for consistent display
        found_in_carlines = sorted(list(found_in_carlines_set))

        # Group results by Customer (Client_ID_1) and Carline (PRJ_ID1)
        grouped_results = defaultdict(lambda: defaultdict(list))
        for item in cp_data_with_qty:
            cp = item['cp']
            quantity = item['quantity']
            customer = cp.Client_ID_1 or "Unknown Customer"
            carline = cp.PRJ_ID1 or "Unknown Carline"
            grouped_results[customer][carline].append({'cp': cp, 'quantity': quantity})
            
        # Import the helper function if needed in the results template
        from helpers import get_apn_details 

        return render_template(
            'results_apn.html',
            apn_query=apn_query,
            target_apn=target_apn,
            grouped_results=grouped_results,
            total_cps_found=total_cps_found,
            total_apn_quantity=total_apn_quantity, 
            found_in_carlines=found_in_carlines, # Pass the list of carlines
            get_apn_details=get_apn_details 
        )

    @app.route('/apn_database')
    def apn_database():
        """Display the entire APN database with total quantities across all CPs."""
        try:
            # Calculate total quantities for each APN PIN_id across all CPs
            apn_total_quantities = defaultdict(int)
            all_cps = CP.query.all()
            for cp in all_cps:
                if cp.PIN1_ID is not None and cp.Qte_1 is not None: apn_total_quantities[cp.PIN1_ID] += cp.Qte_1
                if cp.PIN2_ID is not None and cp.Qte_2 is not None: apn_total_quantities[cp.PIN2_ID] += cp.Qte_2
                if cp.PIN3_ID is not None and cp.Qte_3 is not None: apn_total_quantities[cp.PIN3_ID] += cp.Qte_3
                if cp.PIN4_ID is not None and cp.QTE_4 is not None: apn_total_quantities[cp.PIN4_ID] += cp.QTE_4
                if cp.TIGE_1_ID is not None and cp.Qte_Tige_1 is not None: apn_total_quantities[cp.TIGE_1_ID] += cp.Qte_Tige_1
                if cp.TIGE_2_ID is not None and cp.Qte_Tige_2 is not None: apn_total_quantities[cp.TIGE_2_ID] += cp.Qte_Tige_2
                # Ressort fields don't have associated quantity columns in the CP model

            # Fetch all APN records, ordered by DPN
            all_apns = APN.query.order_by(APN.DPN).all()
            
            # Combine APN data with calculated total quantities
            apn_data_with_total = []
            for apn in all_apns:
                total_db_quantity = apn_total_quantities.get(apn.PIN_id, 0)
                apn_data_with_total.append({
                    'apn': apn,
                    'total_db_quantity': total_db_quantity
                })

            return render_template('apn_database.html', apn_data=apn_data_with_total)
        except Exception as e:
            logging.error(f"Error fetching APN database: {str(e)}")
            abort(500) 

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('index.html', error="Page not found."), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('index.html', error="An internal server error occurred."), 500
