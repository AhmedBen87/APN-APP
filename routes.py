from flask import render_template, request, jsonify, send_from_directory, current_app, abort, redirect, url_for, flash, session
from sqlalchemy import func, or_, case
from sqlalchemy.orm import aliased, selectinload
from models import CP, APN, User
from extensions import db
from flask_login import login_user, logout_user, login_required, current_user
import os
import logging
from collections import defaultdict
from functools import wraps
from werkzeug.utils import secure_filename
from helpers import parse_location
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Admin required decorator 
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You need administrator privileges to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# === Authentication ===
# Removed hardcoded credentials in favor of database-backed users

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        # Use selectinload to eager load related APNs and prevent N+1 queries
        cp_results = CP.query.options(
            selectinload(CP.apn1),
            selectinload(CP.apn2),
            selectinload(CP.apn3),
            selectinload(CP.apn4),
            selectinload(CP.apn5),
            selectinload(CP.apn6),
            selectinload(CP.apn7),
            selectinload(CP.apn8)
        ).filter(
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
        search_type = request.args.get('search_type', 'apn')
        query_value = request.args.get('apn_dpn', '').strip()
        
        if not query_value:
            return render_template('search_apn_form.html', error="Please enter a value to search.")
        
        # Initialize target_apn to None
        target_apn = None
        
        # Different search logic based on search_type
        if search_type == 'apn':
            # Original APN/DPN search
            target_apn = APN.query.filter(func.lower(APN.DPN) == func.lower(query_value)).first()
            if not target_apn:
                return render_template('search_apn_form.html', 
                                      error=f"APN with DPN '{query_value}' not found.",
                                      search_type=search_type)
        
        elif search_type == 'emdep':
            # Search by Emdep reference
            target_apn = APN.query.filter(func.lower(APN.Ref_Emdep) == func.lower(query_value)).first()
            if not target_apn:
                return render_template('search_apn_form.html', 
                                      error=f"No APN found with Emdep reference '{query_value}'.",
                                      search_type=search_type)
        
        elif search_type == 'fenmmital':
            # Search by Fenmmital reference
            target_apn = APN.query.filter(func.lower(APN.Ref_Fenmmital) == func.lower(query_value)).first()
            if not target_apn:
                return render_template('search_apn_form.html', 
                                      error=f"No APN found with Fenmmital reference '{query_value}'.",
                                      search_type=search_type)
        
        elif search_type == 'ingun':
            # Search by Ingun reference
            target_apn = APN.query.filter(func.lower(APN.Ref_Ingun) == func.lower(query_value)).first()
            if not target_apn:
                return render_template('search_apn_form.html', 
                                      error=f"No APN found with Ingun reference '{query_value}'.",
                                      search_type=search_type)
        
        elif search_type == 'ptr':
            # Search by PTR reference
            target_apn = APN.query.filter(func.lower(APN.Ref_Ptr) == func.lower(query_value)).first()
            if not target_apn:
                return render_template('search_apn_form.html', 
                                      error=f"No APN found with PTR reference '{query_value}'.",
                                      search_type=search_type)
        
        # If we don't have an APN by now, something went wrong with the search type
        if not target_apn:
            return render_template('search_apn_form.html', 
                                  error=f"Invalid search or no results found.",
                                  search_type=search_type)
        
        # Continue with existing logic using the target_apn we found
        target_pin_id = target_apn.PIN_id
        
        # Define the mapping between PIN fields and their corresponding quantity fields
        # Use the actual Column objects as keys
        pin_to_qty_map = {
            CP.PIN1_ID.key: CP.Qte_1.key,
            CP.PIN2_ID.key: CP.Qte_2.key,
            CP.PIN3_ID.key: CP.Qte_3.key,
            CP.PIN4_ID.key: CP.QTE_4.key, # Careful with column name
            CP.TIGE_1_ID.key: CP.Qte_Tige_1.key,
            CP.TIGE_2_ID.key: CP.Qte_Tige_2.key,
            # RESSORT fields do not have quantity columns in the model
            CP.RESSORT_1_ID.key: None,
            CP.RESSORT_2_ID.key: None 
        }
        
        # Find all CPs that reference this APN's PIN_id
        # Consider adding selectinload here too if performance is critical for APN search page
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
        cp_data_with_qty = []

        # Calculate total quantity and quantity per CP (Simplified)
        for cp in cp_results:
            quantity_in_this_cp = 0
            for pin_key, qty_key in pin_to_qty_map.items():
                # Check if the current PIN field matches the target and has a quantity field
                if getattr(cp, pin_key) == target_pin_id and qty_key is not None:
                    qty_value = getattr(cp, qty_key)
                    if qty_value is not None:
                        quantity_in_this_cp += qty_value
            
            total_apn_quantity += quantity_in_this_cp
            cp_data_with_qty.append({'cp': cp, 'quantity': quantity_in_this_cp})

        # Convert set to sorted list for consistent display
        found_in_carlines_set = set() # Use a set to store unique carlines

        # Add carline to the set
        for cp in cp_results:
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

        # Include search type and original query in the context
        return render_template(
            'results_apn.html',
            apn_query=query_value,
            search_type=search_type,
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
            # Efficiently calculate total quantities using database aggregation
            # We need to sum quantities based on which PIN_ID matches
            qty_sums = db.session.query(
                APN.PIN_id,
                func.sum(
                    case(
                        (CP.PIN1_ID == APN.PIN_id, CP.Qte_1),
                        (CP.PIN2_ID == APN.PIN_id, CP.Qte_2),
                        (CP.PIN3_ID == APN.PIN_id, CP.Qte_3),
                        (CP.PIN4_ID == APN.PIN_id, CP.QTE_4),
                        (CP.TIGE_1_ID == APN.PIN_id, CP.Qte_Tige_1),
                        (CP.TIGE_2_ID == APN.PIN_id, CP.Qte_Tige_2),
                        # Add RESSORT here if they ever get quantities
                        else_=0 # Ensure we sum 0 if no match or quantity is null
                    ).cast(db.Integer) # Cast case statement result to Integer for sum
                ).label('total_quantity')
            ).join(CP, 
                or_(
                     CP.PIN1_ID == APN.PIN_id, 
                     CP.PIN2_ID == APN.PIN_id,
                     CP.PIN3_ID == APN.PIN_id,
                     CP.PIN4_ID == APN.PIN_id,
                     CP.TIGE_1_ID == APN.PIN_id,
                     CP.TIGE_2_ID == APN.PIN_id,
                     CP.RESSORT_1_ID == APN.PIN_id,
                     CP.RESSORT_2_ID == APN.PIN_id
                )
             ).group_by(APN.PIN_id).all()
            
            # Convert results to a dictionary for easy lookup
            apn_total_quantities = {pin_id: total for pin_id, total in qty_sums}

            # Fetch all APN records, ordered by DPN
            all_apns = APN.query.order_by(APN.DPN).all()
            
            # Combine APN data with calculated total quantities
            apn_data_with_total = []
            for apn in all_apns:
                total_db_quantity = apn_total_quantities.get(apn.PIN_id, 0)
                apn_data_with_total.append({
                    'apn': apn,
                    'total_db_quantity': total_db_quantity if total_db_quantity is not None else 0 # Handle potential None from sum
                })

            return render_template('apn_database.html', apn_data=apn_data_with_total)
        except Exception as e:
            logging.error(f"Error fetching APN database: {str(e)}")
            # Log the full traceback for better debugging
            logging.exception("Traceback:") 
            abort(500)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('index.html', error="Page not found."), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('index.html', error="An internal server error occurred."), 500

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                flash('Please provide both username and password', 'warning')
                return redirect(url_for('login'))
                
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                flash(f'Welcome back, {user.username}!', 'success')
                
                # Redirect to the page the user was trying to access, or to index
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
            else:
                flash('Invalid username or password', 'danger')
                
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out', 'info')
        return redirect(url_for('index'))

    # === Add/Update Routes ===

    @app.route('/add_apn', methods=['GET', 'POST'])
    @login_required
    def add_apn_form():
        """Display form to add a new APN and handle submission with image upload."""
        if request.method == 'POST':
            try:
                # Extract data from form
                dpn = request.form.get('dpn')
                apn_type = request.form.get('type')
                ref_emdep = request.form.get('ref_emdep')
                ref_ingun = request.form.get('ref_ingun')
                ref_fenmmital = request.form.get('ref_fenmmital')
                ref_ptr = request.form.get('ref_ptr')
                multi_apn = request.form.get('multi_apn')
                
                # Get location from dropdown inputs
                location_cabinet = request.form.get('location_cabinet', '').strip()
                location_drawer = request.form.get('location_drawer', '').strip()
                
                # Combine into full location if both are selected
                location = ''
                if location_cabinet and location_drawer:
                    location = f"ARMOIRE {location_cabinet}-{location_drawer}"
                
                # Handle file upload
                image_file = request.files.get('image')
                image_path_to_save = None # Path to store in DB

                # Basic validation
                if not dpn or not apn_type:
                    flash('DPN and Type are required fields.', 'warning')
                    return render_template('add_apn_form.html', form_data=request.form)
                
                # Validate and process image if uploaded
                if image_file and image_file.filename != '':
                    if allowed_file(image_file.filename):
                        filename = secure_filename(image_file.filename) 
                        # Determine save directory based on type
                        if apn_type == 'PIN':
                            save_dir_key = 'APN_PIN_IMAGES_FOLDER' # e.g., static/apn_pin_images
                            relative_path_prefix = 'pin'       # To store /pin/filename.jpg in DB
                        else:
                            save_dir_key = 'APN_IMAGES_FOLDER'     # e.g., static/apn_images
                            relative_path_prefix = 'apn'       # To store /apn/filename.jpg in DB
                        
                        save_dir = current_app.config[save_dir_key]
                        # Ensure directory exists (should be created by app factory, but double check)
                        os.makedirs(save_dir, exist_ok=True)
                        
                        full_save_path = os.path.join(save_dir, filename)
                        image_file.save(full_save_path)
                        
                        # Store the relative path for the database
                        # Use forward slashes for web paths
                        image_path_to_save = f"/{relative_path_prefix}/{filename}"
                        logging.info(f"Saved uploaded image to: {full_save_path}")
                        logging.info(f"Database image path: {image_path_to_save}")
                    else:
                        flash('Invalid image file type. Allowed types: png, jpg, jpeg.', 'warning')
                        return render_template('add_apn_form.html', form_data=request.form)
                else:
                    logging.info("No image file uploaded.")

                # Check if DPN already exists
                existing_apn = APN.query.filter(func.lower(APN.DPN) == func.lower(dpn)).first()
                if existing_apn:
                    flash(f'APN with DPN \'{dpn}\' already exists (PIN ID: {existing_apn.PIN_id}).', 'danger')
                    return render_template('add_apn_form.html', form_data=request.form)

                # Create new APN object
                new_apn = APN(
                    DPN=dpn,
                    Type=apn_type,
                    Image=image_path_to_save, # Use the saved relative path
                    Ref_Emdep=ref_emdep,
                    Ref_Ingun=ref_ingun,
                    Ref_Fenmmital=ref_fenmmital,
                    Ref_Ptr=ref_ptr,
                    Multi_APN=multi_apn,
                    Location=location
                )
                
                # Add to database
                db.session.add(new_apn)
                db.session.commit()
                
                flash(f'Successfully added APN: {new_apn.DPN}', 'success')
                return redirect(url_for('apn_database')) # Redirect to database view

            except Exception as e:
                db.session.rollback() # Rollback in case of error
                logging.error(f"Error adding new APN: {str(e)}")
                logging.exception("Traceback:")
                flash('Error adding APN. Please check logs.', 'danger')
        
        # GET request
        return render_template('add_apn_form.html')

    @app.route('/add_cp', methods=['GET', 'POST'])
    @login_required
    def add_cp_form():
        """Display form to add a new CP and handle submission with dynamic customer/carline."""
        
        # Fetch existing customers for dropdown
        existing_customers = db.session.query(CP.Client_ID_1).distinct().order_by(CP.Client_ID_1).all()
        customers = [c[0] for c in existing_customers if c[0]]
        
        if request.method == 'POST':
            try:
                # --- Determine Customer --- 
                selected_customer_option = request.form.get('customer_select')
                client_id = None
                is_new_customer = False
                if selected_customer_option == '__NEW__':
                    client_id = request.form.get('new_customer_name', '').strip().upper()
                    if not client_id:
                        flash('New Customer Name cannot be empty.', 'warning')
                        return render_template('add_cp_form.html', customers=customers, form_data=request.form)
                    # Optional: Check if new name conflicts with existing
                    if client_id in customers:
                         flash(f'Customer \'{client_id}\' already exists. Please select it from the list.', 'warning')
                         return render_template('add_cp_form.html', customers=customers, form_data=request.form)
                    is_new_customer = True
                elif selected_customer_option:
                    client_id = selected_customer_option # Already uppercase from DB query logic usually
                else:
                    flash('Please select an existing customer or add a new one.', 'warning')
                    return render_template('add_cp_form.html', customers=customers, form_data=request.form)
                
                # --- Handle New Customer Logo Upload ---
                if is_new_customer:
                    logo_file = request.files.get('new_customer_logo')
                    if logo_file and logo_file.filename != '':
                        if allowed_file(logo_file.filename):
                            # Use customer name for logo filename, ensuring it's safe
                            filename_base = secure_filename(client_id)
                            _, ext = os.path.splitext(logo_file.filename)
                            logo_filename = f"{filename_base}{ext.lower()}"
                            
                            logo_save_dir = os.path.join(current_app.root_path, 'attached_assets', 'CUSTOMER')
                            os.makedirs(logo_save_dir, exist_ok=True)
                            full_logo_path = os.path.join(logo_save_dir, logo_filename)
                            logo_file.save(full_logo_path)
                            logging.info(f"Saved new customer logo: {full_logo_path}")
                        else:
                            flash('Invalid file type for customer logo. Allowed: png, jpg, jpeg.', 'warning')
                            return render_template('add_cp_form.html', customers=customers, form_data=request.form)

                # --- Determine Carline --- 
                selected_carline_option = request.form.get('carline_select')
                prj_id = None
                if selected_carline_option == '__NEW__':
                    prj_id = request.form.get('new_carline_name', '').strip().upper()
                    if not prj_id:
                        flash('New Carline Name cannot be empty.', 'warning')
                        return render_template('add_cp_form.html', customers=customers, form_data=request.form)
                    # Optional: Check if new carline name conflicts with existing for this customer (more complex query needed)
                elif selected_carline_option:
                     prj_id = selected_carline_option
                else:
                     # This case should ideally be caught by client-side JS validation
                     flash('Please select a carline or add a new one.', 'warning')
                     return render_template('add_cp_form.html', customers=customers, form_data=request.form)

                # --- Other CP Data ---
                cp_name = request.form.get('cp_name')
                ot_ref = request.form.get('ot_ref')
                cp_type = request.form.get('cp_type') # 'main' or 'sub51'

                # --- Extract APNs --- (Same as before)
                apn_inputs = {}
                pin_fields = ['PIN1', 'PIN2', 'PIN3', 'PIN4', 'TIGE_1', 'TIGE_2', 'RESSORT_1', 'RESSORT_2']
                for field in pin_fields:
                    dpn = request.form.get(f'{field}_DPN')
                    qty = request.form.get(f'Qte_{field}')
                    # Handle potential naming mismatch for QTE_4
                    if field == 'PIN4':
                        qty = request.form.get('QTE_4') 
                    apn_inputs[field] = {'dpn': dpn.strip() if dpn else None, 'qty': qty}
                
                # --- Basic Validation (Remaining) ---
                if not all([cp_name, cp_type]): # Customer/Carline checked above
                    flash('CP Name and CP Type are required.', 'warning')
                    return render_template('add_cp_form.html', customers=customers, form_data=request.form)
                
                # --- CP Image Handling --- (Same as before)
                image_file = request.files.get('image')
                image_path_to_save = None
                if image_file and image_file.filename != '':
                    if allowed_file(image_file.filename):
                        filename = secure_filename(image_file.filename)
                        if cp_type == 'sub51':
                            save_dir = current_app.config['CP_SUB51_IMAGES_FOLDER']
                            relative_path_prefix = 'CP_SUB51' # Matching example path in existing data
                        else: # Default to main
                            save_dir = current_app.config['CP_IMAGES_FOLDER']
                            relative_path_prefix = 'CP'       # Matching example path
                        
                        os.makedirs(save_dir, exist_ok=True)
                        full_save_path = os.path.join(save_dir, filename)
                        image_file.save(full_save_path)
                        image_path_to_save = f"/{relative_path_prefix}/{filename}"
                        logging.info(f"Saved CP image to: {full_save_path}")
                    else:
                        flash('Invalid CP image file type. Allowed: png, jpg, jpeg.', 'warning')
                        return render_template('add_cp_form.html', customers=customers, form_data=request.form)

                # --- APN Lookup and Validation --- (Same as before)
                cp_data = {
                    'Client_ID_1': client_id, # Use determined client_id
                    'PRJ_ID1': prj_id,       # Use determined prj_id
                    'CP': cp_name,
                    'OT_rfrence': ot_ref,
                    'Image': image_path_to_save
                }
                valid_apns = True
                # Map the form field base ('PIN1', 'TIGE_1', etc.) to the correct CP model key for quantity
                field_to_qty_model_key = {
                    'PIN1': 'Qte_1',
                    'PIN2': 'Qte_2',
                    'PIN3': 'Qte_3',
                    'PIN4': 'QTE_4',
                    'TIGE_1': 'Qte_Tige_1',
                    'TIGE_2': 'Qte_Tige_2'
                    # RESSORT fields have no quantity in the model
                }

                for field, data in apn_inputs.items():
                    pin_id = None
                    qty_val = None
                    if data['dpn']: # If a DPN was entered for this slot
                        found_apn = APN.query.filter(func.lower(APN.DPN) == func.lower(data['dpn'])).first()
                        if not found_apn:
                            flash(f'APN with DPN \'{data["dpn"]}\' not found in database for field {field}. Please add it first.', 'danger')
                            valid_apns = False
                        else:
                            pin_id = found_apn.PIN_id
                    
                    # Get the correct quantity model key (e.g., 'Qte_1') from the map
                    # Use .get() to handle fields like RESSORT which aren't in the map
                    qty_model_key = field_to_qty_model_key.get(field)

                    if pin_id is not None and qty_model_key:
                        try:
                            qty_val = int(data['qty']) if data['qty'] and data['qty'].strip() else None 
                        except (ValueError, TypeError):
                            flash(f'Invalid quantity \'{data["qty"]}\' entered for {field}.', 'danger')
                            valid_apns = False
                    
                    # Add the ID field (e.g., PIN1_ID)
                    cp_data[f'{field}_ID'] = pin_id
                    # Add the Quantity field IF it exists for this field type (e.g., Qte_1)
                    if qty_model_key:
                         cp_data[qty_model_key] = qty_val

                if not valid_apns:
                    return render_template('add_cp_form.html', customers=customers, form_data=request.form)

                # --- Create and Save CP --- (Now uses correct keys)
                new_cp = CP(**cp_data) 
                db.session.add(new_cp)
                db.session.commit()

                flash(f'Successfully added CP: {new_cp.CP}', 'success')
                return redirect(url_for('index')) 

            except Exception as e:
                db.session.rollback()
                logging.error(f"Error adding new CP: {str(e)}")
                logging.exception("Traceback:")
                flash('Error adding CP. Please check logs.', 'danger')
                return render_template('add_cp_form.html', customers=customers, form_data=request.form)
        
        # GET request: display empty form with existing customers
        # Pass an empty dict for form_data on initial load
        return render_template('add_cp_form.html', customers=customers, form_data={})

    # === AJAX Endpoints ===

    @app.route('/check_apn/<dpn>')
    @login_required # Ensure only logged-in users can check
    def check_apn_exists(dpn):
        """Check if an APN DPN exists (case-insensitive). Returns JSON."""
        if not dpn or not dpn.strip():
            return jsonify({'exists': False, 'error': 'DPN cannot be empty'}), 400
            
        found_apn = APN.query.filter(func.lower(APN.DPN) == func.lower(dpn.strip())).first()
        return jsonify({'exists': found_apn is not None})

    @app.route('/ajax/add_apn', methods=['POST'])
    @login_required
    def ajax_add_apn():
        """Handle APN addition via AJAX from modal. Returns JSON."""
        try:
            # Reuse the same logic as add_apn_form POST, but return JSON
            dpn = request.form.get('dpn')
            apn_type = request.form.get('type')
            image_file = request.files.get('image')
            ref_emdep = request.form.get('ref_emdep')
            ref_ingun = request.form.get('ref_ingun')
            ref_fenmmital = request.form.get('ref_fenmmital')
            ref_ptr = request.form.get('ref_ptr')
            multi_apn = request.form.get('multi_apn')
            
            image_path_to_save = None
            errors = {}

            if not dpn or not dpn.strip(): errors['dpn'] = 'DPN is required.'
            if not apn_type: errors['type'] = 'Type is required.'
            
            # Check if DPN already exists before trying to save
            if dpn and not errors.get('dpn'):
                existing_apn = APN.query.filter(func.lower(APN.DPN) == func.lower(dpn.strip())).first()
                if existing_apn:
                     errors['dpn'] = f'DPN \'{dpn}\' already exists (ID: {existing_apn.PIN_id}).'
            
            # Handle image upload (similar logic to non-AJAX route)
            if image_file and image_file.filename != '':
                if allowed_file(image_file.filename):
                    filename = secure_filename(image_file.filename)
                    if apn_type == 'PIN': # Requires apn_type to be selected
                        save_dir_key = 'APN_PIN_IMAGES_FOLDER'
                        relative_path_prefix = 'pin'
                    else:
                        save_dir_key = 'APN_IMAGES_FOLDER'
                        relative_path_prefix = 'apn'
                    
                    save_dir = current_app.config[save_dir_key]
                    os.makedirs(save_dir, exist_ok=True)
                    full_save_path = os.path.join(save_dir, filename)
                    image_file.save(full_save_path)
                    image_path_to_save = f"/{relative_path_prefix}/{filename}"
                else:
                    errors['image'] = 'Invalid image file type.'

            if errors:
                return jsonify({'success': False, 'errors': errors}), 400 # Bad request status

            # If validation passes, create and save
            new_apn = APN(
                DPN=dpn.strip(), Type=apn_type, Image=image_path_to_save,
                Ref_Emdep=ref_emdep, Ref_Ingun=ref_ingun,
                Ref_Fenmmital=ref_fenmmital, Ref_Ptr=ref_ptr,
                Multi_APN=multi_apn
            )
            db.session.add(new_apn)
            db.session.commit()
            
            # Return success and potentially the new APN details
            return jsonify({
                'success': True, 
                'message': f'APN {new_apn.DPN} added successfully.',
                'new_apn': {'dpn': new_apn.DPN, 'pin_id': new_apn.PIN_id}
            })

        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding APN via AJAX: {str(e)}")
            logging.exception("Traceback:")
            return jsonify({'success': False, 'errors': {'general': 'Server error occurred.'}}), 500

    # Route to Edit an existing APN
    @app.route('/edit_apn/<int:pin_id>', methods=['GET', 'POST'])
    @login_required
    def edit_apn(pin_id):
        """Handle editing an existing APN."""
        apn_to_edit = APN.query.get_or_404(pin_id) # Fetch APN by PIN_id or return 404

        if request.method == 'POST':
            # Process the submitted form data
            try:
                # --- Get data from form --- 
                dpn = request.form.get('dpn', '').strip().upper()
                apn_type = request.form.get('type')
                ref_emdep = request.form.get('ref_emdep', '').strip()
                ref_ingun = request.form.get('ref_ingun', '').strip()
                ref_fenmmital = request.form.get('ref_fenmmital', '').strip()
                ref_ptr = request.form.get('ref_ptr', '').strip()
                multi_apn = request.form.get('multi_apn', '').strip()
                
                # Get location from dropdown inputs
                location_cabinet = request.form.get('location_cabinet', '').strip()
                location_drawer = request.form.get('location_drawer', '').strip()
                
                # Combine into full location if both are selected
                location = ''
                if location_cabinet and location_drawer:
                    location = f"ARMOIRE {location_cabinet}-{location_drawer}"
                
                image_file = request.files.get('image')

                # --- Validate required fields --- 
                if not dpn:
                    flash('DPN is required.', 'danger')
                    return render_template('edit_apn_form.html', apn=apn_to_edit) # Re-render form
                if not apn_type:
                    flash('Type is required.', 'danger')
                    return render_template('edit_apn_form.html', apn=apn_to_edit)

                # --- Check if DPN changed and if new DPN already exists --- 
                if dpn != apn_to_edit.DPN:
                    existing_apn = APN.query.filter(APN.DPN == dpn).first()
                    if existing_apn:
                        flash(f'An APN with DPN \'{dpn}\' already exists.', 'danger')
                        return render_template('edit_apn_form.html', apn=apn_to_edit)

                # --- Handle Image Upload (if a new image is provided) --- 
                image_web_path = apn_to_edit.Image # Keep old image by default
                if image_file and allowed_file(image_file.filename):
                    filename = secure_filename(f"{dpn}_{apn_type}_{image_file.filename}")
                    
                    # Determine save path based on type
                    if apn_type == 'PIN':
                        save_dir = current_app.config['APN_PIN_IMAGES_FOLDER']
                        image_web_path_base = 'pin'
                    else:
                        save_dir = current_app.config['APN_IMAGES_FOLDER']
                        image_web_path_base = 'apn' # Assuming a generic folder for others
                    
                    save_path = os.path.join(save_dir, filename)
                    
                    # Delete old image if it exists and is different
                    if apn_to_edit.Image and image_web_path != apn_to_edit.Image:
                        old_filename = apn_to_edit.Image.split('/')[-1]
                        old_dir = current_app.config['APN_PIN_IMAGES_FOLDER'] if '/pin/' in apn_to_edit.Image else current_app.config['APN_IMAGES_FOLDER']
                        old_path = os.path.join(old_dir, old_filename)
                        if os.path.exists(old_path):
                            try:
                                os.remove(old_path)
                                logging.info(f"Deleted old image: {old_path}")
                            except OSError as e:
                                logging.error(f"Error deleting old image {old_path}: {e}")
                                flash(f'Could not delete old image: {e}', 'warning')
                    
                    # Save new image
                    try:
                        image_file.save(save_path)
                        image_web_path = f"/{image_web_path_base}/{filename}" # Store web-accessible path
                        logging.info(f"Saved new image: {save_path}")
                    except Exception as e:
                        logging.error(f"Error saving image {save_path}: {e}")
                        flash(f'Error saving new image: {e}', 'danger')
                        # Optionally decide if you want to proceed without the image or stop
                        return render_template('edit_apn_form.html', apn=apn_to_edit)
                elif image_file: # File provided but not allowed type
                     flash('Invalid image file type. Allowed types: png, jpg, jpeg.', 'warning')
                     # Continue update without changing image? Or return? Let's return.
                     return render_template('edit_apn_form.html', apn=apn_to_edit)

                # --- Update APN object --- 
                apn_to_edit.DPN = dpn
                apn_to_edit.Type = apn_type
                apn_to_edit.Ref_Emdep = ref_emdep
                apn_to_edit.Ref_Ingun = ref_ingun
                apn_to_edit.Ref_Fenmmital = ref_fenmmital
                apn_to_edit.Ref_Ptr = ref_ptr
                apn_to_edit.Multi_APN = multi_apn
                apn_to_edit.Location = location
                apn_to_edit.Image = image_web_path # Update with new path or retain old one

                # --- Commit changes to DB --- 
                db.session.commit()
                flash(f'APN \'{apn_to_edit.DPN}\' updated successfully!', 'success')
                return redirect(url_for('apn_database')) # Redirect back to the database view
            
            except Exception as e:
                db.session.rollback() # Rollback in case of error during update
                logging.error(f"Error updating APN {pin_id}: {str(e)}")
                flash(f'An error occurred while updating the APN: {str(e)}', 'danger')
                return render_template('edit_apn_form.html', apn=apn_to_edit) # Show form again with error

        # --- GET Request: Show the edit form --- 
        return render_template('edit_apn_form.html', apn=apn_to_edit)

    # Route to Edit an existing CP
    @app.route('/edit_cp/<int:cp_id>', methods=['GET', 'POST'])
    @login_required
    def edit_cp(cp_id):
        """Handle editing an existing CP record."""
        # Fetch the CP to edit by ID
        cp_to_edit = CP.query.get_or_404(cp_id)
        
        # Fetch all customers for dropdown (same as add form)
        existing_customers = db.session.query(CP.Client_ID_1).distinct().order_by(CP.Client_ID_1).all()
        customers = [c[0] for c in existing_customers if c[0]]
        
        # For the GET request, prepare data for the form
        if request.method == 'GET':
            # Get carlines for this CP's customer to populate carline dropdown
            carlines = []
            if cp_to_edit.Client_ID_1:
                carlines_query = db.session.query(CP.PRJ_ID1)\
                    .filter(CP.Client_ID_1 == cp_to_edit.Client_ID_1)\
                    .distinct()\
                    .order_by(CP.PRJ_ID1)\
                    .all()
                carlines = [c[0] for c in carlines_query if c[0]]

            # Get APN DPNs for the form fields
            pin_data = {}
            pin_fields = ['PIN1', 'PIN2', 'PIN3', 'PIN4', 'TIGE_1', 'TIGE_2', 'RESSORT_1', 'RESSORT_2']
            
            for field in pin_fields:
                field_id = f"{field}_ID"
                pin_id = getattr(cp_to_edit, field_id)
                if pin_id:
                    # Fetch APN by PIN_id
                    apn = APN.query.get(pin_id)
                    if apn:
                        pin_data[field] = {
                            'dpn': apn.DPN,
                            'type': apn.Type
                        }
                    else:
                        pin_data[field] = {'dpn': '', 'type': ''}
                else:
                    pin_data[field] = {'dpn': '', 'type': ''}
                
                # Get quantity if applicable
                qty_field = None
                if field == 'PIN1': qty_field = 'Qte_1'
                elif field == 'PIN2': qty_field = 'Qte_2'
                elif field == 'PIN3': qty_field = 'Qte_3'
                elif field == 'PIN4': qty_field = 'QTE_4'
                elif field == 'TIGE_1': qty_field = 'Qte_Tige_1'
                elif field == 'TIGE_2': qty_field = 'Qte_Tige_2'
                
                if qty_field:
                    pin_data[field]['qty'] = getattr(cp_to_edit, qty_field) or ''
                else:
                    pin_data[field]['qty'] = ''
            
            # Build form data for the template
            form_data = {
                'customer_select': cp_to_edit.Client_ID_1 or '',
                'carline_select': cp_to_edit.PRJ_ID1 or '',
                'cp_name': cp_to_edit.CP or '',
                'ot_ref': cp_to_edit.OT_rfrence or '',
                'cp_type': 'sub51' if cp_to_edit.Image and '/CP_SUB51/' in cp_to_edit.Image else 'main',
                'pin_data': pin_data
            }
            
            return render_template('edit_cp_form.html', 
                                 cp=cp_to_edit, 
                                 customers=customers, 
                                 carlines=carlines,
                                 form_data=form_data)
        
        # Handle the POST request (form submission)
        if request.method == 'POST':
            try:
                # --- Determine Customer --- 
                client_id = request.form.get('customer_select')
                if not client_id:
                    flash('Customer is required.', 'warning')
                    return redirect(url_for('edit_cp', cp_id=cp_id))
                
                # --- Determine Carline --- 
                prj_id = request.form.get('carline_select')
                if not prj_id:
                    flash('Carline is required.', 'warning')
                    return redirect(url_for('edit_cp', cp_id=cp_id))

                # --- Other CP Data ---
                cp_name = request.form.get('cp_name')
                ot_ref = request.form.get('ot_ref')
                cp_type = request.form.get('cp_type')  # 'main' or 'sub51'
                
                # Validate required fields
                if not cp_name or not cp_type:
                    flash('CP Name and CP Type are required.', 'warning')
                    return redirect(url_for('edit_cp', cp_id=cp_id))
                
                # --- Handle Image Update if needed ---
                image_path_to_save = cp_to_edit.Image  # Default: keep existing image
                image_file = request.files.get('image')
                if image_file and image_file.filename != '':
                    if allowed_file(image_file.filename):
                        filename = secure_filename(image_file.filename)
                        
                        # Determine save directory based on type
                        if cp_type == 'sub51':
                            save_dir = current_app.config['CP_SUB51_IMAGES_FOLDER']
                            relative_path_prefix = 'CP_SUB51'
                        else:  # Default to main
                            save_dir = current_app.config['CP_IMAGES_FOLDER']
                            relative_path_prefix = 'CP'
                        
                        # If image type changed, we need to handle it differently
                        type_changed = (cp_type == 'sub51' and cp_to_edit.Image and '/CP_SUB51/' not in cp_to_edit.Image) or \
                                     (cp_type != 'sub51' and cp_to_edit.Image and '/CP_SUB51/' in cp_to_edit.Image)
                        
                        # Delete old image if it exists and we're changing it
                        if cp_to_edit.Image:
                            try:
                                old_filename = cp_to_edit.Image.split('/')[-1]
                                old_dir = current_app.config['CP_SUB51_IMAGES_FOLDER'] if '/CP_SUB51/' in cp_to_edit.Image else current_app.config['CP_IMAGES_FOLDER']
                                old_path = os.path.join(old_dir, old_filename)
                                if os.path.exists(old_path):
                                    os.remove(old_path)
                                    logging.info(f"Deleted old CP image: {old_path}")
                            except Exception as e:
                                logging.error(f"Error deleting old CP image: {str(e)}")
                                flash(f"Warning: Could not delete old image: {str(e)}", 'warning')
                        
                        # Save new image
                        os.makedirs(save_dir, exist_ok=True)
                        full_save_path = os.path.join(save_dir, filename)
                        image_file.save(full_save_path)
                        image_path_to_save = f"/{relative_path_prefix}/{filename}"
                        logging.info(f"Saved new CP image to: {full_save_path}")
                    else:
                        flash('Invalid image file type. Allowed types: png, jpg, jpeg.', 'warning')
                        return redirect(url_for('edit_cp', cp_id=cp_id))
                
                # --- Extract APNs ---
                apn_inputs = {}
                pin_fields = ['PIN1', 'PIN2', 'PIN3', 'PIN4', 'TIGE_1', 'TIGE_2', 'RESSORT_1', 'RESSORT_2']
                for field in pin_fields:
                    dpn = request.form.get(f'{field}_DPN')
                    qty = request.form.get(f'Qte_{field}')
                    # Handle potential naming mismatch for QTE_4
                    if field == 'PIN4':
                        qty = request.form.get('QTE_4')
                    apn_inputs[field] = {'dpn': dpn.strip() if dpn else None, 'qty': qty}
                
                # --- APN Lookup and Validation ---
                valid_apns = True
                field_to_qty_model_key = {
                    'PIN1': 'Qte_1',
                    'PIN2': 'Qte_2',
                    'PIN3': 'Qte_3',
                    'PIN4': 'QTE_4',  # Note the case difference
                    'TIGE_1': 'Qte_Tige_1',
                    'TIGE_2': 'Qte_Tige_2'
                    # RESSORT fields have no quantity in the model
                }
                
                for field, data in apn_inputs.items():
                    pin_id = None
                    qty_val = None
                    
                    if data['dpn']:  # If a DPN was entered for this slot
                        found_apn = APN.query.filter(func.lower(APN.DPN) == func.lower(data['dpn'])).first()
                        if not found_apn:
                            flash(f'APN with DPN \'{data["dpn"]}\' not found in database for field {field}. Please add it first.', 'danger')
                            valid_apns = False
                        else:
                            pin_id = found_apn.PIN_id
                    
                    # Get the correct quantity model key from the map
                    qty_model_key = field_to_qty_model_key.get(field)
                    
                    if pin_id is not None and qty_model_key:
                        try:
                            qty_val = int(data['qty']) if data['qty'] and data['qty'].strip() else None
                        except (ValueError, TypeError):
                            flash(f'Invalid quantity \'{data["qty"]}\' entered for {field}.', 'danger')
                            valid_apns = False
                    
                    # Set the new values on the CP object
                    setattr(cp_to_edit, f'{field}_ID', pin_id)
                    if qty_model_key:
                        setattr(cp_to_edit, qty_model_key, qty_val)
                
                if not valid_apns:
                    return redirect(url_for('edit_cp', cp_id=cp_id))
                
                # --- Update CP object ---
                cp_to_edit.Client_ID_1 = client_id
                cp_to_edit.PRJ_ID1 = prj_id
                cp_to_edit.CP = cp_name
                cp_to_edit.OT_rfrence = ot_ref
                cp_to_edit.Image = image_path_to_save
                
                # --- Commit changes to DB ---
                db.session.commit()
                flash(f'CP \'{cp_to_edit.CP}\' updated successfully!', 'success')
                return redirect(url_for('index'))
                
            except Exception as e:
                db.session.rollback()
                logging.error(f"Error updating CP {cp_id}: {str(e)}")
                logging.exception("Traceback:")
                flash(f'An error occurred while updating the CP: {str(e)}', 'danger')
                return redirect(url_for('edit_cp', cp_id=cp_id))

    @app.route('/apn_search_suggestions')
    def apn_search_suggestions():
        """Provide search suggestions for APNs and reference fields"""
        search_type = request.args.get('search_type', 'apn')
        term = request.args.get('term', '').lower()
        
        if not term or len(term) < 1:
            return jsonify([])
        
        # Different query based on search type
        if search_type == 'apn':
            # Search by DPN
            query = APN.query.filter(
                func.lower(APN.DPN).contains(func.lower(term))
            ).limit(10)
            suggestions = [{'value': apn.DPN} for apn in query.all()]
            
        elif search_type == 'emdep':
            # Search by Emdep reference
            query = APN.query.filter(
                APN.Ref_Emdep.isnot(None),
                func.lower(APN.Ref_Emdep).contains(func.lower(term))
            ).limit(10)
            suggestions = [{'value': apn.Ref_Emdep} for apn in query.all()]
            
        elif search_type == 'fenmmital':
            # Search by Fenmmital reference
            query = APN.query.filter(
                APN.Ref_Fenmmital.isnot(None),
                func.lower(APN.Ref_Fenmmital).contains(func.lower(term))
            ).limit(10)
            suggestions = [{'value': apn.Ref_Fenmmital} for apn in query.all()]
            
        elif search_type == 'ingun':
            # Search by Ingun reference
            query = APN.query.filter(
                APN.Ref_Ingun.isnot(None),
                func.lower(APN.Ref_Ingun).contains(func.lower(term))
            ).limit(10)
            suggestions = [{'value': apn.Ref_Ingun} for apn in query.all()]
            
        elif search_type == 'ptr':
            # Search by PTR reference
            query = APN.query.filter(
                APN.Ref_Ptr.isnot(None),
                func.lower(APN.Ref_Ptr).contains(func.lower(term))
            ).limit(10)
            suggestions = [{'value': apn.Ref_Ptr} for apn in query.all()]
        
        else:
            # Handle unknown search type
            suggestions = []
            
        return jsonify(suggestions)

    @app.route('/admin/users')
    @login_required
    @admin_required
    def manage_users():
        users = User.query.all()
        return render_template('admin/users.html', users=users)
    
    @app.route('/admin/users/add', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def add_user():
        if request.method == 'POST':
            username = request.form.get('username')
            employee_id = request.form.get('employee_id')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            role = request.form.get('role', 'user')
            
            # Validate input
            if not username or not password or not confirm_password:
                flash('All fields are required', 'danger')
                return redirect(url_for('add_user'))
                
            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return redirect(url_for('add_user'))
                
            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists', 'danger')
                return redirect(url_for('add_user'))
                
            if employee_id:
                existing_employee = User.query.filter_by(employee_id=employee_id).first()
                if existing_employee:
                    flash('Employee ID already exists', 'danger')
                    return redirect(url_for('add_user'))
            
            # Create new user
            new_user = User(username=username, employee_id=employee_id, role=role)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            flash(f'User {username} created successfully', 'success')
            return redirect(url_for('manage_users'))
            
        return render_template('admin/add_user.html')
        
    @app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def edit_user(user_id):
        user = User.query.get_or_404(user_id)
        
        # Prevent editing yourself through this route
        if user.id == current_user.id:
            flash('You cannot edit your own account through this interface', 'warning')
            return redirect(url_for('manage_users'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            employee_id = request.form.get('employee_id')
            role = request.form.get('role')
            new_password = request.form.get('new_password')
            
            # Check username uniqueness if changed
            if username != user.username:
                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    flash('Username already exists', 'danger')
                    return redirect(url_for('edit_user', user_id=user_id))
            
            # Check employee ID uniqueness if changed and not empty
            if employee_id and employee_id != user.employee_id:
                existing_employee = User.query.filter_by(employee_id=employee_id).first()
                if existing_employee:
                    flash('Employee ID already exists', 'danger')
                    return redirect(url_for('edit_user', user_id=user_id))
            
            # Update user
            user.username = username
            user.employee_id = employee_id
            user.role = role
            
            # Update password if provided
            if new_password:
                user.set_password(new_password)
                
            db.session.commit()
            flash(f'User {username} updated successfully', 'success')
            return redirect(url_for('manage_users'))
            
        return render_template('admin/edit_user.html', user=user)
        
    @app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
    @login_required
    @admin_required
    def delete_user(user_id):
        user = User.query.get_or_404(user_id)
        
        # Prevent deleting yourself
        if user.id == current_user.id:
            flash('You cannot delete your own account', 'danger')
            return redirect(url_for('manage_users'))
            
        # Check if this is the last admin user
        if user.is_admin():
            admin_count = User.query.filter_by(role='admin').count()
            if admin_count <= 1:
                flash('Cannot delete the last admin user', 'danger')
                return redirect(url_for('manage_users'))
        
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        flash(f'User {username} has been deleted', 'success')
        return redirect(url_for('manage_users'))

    @app.route('/locate_apn/<int:apn_id>')
    def locate_apn(apn_id):
        """Show the cabinet visualization for an APN's location"""
        apn = APN.query.get_or_404(apn_id)
        location_data = parse_location(apn.Location)
        
        if not location_data:
            flash("Location information not available for this APN.", "warning")
            return redirect(request.referrer or url_for('index'))
            
        # Get a list of all cabinets for visualization
        all_cabinets = db.session.query(
            db.func.distinct(
                db.func.substr(APN.Location, 9, 1)  # Extract cabinet letter (assuming format "ARMOIRE X-YY")
            )
        ).filter(APN.Location.isnot(None)).order_by(
            db.func.substr(APN.Location, 9, 1)
        ).all()
        
        all_cabinets = [cab[0] for cab in all_cabinets if cab[0]]
        
        return render_template(
            'locate_apn.html',
            apn=apn,
            location=location_data,
            all_cabinets=all_cabinets
        )
