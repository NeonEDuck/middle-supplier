from flask import render_template, redirect, request, session, Blueprint
import pgsql

order_bp = Blueprint('order_bp', __name__)

@order_bp.route('/', methods=['GET', 'POST'])
def order_page():
    if session.get('user') is None:
        return redirect('/login')
    
    firm_list = []
    item_list = []
    with pgsql.connect() as conn:
        with conn.cursor() as cur:
                
            if request.method == 'POST':
                firm_id = request.json['firm_id']
                items = request.json['items']
                
                cur.execute('INSERT INTO order_summary (firm_id, employee_id) VALUES (%s, %s) RETURNING order_id;', (firm_id, session.get('user')['employee_id']))
                result = cur.fetchone()
                order_id = result[0]
                for item in items:
                    cur.execute(
                        'INSERT INTO order_detail (order_id, item_id, price, amount) VALUES (%s, %s, %s, %s)',
                        (order_id, item['item_id'], item['price'], item['amount'])
                    )
                conn.commit()
                
                return 'success'
                
            cur.execute('''SELECT order_id, firm_name, generated_date, complete_date FROM order_summary
                        JOIN firm ON order_summary.firm_id = firm.firm_id
                        ORDER BY order_id;''')
            result = cur.fetchall()
            result = [ (x[0], x[1], x[2].strftime("%Y/%m/%d %H:%M:%S"), '完成' if x[3] else '未完成') for x in result]
            cur.execute('SELECT firm_id, firm_name FROM firm;')
            firm_list = {_id: name for _id, name in cur.fetchall() }
            cur.execute('SELECT item_id, item_name FROM item;')
            item_list = {_id: name for _id, name in cur.fetchall() }
    
    return render_template(
        'order_list_page.html',
        user=session.get('user'),
        info={
            'title': '訂單',
            'path': 'order',
        },
        header=[
            ('id', 5),
            ('廠商', 10),
            ('生成日期', 10),
            ('訂單狀態', 5),
        ],
        display=result,
        firm_list=firm_list,
        item_list=item_list,
    )

@order_bp.route("/<_id>", methods=['GET', 'PUT', 'DELETE'])
def order_detail_page(_id):
    if session.get('user') is None:
        return redirect('/login')
    match request.method:
        case 'GET':
            # fetch detail
            firm_list = []
            item_list = []
            with pgsql.connect() as conn:
                with conn.cursor() as cur:
            
                    # query_string = '''SELECT firm.firm_id, firm_name, generated_date, complete_date, employee_name, item.item_id, item_name, price, order_detail.amount AS amount FROM order_summary
                    #                     JOIN firm ON order_summary.firm_id = firm.firm_id
                    #                     JOIN employee ON order_summary.employee_id = employee.employee_id
                    #                     JOIN order_detail ON order_summary.order_id = order_detail.order_id
                    #                     JOIN item ON order_detail.item_id = item.item_id
                    #                     WHERE order_summary.order_id = %s;'''
                    cur.execute(
                        '''SELECT firm.firm_id, firm_name, generated_date, complete_date, employee_name FROM order_summary
                            JOIN firm ON order_summary.firm_id = firm.firm_id
                            JOIN employee ON order_summary.employee_id = employee.employee_id
                            WHERE order_id = %s;''', 
                        (_id,)
                    )
                    result = cur.fetchone()
                    firm_id, firm_name, generated_date, complete_date, employee_name = result
                    
                    cur.execute(
                        '''SELECT item.item_id, item_name, price, order_detail.amount FROM order_summary
                            JOIN order_detail ON order_summary.order_id = order_detail.order_id
                            JOIN item ON order_detail.item_id = item.item_id
                            WHERE order_summary.order_id = %s;''', 
                        (_id,)
                    )
                    result2 = cur.fetchall()
                    # item_name, price, amount
                    order_items = [
                        {
                            'item_id': row[0],
                            'item_name': row[1],
                            'price': row[2],
                            'amount': row[3],
                        }
                        for row in result2
                    ]
                    
                    cur.execute('SELECT firm_id, firm_name FROM firm;')
                    firm_list = {_id: name for _id, name in cur.fetchall() }
                    cur.execute('SELECT item_id, item_name FROM item;')
                    item_list = {_id: name for _id, name in cur.fetchall() }
            
            
            return render_template(
                'order_detail.html',
                user=session.get('user'),
                _id=_id,
                name='訂單',
                info={
                    'title': '訂單',
                    'path': 'order',
                    'edit_button': True,
                },
                order_items=order_items,
                firm_id=firm_id,
                firm_list=firm_list,
                item_list=item_list,
                data={
                    'firm_name': {
                        'label': '廠商',
                        'value': firm_name,
                        'editable': False
                    },
                    'generated_date': {
                        'label': '生成日期',
                        'value': generated_date.strftime("%Y/%m/%d %H:%M:%S"),
                        'editable': False
                    },
                    'complete_date': {
                        'label': '完成日期',
                        'value': complete_date.strftime("%Y/%m/%d %H:%M:%S") if complete_date else '未完成',
                        'editable': False
                    },
                    'employee': {
                        'label': '承辦人',
                        'value': employee_name,
                        'editable': False
                    },
                },
            )
        
        case 'PUT':
            # update
            json = request.get_json()
            print(json)
                
            try:
                with pgsql.connect() as conn:
                    with conn.cursor() as cur:
            
                        if json:
                            firm_id = request.json['firm_id']
                            items = request.json['items']
                            cur.execute('UPDATE order_summary SET firm_id = %s WHERE order_id = %s', (firm_id, _id))
                            cur.execute('DELETE FROM order_detail WHERE order_id = %s', (_id,))
                            
                            for item in items:
                                cur.execute(
                                    'INSERT INTO order_detail (order_id, item_id, price, amount) VALUES (%s, %s, %s, %s)',
                                    (_id, item['item_id'], item['price'], item['amount'])
                                )
                        else:
                            cur.execute('UPDATE order_summary SET complete_date = now() WHERE order_id = %s', (_id, ))
                            
                        conn.commit()
            except:
                return 'update_failed'
            return 'update_success'
        
        case 'DELETE':
            # delete
            try:
                pgsql.query('DELETE FROM order_summary WHERE order_id = %s', (_id, ))
            except:
                return 'delete_failed'
            return 'delete_success'