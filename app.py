from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'

# Simuler une base de données pour les utilisateurs, leurs mots de passe et rôles
users = {
    'anne.sophie': 'ClsRbx59',
    'bernard.vanalderwelt': 'ClsRbx59',
    'bertrand.millet': 'ClsRbx59',
    'bbouzakri': 'ClsRbx59'
}

roles = {
    'anne.sophie': 1,
    'bernard.vanalderwelt': 2,
    'bertrand.millet': 3
}

# Simuler une base de données pour les demandes de congé
leave_requests = []

# Statut des approbations
STATUS = ["En attente", "Approuvé par Anne-Sophie", "Approuvé par Bernard", "Approuvé par Bertrand", "Refusé"]


class LeaveRequest:
    def __init__(self, employee_name, leave_type, start_date, end_date, reason):
        self.employee_name = employee_name
        self.leave_type = leave_type
        self.start_date = start_date
        self.end_date = end_date
        self.reason = reason
        self.status = STATUS[0]
        self.current_approval_stage = 0


@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['username'] = username
            flash('Connexion réussie.', 'success')
            return redirect(url_for('index'))
        flash('Nom d\'utilisateur ou mot de passe incorrect.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Vous êtes déconnecté.', 'info')
    return redirect(url_for('login'))


@app.route('/submit', methods=['GET', 'POST'])
def submit_leave_request():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        leave_type = request.form['leave_type']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        reason = request.form['reason']

        if not all([leave_type, start_date, end_date, reason]):
            flash('Tous les champs sont obligatoires.', 'warning')
            return redirect(url_for('submit_leave_request'))

        employee_name = session['username']
        new_request = LeaveRequest(employee_name, leave_type, start_date, end_date, reason)
        leave_requests.append(new_request)

        flash('Demande de congé soumise avec succès.', 'success')
        return redirect(url_for('leave_status'))

    return render_template('submit.html')


@app.route('/status')
def leave_status():
    if 'username' not in session:
        return redirect(url_for('login'))

    employee_name = session['username']
    user_leave_requests = [req for req in leave_requests if req.employee_name == employee_name]
    return render_template('status.html', leave_requests=user_leave_requests)


@app.route('/approve_panel')
def approve_panel():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    approver_role = roles.get(username)
    if approver_role is None:
        flash('Accès interdit.', 'danger')
        return redirect(url_for('index'))

    requests_for_approver = [req for req in leave_requests if req.current_approval_stage == approver_role - 1]
    return render_template('approve_panel.html', leave_requests=requests_for_approver, approver_role=approver_role)


@app.route('/approve/<int:request_id>/<int:decision>')
def approve_leave(request_id, decision):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    approver_role = roles.get(username)
    if approver_role is None or request_id >= len(leave_requests):
        flash('Action interdite.', 'danger')
        return redirect(url_for('approve_panel'))

    leave_request = leave_requests[request_id]
    if decision == 1 and approver_role == leave_request.current_approval_stage + 1:
        leave_request.current_approval_stage += 1
        leave_request.status = STATUS[leave_request.current_approval_stage]
        flash('Demande approuvée.', 'success')
    elif decision == 0:
        leave_request.status = STATUS[4]
        flash('Demande refusée.', 'danger')

    return redirect(url_for('approve_panel'))


if __name__ == '__main__':
    app.run(debug=True)
