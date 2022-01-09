from flask import render_template, redirect, request, session, Blueprint
import pgsql 

item_bp = Blueprint('item_bp', __name__)

@item_bp.route('/', methods=['GET', 'POST'])
def item_page():
    if session.get('user') is None:
        return redirect('/login')
    if request.method == 'POST':
        name      = request.form['name']
        amount    = request.form['amount']
        ref_price = request.form['ref_price']
        
        pgsql.query(f'INSERT INTO item (item_name, amount, ref_price, employee_id) VALUES (%s, %s, %s, %s);', (name, amount, ref_price, session.get('user')['employee_id']))
    
    # get item list
    result = pgsql.query('SELECT item_id, item_name FROM item ORDER BY item_id;')
    
    return render_template(
        'list_page.html',
        user=session.get('user'),
        info={
            'title': '商品',
            'path': 'item',
        },
        header=[
            ('id', 5),
            ('名稱', 10)
        ],
        display=result,
        create_form={
            'name': 'text',
            'amount': 'number',
            'ref_price': 'number',
        },
    )

@item_bp.route("/<_id>", methods=['GET', 'PUT', 'DELETE'])
def item_detail_page(_id):
    if session.get('user') is None:
        return redirect('/login')
    match request.method:
        case 'GET':
            # fetch item detail
            query_string = '''SELECT item_name, amount, ref_price, employee_name FROM item
                                JOIN employee ON item.employee_id = employee.employee_id
                                WHERE item_id = %s;'''
            result = pgsql.query(query_string, (_id,))
            if not result:
                return redirect('/item')
            item_name, amount, ref_price, employee_name = result[0]
            
            return render_template(
                'detail_page.html',
                user=session.get('user'),
                _id=_id,
                name=item_name,
                info={
                    'title': '商品',
                    'path': 'item',
                    'edit_button': True,
                },
                data={
                    'amount': {
                        'label': '數量',
                        'value': amount
                    },
                    'ref_price': {
                        'label': '定價',
                        'value': ref_price
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
                pgsql.query('UPDATE item SET item_name = %s, amount = %s, ref_price = %s WHERE item_id = %s', (json["name"], json["amount"], json["ref_price"], _id))
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
                pgsql.query('DELETE FROM item WHERE item_id = %s', (_id,))
            except Exception as e:
                return {
                    'status': 'delete_failed'
                }
            return {
                'status': 'delete_success'
            }