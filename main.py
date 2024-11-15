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
    phrase, param_name = get_phrase_and_param(index)
    return render_template(f'/params_forms/manager/{param_name}.html', phrase=phrase)


@app.route('/m_<int:index>', methods=['post'])
def ask_info2(index):
    
    phrase, param_name = get_phrase_and_param(index)
    
    param = ''
    request_dict = request.form
    if 'group' in request_dict:
        param = request_dict['group']
    elif 'song' in request_dict:
        param = request_dict['song']
    
    return render_template("output.html", param=param, phrase=phrase, param_type=param_name)


# Вспомогательные функции (часть менеджера)
def get_phrase_and_param(index):
    phrase = ph.managers[index]
    param = 'group'
    if index == 2:
        param = 'song'
    return phrase, param

if __name__ == '__main__':
    app.run(debug=True)