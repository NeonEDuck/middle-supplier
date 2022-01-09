from flask import render_template, redirect, request, session, Blueprint
import pgsql 

firm_bp = Blueprint('firm_bp', __name__)

@firm_bp.route('/', methods=['GET', 'POST'])
def firm_page():
    if session.get('user') is None:
        return redirect('/login')
    if request.method == 'POST':
        firm_name   = request.form['firm_name']
        tel         = request.form['tel']
        is_supplier = request.form['is_supplier']
        
        pgsql.query(f'INSERT INTO firm (firm_name, tel, is_supplier, employee_id) VALUES (%s, %s, %s, %s);', (firm_name, tel, is_supplier, session.get('user')['employee_id']))
    
    # get item list
    result = pgsql.query('SELECT firm_id, firm_name, is_supplier FROM firm ORDER BY firm_id;')
    
    result = [ (x[0], x[1], '供應商' if x[2] else '出貨商') for x in result]
    
    return render_template(
        'list_page.html',
        user=session.get('user'),
        info={
            'title': '廠商',
            'path': 'firm',
        },
        header=[
            ('id', 5),
            ('名稱', 10),
            ('是否供應商', 5),
        ],
        display=result,
        create_form={
            'firm_name': 'text',
            'tel': 'text',
            'is_supplier': 'checkbox',
        },
    )

@firm_bp.route("/<_id>", methods=['GET', 'PUT', 'DELETE'])
def firm_detail_page(_id):
    if session.get('user') is None:
        return redirect('/login')
    match request.method:
        case 'GET':
            # fetch item detail
            query_string = '''SELECT firm_name, tel, is_supplier, employee_name FROM firm
                                JOIN employee ON firm.employee_id = employee.employee_id
                                WHERE firm_id = %s;'''
            result = pgsql.query(query_string, (_id,))
            firm_name, tel, is_supplier, employee_name = result[0]

            return render_template(
                'detail_page.html',
                user=session.get('user'),
                _id=_id,
                name=firm_name,
                info={
                    'title': '廠商',
                    'path': 'firm',
                    'edit_button': True,
                },
                data={
                    'tel': {
                        'label': '電話',
                        'value': tel
                    },
                    'is_supplier': {
                        'label': '是否為供應商',
                        'value': is_supplier
                    },
                    'employee': {
                        'label': '承辦人',
                        'value': employee_name,
                        'editable': False
                    },
                },
            )
        
        case 'PUT':
            # update item
            json = request.get_json()
            try:
                pgsql.query('UPDATE firm SET firm_name = %s, tel = %s, is_supplier = %s WHERE firm_id = %s', (json["name"], json["tel"], json["is_supplier"], _id))
            except:
                return {
                    'status': 'update_failed'
                }
            return {
                'status': 'update_success'
            }

        
        case 'DELETE':
            # delete item
            try:
                pgsql.query('DELETE FROM firm WHERE firm_id = %s', (_id,))
            except:
                return {
                    'status': 'delete_failed'
                }
            return {
                'status': 'delete_success'
            }