from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Clé secrète pour les sessions

# Simuler une base de données des utilisateurs et leurs rôles
users = {
    'anne.sophie': 'keirel123',          # Anne Sophie Keirel, Responsable 1
    'bernard.vanalderwelt': 'vanalderwelt123',  # Bernard Vanalderwelt, Responsable 2
    'bertrand.millet': 'millet123'       # Bertrand Millet, Responsable 3
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

# Page d'accueil pour soumettre une demande de congé
@app.route('/')
def index():
    return render_template('index.html')

# Soumettre une demande de congé
@app.route('/submit', methods=['POST'])
def submit_leave_request():
    employee_name = request.form['employee_name']
    leave_type = request.form['leave_type']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    reason = request.form['reason']

    new_request = LeaveRequest(employee_name, leave_type, start_date, end_date, reason)
    leave_requests.append(new_request)

    return redirect(url_for('leave_status'))

# Afficher les demandes de congé pour les employés
@app.route('/status')
def leave_status():
    return render_template('status.html', leave_requests=leave_requests)

# Page de connexion pour les approbateurs
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('approve_panel'))

        return "Nom d'utilisateur ou mot de passe incorrect", 401

    return render_template('login.html')

# Panneau d'approbation réservé aux responsables connectés
@app.route('/approve_panel')
def approve_panel():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    approver_role = roles[username]

    # Filtrer les demandes qui sont prêtes pour ce responsable
    requests_for_approver = [req for req in leave_requests if req.current_approval_stage == approver_role - 1]

    return render_template('approve_panel.html', leave_requests=requests_for_approver, approver_role=approver_role)


# Approbation par les responsables
@app.route('/approve/<int:request_id>/<int:approver>')
def approve_leave(request_id, approver):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    approver_role = roles[username]

    if request_id < len(leave_requests):
        leave_request = leave_requests[request_id]
        if approver == approver_role and approver == leave_request.current_approval_stage + 1:
            leave_request.current_approval_stage += 1
            leave_request.status = STATUS[leave_request.current_approval_stage]
        elif approver == 0:  # Refus
            leave_request.status = STATUS[4]

    return redirect(url_for('approve_panel'))

# Déconnexion de l'utilisateur
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
