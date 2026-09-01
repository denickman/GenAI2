from operator import truediv

from flask import Flask, render_template, request, redirect, url_for, session
from main_flask import agent

import uuid

app = Flask(__name__)
app.secret_key = 'random_generated_string_key'



"""
session — это объект Flask, который позволяет хранить данные между запросами одного и того же пользователя
(в отличие от обычных переменных, которые живут только один запрос и умирают).

Как работает под капотом:

Flask сохраняет данные session не на сервере, а в cookie браузера пользователя — в зашифрованном/подписанном виде
При каждом новом запросе браузер отправляет эту cookie обратно, 
Flask её расшифровывает и восстанавливает session с теми же данными
Именно поэтому нужен app.secret_key — это ключ, которым 

Flask подписывает (не шифрует полностью, а именно подписывает) содержимое cookie, 
чтобы пользователь не мог сам подделать/изменить данные в своей cookie. 
Без secret_key session вообще не будет работать — выдаст ошибку.
"""


# define the root
@app.route('/')
def home():
    if 'thread_id' not in session:
        session['thread_id'] = str(uuid.uuid4())

    if 'messages' not in session:
        session['messages'] = []
        
    return render_template('chat.html', messages=session['messages'])


@app.route('/clear')
def clear():
    session.clear()
    return redirect(url_for('home'))


@app.route('/send', methods=['POST'])
def send():
    user_message = request.form['message']

    user_lat = request.form.get('latitude')
    user_lon = request.form.get('longitude')


    if user_lat and user_lon:
        session['user_location'] = {'lat': user_lat, 'lon': user_lon}

    response = agent.invoke({"messages": [{'role': 'user', 'content': user_message}]},
                            {"configurable": {"thread_id":  session['thread_id']}})


    # session['messages'] = []
    session['messages'].append({'type': 'user', 'content': user_message})
    session['messages'].append({'type': 'ai', 'content': response['messages'][-1].content})

    session.modified = True
    print(session)
    return redirect(url_for('home'))




# must be at the end of all routes
app.run(debug=True)






