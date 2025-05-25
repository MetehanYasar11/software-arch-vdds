from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from detection import analyze_image
from feedback import record_feedback, init_feedback_log

app = Flask(__name__, static_folder='../static', template_folder='../templates')
app.secret_key = 'gizli-key'

USERS = {
    'qofficer': {'pwd': '1234', 'role': 'officer'},
    'qmanager': {'pwd': '1234', 'role': 'manager'}
}

UPLOAD_FOLDER = 'static/uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd  = request.form['password']
        if user in USERS and USERS[user]['pwd'] == pwd:
            session['user'] = user
            session['role'] = USERS[user]['role']
            return redirect(url_for('officer_dashboard') if session['role']=='officer' else url_for('manager_dashboard'))
        flash('Kullanıcı adı veya şifre hatalı', 'danger')
    return render_template('login.html')

@app.route('/officer', methods=['GET','POST'])
def officer_dashboard():
    if session.get('role')!='officer':
        return redirect(url_for('login'))
    if request.method=='POST':
        file = request.files['image']
        if not file:
            flash('Lütfen bir dosya seçin', 'warning')
            return redirect(request.url)
        fname = file.filename
        path = os.path.join(UPLOAD_FOLDER, fname)
        file.save(path)
        marked = analyze_image(path)
        return render_template('result.html', original=f'/{path}', processed=f'/{marked}')
    return render_template('officer.html')

@app.route('/feedback', methods=['GET','POST'])
def feedback():
    if session.get('role')!='officer':
        return redirect(url_for('login'))

    if request.method == 'GET':
        img = request.args.get('img')
        if not img:
            flash('Geri bildirim için önce bir analiz yapın.', 'warning')
            return redirect(url_for('officer_dashboard'))
        return render_template('feedback.html', img=img)

    # POST
    init_feedback_log()
    img     = request.form['img']
    fb_type = request.form['fb_type']
    note    = request.form.get('note','')
    record_feedback(os.path.basename(img), fb_type, note)
    flash('Geri bildiriminiz kaydedildi', 'success')
    return redirect(url_for('officer_dashboard'))

@app.route('/manager')
def manager_dashboard():
    if session.get('role') != 'manager':
        return redirect(url_for('login'))

    import pandas as pd
    import os

    csv_path = 'data/feedback_log.csv'
    if os.path.exists(csv_path):
        log = pd.read_csv(csv_path)
        # Eğer başlık satırı yoksa, sütun isimleri otomatik atanmış -> ilk satırı başlık olarak al
        if 'type' not in log.columns and len(log.columns) >= 3:
            # Varolan sütun sayısına göre isimlendirme
            names = ['timestamp', 'image', 'type', 'note'][:len(log.columns)]
            log.columns = names
            # Eski başlık satırını da veri olarak geri eklemek isterseniz aşağıdakini kullanabilirsiniz:
            # header_row = pd.read_csv(csv_path, nrows=1, header=None).iloc[0]
            # log = pd.concat([header_row.to_frame().T, log], ignore_index=True)
    else:
        log = pd.DataFrame(columns=['type'])

    total = len(log)
    if 'type' in log.columns:
        fp = int((log['type'] == 'false_positive').sum())
        md = int((log['type'] == 'missed_defect').sum())
    else:
        fp = 0
        md = 0

    return render_template('manager.html', total=total, fp=fp, md=md)



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_feedback_log()
    app.run(debug=True)
