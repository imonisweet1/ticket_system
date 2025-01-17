from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from .models import db, Event, Ticket
import qrcode
from io import BytesIO
import base64

main = Blueprint('main', __name__)

@main.route('/')
def index():
    events = Event.query.all()
    return render_template('index.html', events=events)

@main.route('/purchase', methods=['POST'])
def purchase_ticket():
    name = request.form['name']
    event_id = request.form['event']
    quantity = request.form['quantity']

    if not name or not event_id or not quantity:
        flash('All fields are required!', 'error')
        return redirect(url_for('main.index'))

    qr = qrcode.QRCode()
    qr_data = f"Name: {name}, Event ID: {event_id}, Quantity: {quantity}"
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    ticket = Ticket(name=name, event_id=event_id, quantity=quantity, qr_code=qr_code_base64)
    db.session.add(ticket)
    db.session.commit()

    return render_template('ticket.html', ticket=ticket)

@main.route('/validate', methods=['POST'])
def validate_ticket():
    qr_data = request.json.get('qr_data')
    ticket = Ticket.query.filter_by(qr_code=qr_data).first()
    if ticket:
        return jsonify({"status": "valid", "name": ticket.name, "event_id": ticket.event_id})
    return jsonify({"status": "invalid"})

@main.route('/admin')
def admin():
    events = Event.query.all()
    return render_template('admin.html', events=events)

@main.route('/admin/add_event', methods=['POST'])
def add_event():
    name = request.form['name']
    if name:
        event = Event(name=name)
        db.session.add(event)
        db.session.commit()
        flash('Event added successfully!', 'success')
    else:
        flash('Event name is required!', 'error')
    return redirect(url_for('main.admin'))
