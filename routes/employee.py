from flask import render_template, redirect, request, session, Blueprint
import pgsql

employee_bp = Blueprint('employee_bp', __name__)

@employee_bp.route('/', methods=['GET', 'POST'])
def employee_page():
    if session.get('user') is None:
        return redirect('/login')
    
    if session.get('user')['title'] != 'supervisor':
        return redirect('/')
    
    if request.method == 'POST':
        name          = request.form['name']
        passwd        = request.form['passwd']
        title         = request.form['title']
        supervisor_id = request.form['supervisor_id']
        
        pgsql.query(f'INSERT INTO employee (employee_name, passwd, title, supervisor_id) VALUES (%s, %s, %s, %s);', (name, passwd, title, supervisor_id))
    # get list
    result = pgsql.query('SELECT employee_id, employee_name, title FROM employee ORDER BY employee_id;')
    
    result = [ (x[0], x[1], '管理員' if x[2] == 'supervisor' else '員工') for x in result]
    
    return render_template(
        'list_page.html',
        user=session.get('user'),
        info={
            'title': '員工',
            'path': 'employee',
        },
        header=[
            ('id', 5),
            ('名字', 10),
            ('職稱', 5),
        ],
        display=result,
        create_form={
            'name': 'text',
            'passwd': 'password',
            'title': {
                'employee': '員工', 
                'supervisor': '管理員', 
            },
            'supervisor_id': { _id: name for _id, name, title in result if title == '管理員' },
        },
    )

@employee_bp.route("/<_id>", methods=['GET', 'PUT', 'DELETE'])
def employee_detail_page(_id):
    if session.get('user') is None:
        return redirect('/login')
    if session.get('user')['title'] != 'supervisor' and session.get('user')['employee_id'] != int(_id):
        return redirect('/')
    match request.method:
        case 'GET':
            # fetch detail
            with pgsql.connect() as conn:
                with conn.cursor() as cur:
                    query_string = '''SELECT emp.employee_name, emp.title, emp.supervisor_id, sup.employee_name as supervisor_name FROM employee as emp
                                        JOIN employee as sup ON emp.supervisor_id = sup.employee_id
                                        WHERE emp.employee_id = %s;'''
                    cur.execute(query_string, (_id,))
                    employee_name, title, supervisor_id, supervisor_name = cur.fetchall()[0]
                    
                    query_string = '''SELECT employee_id, employee_name FROM employee
                                        WHERE title = 'supervisor';'''
                    cur.execute(query_string)
                    supervisor_list = cur.fetchall()
            return render_template(
                'detail_page.html',
                user=session.get('user'),
                _id=_id,
                name=employee_name,
                info={
                    'title': '員工',
                    'path': 'employee',
                    'edit_button': session.get('user') != None,
                },
                data={
                    'title': {
                        'label': '職稱',
                        'value': title,
                        'options': {
                            'supervisor': '管理員',
                            'employee': '員工',
                        },
                        'editable': False
                    },
                    'supervisor': {
                        'label': '管理人',
                        'value': supervisor_id,
                        'options': { _id: name for _id, name in supervisor_list },
                        'editable': False
                    },
                },
            )
        
        case 'PUT':
            # update
            try:
                json = request.get_json()
                pgsql.query('UPDATE employee SET employee_name = %s WHERE employee_id = %s', (json["name"], _id))
                if session.get('user')['employee_id'] == int(_id):
                    session.get('user')['employee_name'] = json["name"]
            except:
                return {
                    'status': 'update_failed'
                }
            return {
                'status': 'update_success'
            }
        
        case 'DELETE':
            # delete
            try:
                pgsql.query('DELETE FROM employee WHERE employee_id = %s', (_id,))
            except:
                return {
                    'status': 'delete_failed'
                }
            if session.get('user')['employee_id'] == int(_id):
                session['user'] = None
            return {
                'status': 'delete_success'
            }