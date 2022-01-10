from flask import render_template, redirect, request, session, Blueprint
import pgsql

view_bp = Blueprint('view_bp', __name__)


@view_bp.get("/")
def home_page():
    print(session.get('user', 'not set'))
    return render_template(
        'index.html',
        user=session.get('user')
    )

@view_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        employee_id = request.json['employee_id']
        passwd      = request.json['passwd']
        
        
        with pgsql.connect() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT employee_id, employee_name, title FROM employee WHERE employee_id = %s AND passwd = %s;', (employee_id, passwd))
                result = cur.fetchone()

        if result:
            session['user'] = {
                'employee_id': result[0],
                'employee_name': result[1],
                'title': result[2]
            }
            
            return 'success'
        else:
            return '登入失敗'
    
    return render_template(
        'login.html',
        user=session.get('user'),
    )

@view_bp.route('/logout', methods=['GET', 'POST'])
def logout_page():
    session['user'] = None
    
    return redirect('/')