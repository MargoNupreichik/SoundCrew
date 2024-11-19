from flask import Flask, render_template, request
from users import users
import templates.phrases as ph
app = Flask(__name__, template_folder='templates')


@app.route('/')
@app.route('/auth')
def auth():
    return render_template('/params_forms/auth/auth.html')


@app.route('/login', methods=['post'])
def workspace():
    login = request.form.get('log')
    password = request.form.get('passw')
    
    try:
        correct = (password == users[login])
        
        if correct:
            literal = 'a'
            phrases = ph.admins  
            if login=='manager':
                literal = 'm'
                phrases = ph.managers  
            
            return render_template('user_workspace.html', error=False, phrases=phrases, liter=literal)
        else:
            raise ValueError
        
    except ValueError:
        return render_template('/params_forms/auth/auth_error.html',error=True)


@app.route('/m_<int:index>', methods=['get'])
def ask_info(index):
    phrase, param_name = get_phrase_and_param_m(index)
    return render_template(f'/params_forms/manager/{param_name}.html', phrase=phrase)


@app.route('/m_<int:index>', methods=['post'])
def ask_info2(index):
    
    phrase, param_name = get_phrase_and_param_m(index)
    
    param = ''
    request_dict = request.form
    if 'group' in request_dict:
        param = request_dict['group']
    elif 'song' in request_dict:
        param = request_dict['song']
    
    return render_template("transaction_output.html", param=param, phrase=phrase, param_type=param_name)


@app.route('/a_<int:index>', methods=['get'])
def insert_info(index):
    phrase, param_name = get_phrase_and_param_a(index)
    return render_template(f'/insert_forms/admin/{param_name}.html', phrase=phrase)


@app.route('/a_<int:index>', methods=['post'])
def insert_info2(index):
    
    phrase, param_name = get_phrase_and_param_a(index)
    
    # Чтение данных о группе с формы
    group_name = request.form.get("group")
    founded_in = request.form.get("f_date")
    group_country = request.form.get("country")
    
    # Чтение значений из таблицы с музыкантами
    fio_list = request.form.getlist('fio[]')
    age_list = request.form.getlist('age[]')
    position_list = request.form.getlist('position[]')

    # Чтение значений из таблицы с песнями
    title_list = request.form.getlist('title[]')
    create_date_list = request.form.getlist('create_date[]')
    composer_list = request.form.getlist('composer[]')
    textwriter_list = request.form.getlist('textwriter[]')
    
    return render_template("transaction_output.html", param=group_name, phrase=phrase, param_type=param_name)

@app.route('/p_<int:index>')
def print_info(index):
    phrase = get_phrase_p(index)
    return render_template("transaction_result.html", phrase=phrase, param_res=1)

# Вспомогательные функции (часть менеджера)
def get_phrase_and_param_m(index):
    phrase = ph.managers[index]
    param = 'group'
    if index == 2:
        param = 'song'
    return phrase, param

def get_phrase_and_param_a(index):
    phrase = ph.admins[index]
    param = 'insert_group'
    if index == 1:
        param = 'hit_parade'
    if index == 2:
        param = 'delete_group'
    return phrase, param

def get_phrase_p(index):
    return ph.prints[index]

if __name__ == '__main__':
    app.run(debug=True)