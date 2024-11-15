from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'

# Correction des dictionnaires de simulation des utilisateurs et des rôles
users = {
    'anne.sophie': 'ClsRbx59',
    'bernard.vanalderwelt': 'ClsRbx59',
    'bertrand.millet': 'ClsRbx59',
    'bbouzakri': 'ClsRbx59'
}

roles = {
    'anne.sophie': 1,
    'bernard.vanalderwelt': 2,
    'bertrand.millet': 3,
    'bbouzakri': 1
}

# Simulation de base de données pour les demandes de congé
leave_requests = []

# Statuts d'approbation
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

# Route d'inscription pour les nouveaux utilisateurs
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = int(request.form.get('role', 0))

        # Vérifie si le nom d'utilisateur existe déjà
        if username in users:
            flash("Nom d'utilisateur déjà utilisé.", "error")
            return redirect(url_for('register'))

        # Enregistre le nouvel utilisateur
        users[username] = password
        roles[username] = role

        flash("Compte créé avec succès ! Veuillez vous connecter.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# Page d'accueil pour soumettre une demande de congé
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# Soumettre une demande de congé
@app.route('/submit', methods=['POST'])
def submit_leave_request():
    if 'username' not in session:
        return redirect(url_for('login'))

    employee_name = session['username']
    leave_type = request.form['leave_type']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    reason = request.form['reason']

    new_request = LeaveRequest(employee_name, leave_type, start_date, end_date, reason)
    leave_requests.append(new_request)

    flash("Demande de congé soumise avec succès.", "success")
    return redirect(url_for('leave_status'))

# Afficher les demandes de congé pour l'utilisateur connecté
@app.route('/status')
def leave_status():
    if 'username' not in session:
        return redirect(url_for('login'))

    employee_name = session['username']
    user_leave_requests = [req for req in leave_requests if req.employee_name == employee_name]
    return render_template('status.html', leave_requests=user_leave_requests)

# Page de connexion pour les utilisateurs
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['username'] = username
            flash("Connexion réussie.", "success")
            return redirect(url_for('index'))
        
        flash("Nom d'utilisateur ou mot de passe incorrect.", "error")
    return render_template('login.html')

# Panneau d'approbation réservé aux responsables
@app.route('/approve_panel')
def approve_panel():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    approver_role = roles.get(username)
    if approver_role is None:
        return "Accès interdit", 403

    requests_for_approver = [req for req in leave_requests if req.current_approval_stage == approver_role - 1]
    return render_template('approve_panel.html', leave_requests=requests_for_approver, approver_role=approver_role)

# Approbation ou refus des congés
@app.route('/approve/<int:request_id>/<int:approver>')
def approve_leave(request_id, approver):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    approver_role = roles.get(username)
    if approver_role is None:
        return "Accès interdit", 403

    if request_id < len(leave_requests):
        leave_request = leave_requests[request_id]
        if approver == approver_role and approver == leave_request.current_approval_stage + 1:
            leave_request.current_approval_stage += 1
            leave_request.status = STATUS[leave_request.current_approval_stage]
        elif approver == 0:
            leave_request.status = STATUS[4]

    return redirect(url_for('approve_panel'))

# Déconnexion de l'utilisateur
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Déconnexion réussie.", "success")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True)
