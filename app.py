from flask import Flask, render_template, request, session, g
from pyrebase import pyrebase
from datetime import date, datetime, timedelta

app = Flask(__name__)
app.secret_key = 'invsyssecretkey'

firebaseConfig = {
    "apiKey": "AIzaSyDidtYwD7DGqwO_dQCuxyujIliyLW9msPw",
    "authDomain": "marosan-shilan-inv.firebaseapp.com",
    "databaseURL": "https://marosan-shilan-inv-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "marosan-shilan-inv",
    "storageBucket": "marosan-shilan-inv.appspot.com",
    "messagingSenderId": "457271647492",
    "appId": "1:457271647492:web:d5bfac3baa03b34ae28451",
    "measurementId": "G-F2P1SX8P2Q"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
fbdb = firebase.database()

'''
@app.route("/")
def main():
    #test = fbdb.child("InvChart").child("2021-10-08").get()
    #print(test.val())
    #for row in test:
    #    print(row.val())

    ######################################### get value
    #test = fbdb.child("InvCurrent").child("2").get()
    #print(test.val()['name'])
    ######################################### end get value

    ######################################### get key
    #test = fbdb.child("InvCurrent").child().get()
    #for row in test:
    #  print(row.key())
    ######################################### end get key

    ######################################### date
    sdate = date(2021, 10, 1)   # start date
    edate = date(2021, 10, 24)   # end date

    delta = edate - sdate       # as timedelta

    for i in range(delta.days + 1):
        day = sdate + timedelta(days=i)
        test = fbdb.child("InvChart").child(str(day).strip()).get()
        print(day, test.val())
    ######################################### end date

    return render_template('index.html')
'''


@app.before_request
def before_request():
    g.lgin = False
    g.lgot = False
    if 'user_id' in session:
        g.lgot = True
    else:
        g.lgin = True


@app.route("/")
def main():
    if 'user_id' in session:
        return render_template('dashboard.html')
    else:
        return render_template('login.html')


@app.route("/login")
def login():
    return render_template('login.html')


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return render_template('logout.html')


@app.route('/dashboard', methods=["POST", "GET"])
def dashboard():
    if (request.method == 'POST'):
        email = request.form['email']
        password = request.form['password']
        try:
            auth.sign_in_with_email_and_password(email, password)
            session["user_id"] = email
            return render_template('dashboard.html')
        except:
            unsuccessful = 'Please check your credentials'
            return render_template('login.html', umessage=unsuccessful)
    return render_template('login.html')


@app.route("/reports")
def reports():
    if 'user_id' in session:

        # get date
        last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
        start_day_of_prev_month = date.today().replace(
            day=1) - timedelta(days=last_day_of_prev_month.day)

        # date
        styy = start_day_of_prev_month.strftime('%Y')
        stmm = start_day_of_prev_month.strftime('%m')
        stdd = start_day_of_prev_month.strftime('%d')
        spyy = datetime.strftime(datetime.now(), '%Y')
        spmm = datetime.strftime(datetime.now(), '%m')
        spdd = datetime.strftime(datetime.now(), '%d')

        # start date
        sdate = date(int(styy), int(stmm), int(stdd))
        # end date
        edate = date(int(spyy), int(spmm), int(spdd))

        # as timedelta
        delta = edate - sdate

        array_dt = []

        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)
            array_dt.append(day.strftime('%Y-%m-%d'))

        def_day = datetime.strftime(datetime.now(), '%Y-%m-%d')

        return render_template('reportmain.html', array_dt=array_dt[::-1], def_day=def_day)
    else:
        return render_template('login.html')


@app.route("/getchart", methods=['POST', 'GET'])
def getchart():
    if request.method == 'POST':

        # Get data from html
        site = request.form['site']
        date = request.form['date']
        yy = datetime.strftime(datetime.strptime(date, "%Y-%m-%d"), '%Y')
        mm = datetime.strftime(datetime.strptime(date, "%Y-%m-%d"), '%m')
        dd = datetime.strftime(datetime.strptime(date, "%Y-%m-%d"), '%d')

        # get summary
        summary = fbdb.child("inv_summary_shilan").child(
            str(yy).strip()+"_"+str(mm).strip()+"/"+str(dd).strip()).get().val()

        # get details
        details = fbdb.child("inv_details_shilan").child(
            str(yy).strip()+"_"+str(mm).strip()+"/"+str(dd).strip()).get().val()

        # get fast moving
        fast = fbdb.child("fastmoving_shilan").child(
            str(yy).strip()+"_"+str(mm).strip()+"/"+str(dd).strip()).get().val()

        # get slow moving
        slow = fbdb.child("slowmoving_shilan").child(
            str(yy).strip()+"_"+str(mm).strip()+"/"+str(dd).strip()).get().val()

        storage = 0
        display = 0
        total = 0
        sumdata = False
        if summary != None:
            storage = summary['storage_inv']
            display = summary['display_inv']
            total = storage + display
            
            '''
            print(summary)
            
            for key in summary:
                print("......", key, summary[key])
            '''
            sumdata = True
        #print("................................",storage, display)

        detdata = False
        if details != None:
            detdata = True

        fasdata = False
        if fast != None:
            fasdata = True

        slodata = False
        if slow != None:
            slodata = True

        return render_template('reportdata.html', summary=summary, sumdata=sumdata, 
            details=details, detdata=detdata, fast=fast, fasdata=fasdata, slow=slow, slodata=slodata, 
            storage=storage, display=display, total=total)


if __name__ == "__main__":
    #app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)
    app.run(host="0.0.0.0", debug=False)