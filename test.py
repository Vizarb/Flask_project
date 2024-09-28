@app.route('/customers', methods=['GET'])
def get_customers():
    """Retrieve customers based on specified status: active, deactivated, or all."""
    status = request.args.get('status', default='active', type=str)
    customers = get_records(Customers, status)
    return jsonify([customer.to_dict() for customer in customers]), 200

@app.route('/loans', methods=['GET'])
def get_loans():
    """Retrieve loans based on specified status: active, deactivated, or all."""
    status = request.args.get('status', default='active', type=str)
    loans = get_records(loans, status)
    return jsonify([loans.to_dict() for loans in loans]), 200












@app.route('/loans', methods=['GET'])
def get_loans():
    """Retrieve loans based on specified status: active, deactivated, late, or all."""
    status = request.args.get('status', default='active', type=str)

    if status not in ['active', 'deactivated', 'late', 'all']:
        log_message('WARNING', "Invalid status parameter provided for loans.")
        abort(400, description="Invalid status parameter. Use 'active', 'deactivated', 'late', or 'all'.")

    if status == 'late':
        current_time = datetime.utcnow()
        loans = Loans.query.filter(Loans.return_date < current_time, Loans.is_active == True).all()  # Query for late loans
    elif status == 'all':
        loans = Loans.query.all()  # Retrieve all loans
    else:
        is_active = status == 'active'
        loans = Loans.query.filter_by(is_active=is_active).all()  # Filter based on active status

    log_message('INFO', f"Retrieved all {'late' if status == 'late' else status} loans.")
    return jsonify([loan.to_dict() for loan in loans]), 200
