"""
=============================================================
  Shipment Controller
=============================================================
  Handles two routes:
    GET  /create-shipment  → render the empty form
    POST /create-shipment  → validate inputs, save to DB,
                             redirect to history on success
=============================================================
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.OrderModel import Order

# Register as a Blueprint so it plugs into the main app
# the same way auth routes do.
shipment = Blueprint('shipment', __name__)


# ── Delivery fees lookup ──────────────────────────────────────
DELIVERY_FEES = {
    'standard':  150,
    'express':   350,
    'overnight': 500,
}

# ── Fields that must never be blank ──────────────────────────
REQUIRED_FIELDS = [
    ('sender_name',       'Sender full name'),
    ('sender_phone',      'Sender phone number'),
    ('sender_address',    'Sender pickup address'),
    ('sender_city',       'Sender city'),
    ('sender_district',   'Sender district'),
    ('receiver_name',     'Receiver full name'),
    ('receiver_phone',    'Receiver phone number'),
    ('receiver_address',  'Receiver delivery address'),
    ('receiver_city',     'Receiver city'),
    ('receiver_district', 'Receiver district'),
    ('package_type',      'Package type'),
    ('weight',            'Package weight'),
    ('length',            'Package length'),
    ('width',             'Package width'),
    ('height',            'Package height'),
]


@shipment.route('/create-shipment', methods=['GET', 'POST'])
def create_shipment():
    # ── GET: just show the form ───────────────────────────────
    if request.method == 'GET':
        return render_template('create-shipment.html')

    # ── POST: validate then save ──────────────────────────────
    form = request.form

    # 1. Check every required field is non-empty
    errors = []
    for field_name, label in REQUIRED_FIELDS:
        value = form.get(field_name, '').strip()
        if not value:
            errors.append(f'{label} is required.')

    # 2. Numeric fields must be positive numbers
    numeric_fields = [
        ('weight',          'Weight'),
        ('estimated_value', 'Estimated value'),
        ('length',          'Length'),
        ('width',           'Width'),
        ('height',          'Height'),
    ]
    for field_name, label in numeric_fields:
        raw = form.get(field_name, '').strip()
        if raw:  # only validate if provided (weight already caught above if empty)
            try:
                val = float(raw)
                if val < 0:
                    errors.append(f'{label} cannot be negative.')
            except ValueError:
                errors.append(f'{label} must be a valid number.')

    # 3. Return to form with error messages if validation failed
    if errors:
        # flash each error so the template can display them
        for err in errors:
            flash(err, 'error')
        # Pass form data back so user doesn't retype everything
        return render_template('create-shipment.html', form_data=form), 422

    # 4. Build the Order object from validated form data
    delivery_option = form.get('delivery', 'standard')
    fee = DELIVERY_FEES.get(delivery_option, 150)

    order = Order(
        # Attach to the logged-in customer if session exists
        customer_id=session.get('user_id'),

        sender_name=form.get('sender_name', '').strip(),
        sender_phone=form.get('sender_phone', '').strip(),
        sender_address=form.get('sender_address', '').strip(),
        sender_city=form.get('sender_city', '').strip(),
        sender_district=form.get('sender_district', '').strip(),

        receiver_name=form.get('receiver_name', '').strip(),
        receiver_phone=form.get('receiver_phone', '').strip(),
        receiver_address=form.get('receiver_address', '').strip(),
        receiver_city=form.get('receiver_city', '').strip(),
        receiver_district=form.get('receiver_district', '').strip(),

        package_type=form.get('package_type', '').strip(),
        weight=float(form.get('weight', 0) or 0),
        estimated_value=float(form.get('estimated_value', 0) or 0),
        length=float(form.get('length', 0) or 0),
        width=float(form.get('width', 0) or 0),
        height=float(form.get('height', 0) or 0),
        special_instructions=form.get('special_instructions', '').strip(),

        delivery_option=delivery_option,
        payment_method=form.get('payment', 'cod'),
        delivery_fee=fee,

        status='pending',
    )

    # 5. Save to database — save() returns the tracking number
    try:
        tracking_number = order.save()
    except Exception as e:
        flash(f'Database error: {str(e)}', 'error')
        return render_template('create-shipment.html', form_data=form), 500

    # 6. Success → redirect to history page (or confirmation)
    flash(f'Shipment created! Tracking number: {tracking_number}', 'success')
    return redirect(url_for('dashboard'))


@shipment.route('/shipment-history')
def shipment_history():
    """
    Show all orders for the logged-in customer.
    Replace the render_template call with your actual history template.
    """
    customer_id = session.get('user_id')
    orders = []

    if customer_id:
        order_model = Order()
        orders = order_model.find_by_customer(customer_id)

    return render_template('shipment-history.html', orders=orders)
