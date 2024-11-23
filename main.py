from flask import Flask, render_template, request
from users import users
import templates.phrases as ph
import database_work as dw
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
    param_type = 'group'
    request_dict = request.form
    if 'group' in request_dict:
        param = request_dict['group']
    elif 'song' in request_dict:
        param_type = 'song'
        param = request_dict['song']
    
    output_type = 'line'
    columns = []
    if index == 0:
        result = dw.Manager.get_group_info(group_name=param)
    elif index == 1:
        result = dw.Manager.most_popular_band_repertoire()
        output_type = 'table'
        param = result.pop(0)
        columns = ['Название песни']
    elif index == 2:
        result = dw.Manager.get_song_info(song=param)
    elif index == 3:
        result = dw.Manager.get_tour_info(band=param)
    elif index == 4:
        result = dw.Manager.get_ticket_price(band=param)
    elif index == 5:
        result = dw.Manager.get_members_info(band=param)
        output_type = 'table'
        columns = ['ФИО', 'Возраст', 'Роль']
    print(result)
    return render_template("transaction_output.html", param=param, phrase=phrase, 
                           result=result, output_type=output_type, columns=columns, param_type=param_type)

@app.route('/a_<int:index>', methods=['get'])
def insert_info(index):
    phrase, param_name = get_phrase_and_param_a(index)
    return render_template(f'/insert_forms/admin/{param_name}.html', phrase=phrase)

@app.route('/a_<int:index>', methods=['post'])
def insert_info2(index):
    
    phrase, param_name = get_phrase_and_param_a(index)
    
    # Добавление новой группы
    if index == 0:
        # Чтение данных о группе с формы
        group_name = request.form.get("group")
        founded_in = request.form.get("f_date")
        group_country = request.form.get("country")
    
        # Чтение значений из таблицы с музыкантами
        fio_list = request.form.getlist('fio[]')
        age_list = request.form.getlist('age[]')
        position_list = request.form.getlist('position[]')
        members_list = [(fio_list[i], age_list[i], position_list[i]) for i in range(0, len(fio_list))]

        # Чтение значений из таблицы с песнями
        title_list = request.form.getlist('title[]')
        create_date_list = request.form.getlist('create_date[]')
        composer_list = request.form.getlist('composer[]')
        textwriter_list = request.form.getlist('textwriter[]')
        songs_list = [(title_list[i], create_date_list[i], composer_list[i], textwriter_list[i]) for i in range(0, len(title_list))]
    
        result = dw.Admin.insert_new_group(group_name=group_name, foundation_date=founded_in, country=group_country,
                                         members_list=members_list, songs_list=songs_list)
    # Изменение положения группы в хит-параде
    elif index == 1:
        group_name = request.form.get("group")
        new_position = request.form.get("hit_i")
        result = dw.Admin.change_group_position_hit_parade(group_name=group_name, new_position=new_position)
    # Удаление всей информации о группе
    elif index == 2:
        group_name = request.form.get("group")
        result = dw.Admin.delete_group(group_name=group_name)
    
    return render_template("transaction_result.html", param=result, phrase=phrase)

@app.route('/p_<int:index>')
def print_info(index):
    phrase = get_phrase_p(index)
    output_type = 'table'
    if index == 0:
        result = dw.HelpInformation.best_hit_parade_groups()
        columns = ['Название группы', 'Положение в хит-параде']
    elif index == 1:
        result = dw.HelpInformation.tour_report()
        columns = ['Название группы', 'Название тура', 'Дата начала', 'Дата окончания', 'Цена билета']
    return render_template("transaction_output.html", param='', phrase=phrase, result=result, output_type=output_type, columns=columns)

# Вспомогательные функции (часть менеджера)
def get_phrase_and_param_m(index):
    phrase = ph.managers[index]
    param = 'group'
    if index == 2:
        param = 'song'
    if index == 1:
        param = 'skip'
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