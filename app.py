#Imports
from flask import Flask, render_template,url_for,request,redirect,abort,flash
from flask_sqlalchemy import SQLAlchemy
from Databases import *
from Class import Judge,Registrar,Lawyer
from datetime import datetime,date

today = date.today()

app = Flask(__name__)

global curr_user,currcaselist,curraddcase
curr_user = None
database = Database()

currcaselist = None
curraddcase = None

def verifyuser(username,typ):
    global curr_user,currcaselist
    if curr_user == None or curr_user.isloggedin() == False:
        curr_user = None
        return False
    elif curr_user.getUsername() != username or curr_user.getType() != typ:
        return False

    return True

@app.route('/',methods = ['POST','GET'])
def home():
    if request.method == 'POST':
        return redirect(url_for('login'))
    return render_template('HomePage.html')

@app.route('/login',methods=['POST','GET'])
def login():
    global curr_user,currcaselist
    if curr_user!= None:
        if curr_user.getType()=="reg":
            return redirect(url_for('reghome',username = curr_user.getUsername()))
        elif curr_user.getType() == "jud":
            return redirect(url_for('judhome',username = curr_user.getUsername()))
        elif curr_user.getType() == "law":
            return redirect(url_for('lawhome',username = curr_user.getUsername()))
    if request.method == 'POST':
        temp = request.form.to_dict()
        # print(formatuserinput(temp))
        x = formatuserinput(temp)
        if database.checkUser(x[1],x[2]):
            if database.getTypeOfUser(x[1]) == x[0]:
                if x[0]=="jud":
                    x.append(database.getNameOfUser(x[1]))
                    curr_user = Judge(x)
                    return redirect(url_for('judhome',username=x[1]))
                elif x[0] == "law":
                    x.append(database.getNameOfUser(x[1]))
                    x.append(database.getMoneyOfUser(x[1]))
                    curr_user = Lawyer(x)
                    return redirect(url_for('lawhome',username=x[1]))
                else: 
                    x.append(database.getNameOfUser(x[1]))
                    curr_user = Registrar(x)
                    return redirect(url_for('reghome',username=x[1]))
            else:
                return render_template('login.html',error=True)
        else:
            return render_template('login.html',error=True)
    return render_template('login.html')


@app.route('/jud/<username>',methods = ['POST','GET'])
def judhome(username):
    global curr_user,currcaselist
    if not verifyuser(username,"jud"):
        return render_template('403.html')

    msg1 = "Please enter an input"
    msg2 = "Please enter an Integer for CIN."
    msg3 = "There is no case with the given CIN number. Please try again."
    
    if request.method == 'POST':

        if request.form['submit_button'] == "Log Out":
            curr_user = None
            return redirect(url_for('home'))

        elif request.form['submit_button'] == "Search":
            temp = request.form.to_dict()
            if temp['cin']=="" and temp['key'] == "":
                return render_template('judge.html',message = curr_user.getName(),error = msg1)
            elif temp['cin']!="":
                try:
                    int(temp['cin'])
                except ValueError:
                    return render_template('judge.html',message = curr_user.getName(),error = msg2)
                if int(temp['cin']) < 1 or int(temp['cin']) >= database.getNextCIN():
                    return render_template('judge.html',message = curr_user.getName(),error = msg3)
                
                return redirect(url_for('view_case',CIN = int(temp['cin'])))

            elif temp['key']!="":
                lis = database.getCaseByKeyword(temp['key'])
                currcaselist = lis
                return redirect(url_for('viewcaselist'))


    return render_template('judge.html',message = curr_user.getName())

@app.route('/law/<username>',methods = ['POST','GET'])
def lawhome(username):
    global curr_user,currcaselist
    if not verifyuser(username,"law"):
        return render_template('403.html')

    msg1 = "Please enter an input"
    msg2 = "Please enter an Integer for CIN."
    msg3 = "There is no case with the given CIN number. Please try again."
    msg4 = "You don't have enough money to view any case. Please consult Registrar to add money to your wallet."

    if request.method == 'POST':

        if request.form['submit_button'] == "Log Out":
            curr_user = None
            return redirect(url_for('home'))

        elif request.form['submit_button'] == "Search":
            temp = request.form.to_dict()

            if curr_user.getMoney()<5:
                return render_template('lawyer.html',message = curr_user.getName(),money = curr_user.getMoney(),error = msg4)

            if temp['cin']=="" and temp['key'] == "":
                return render_template('lawyer.html',message = curr_user.getName(),money = curr_user.getMoney(),error = msg1)

            elif temp['cin']!="":
                try:
                    int(temp['cin'])
                except ValueError:
                    return render_template('lawyer.html',message = curr_user.getName(),money = curr_user.getMoney(),error = msg2)
                if int(temp['cin']) < 1 or int(temp['cin']) >= database.getNextCIN():
                    return render_template('lawyer.html',message = curr_user.getName(),money = curr_user.getMoney(),error = msg3)
                
                curr_user.subtractMoney()
                database.subtractMoney(curr_user.getUsername())
                return redirect(url_for('view_case',CIN = int(temp['cin'])))

            elif temp['key']!="":
                lis = database.getCaseByKeyword(temp['key'])
                currcaselist = lis
                return redirect(url_for('viewcaselist'))


    return render_template('lawyer.html',message = curr_user.getName(),money = curr_user.getMoney())

@app.route('/reg/<username>/',methods = ['POST','GET'])
def reghome(username):
    global curr_user,currcaselist
    if not verifyuser(username,"reg"):
        return render_template('403.html')

    if request.method == 'POST':

        if request.form['submit_button'] == "Log Out":
            curr_user = None
            return redirect(url_for('home'))

        elif request.form['submit_button'] == "Add User":
            return redirect(url_for('signup',username = username))

        elif request.form['submit_button'] == "Delete User":
            return redirect(url_for('deleteuser',username = username))

        elif request.form['submit_button'] == "Add Money":
            return redirect(url_for('addmoney',username=username))

        elif request.form['submit_button'] == "View Case Details":
            return redirect(url_for('viewcasedetails',username = username))

        elif request.form['submit_button'] == "Get Case Status":
            return redirect(url_for('getcasestatus',username = username))

        elif request.form['submit_button'] == "Add Case":
            return redirect(url_for('addcase',username = username))

        elif request.form['submit_button'] == "Update Case":
            return redirect(url_for('updatecase',username = username))
            

    return render_template('registrar.html',message = curr_user.getName())

@app.route('/reg/<username>/updatecase',methods = ['POST','GET'])
def updatecase(username):
    global curr_user,currcaselist,curraddcase
    if not verifyuser(username,"reg"):
        return render_template('403.html')

    msg1 = "Please Enter a valid CIN."
    msg2 = "Hearing summary cannot be left empty."
    msg3 = "Adjournment Reason cannot be left empty."
    msg4 = "You can't add hearing summary to this case right now."
    msg5 = "You cannot Update a closed Case."
    msg6 = "Judgement cannot be left empty."
    msg7 = "Case Summary cannot be left empty."
    msg8 = "Case is already closed."

    if request.method == 'POST':
        temp = request.form.to_dict()
        if temp['tab'] == "hear":
            try:
                int(temp['cin'])
            except ValueError:
                return render_template('updatecase.html',error = msg1)

            if int(temp['cin'])<1 or int(temp['cin'])>=database.getNextCIN():
                return render_template('updatecase.html',error = msg1)

            if temp['summary'] == "":
                return render_template('updatecase.html',error = msg2)
            
            curraddcase = database.getCaseByCIN(temp['cin'])
            if curraddcase[12] == "Closed":
                return render_template('updatecase.html',error = msg5)
            if database.verifyDate(curraddcase[15])==False or database.verifyDatebeforeToday(curraddcase[15]):
                todaydate = today.strftime("%d") + "/"+ today.strftime("%m") + "/" + today.strftime("%Y")
                curraddcase[17].append([todaydate,temp['summary']])
                curraddcase[15] = ""
                return redirect(url_for('updatecase_slot',username = username))
            else:
                return render_template('updatecase.html',error = msg4)

        elif temp['tab'] == "adj":
            try:
                int(temp['cin1'])
            except ValueError:
                return render_template('updatecase.html',error = msg1)

            if int(temp['cin1'])<1 or int(temp['cin1'])>=database.getNextCIN():
                return render_template('updatecase.html',error = msg1)

            if temp['reason'] == "":
                return render_template('updatecase.html',error = msg3)
            
            curraddcase = database.getCaseByCIN(temp['cin1'])
            if curraddcase[12] == "Closed":
                return render_template('updatecase.html',error = msg5)
            todaydate = today.strftime("%d") + "/"+ today.strftime("%m") + "/" + today.strftime("%Y")
            curraddcase[16].append([todaydate,temp['reason']])
            curraddcase[15] = ""
            return redirect(url_for('updatecase_slot',username = username))

        elif temp['tab'] == "clo":
            try:
                int(temp['cin2'])
            except ValueError:
                return render_template('updatecase.html',error = msg1)
            
            if int(temp['cin2'])<1 or int(temp['cin2'])>=database.getNextCIN():
                return render_template('updatecase.html',error = msg1)

            if temp['judgement'] == "":
                return render_template('updatecase.html',error = msg6)

            if temp['casesummary'] == "":
                return render_template('updatecase.html',error = msg7)

            curraddcase = database.getCaseByCIN(temp['cin2'])
            if curraddcase[12] == "Closed":
                return render_template('updatecase.html',error = msg8)

            todaydate = today.strftime("%d") + "/"+ today.strftime("%m") + "/" + today.strftime("%Y")
            curraddcase[14] = todaydate
            curraddcase[12] = "Closed"
            curraddcase[18] = temp['judgement']
            curraddcase[13] = temp['casesummary']
            curraddcase[15] = "None"
            database.updateCase(curraddcase)
            curraddcase = None
            return render_template('updatecase.html',success = "Succesfully Closed the Case!")

    return render_template('updatecase.html')

@app.route('/reg/<username>/updatecase/chooseslot',methods = ['POST','GET'])
def updatecase_slot(username):
    global curr_user,currcaselist,curraddcase
    url = request.referrer
    if url == None or curraddcase == None or not verifyuser(username,"reg"):
        return render_template('403.html')

    msg1 = "Please enter a valid Date. Date shouldn't be before today."

    if request.method == 'POST':
        temp = request.form.to_dict()
        
        if database.verifyDatefromToday(temp['date']) == False:
            return render_template('Slot.html',error = msg1)

        return redirect(url_for('updatecase_slotwithdate',username = username, date = formatdatetodiff(temp['date'])))

    return render_template('Slot.html')

@app.route('/reg/<username>/updatecase/chooseslot/<date>',methods = ['POST','GET'])
def updatecase_slotwithdate(username,date):
    global curr_user,currcaselist,curraddcase
    url = request.referrer
    if url == None or curraddcase == None or not verifyuser(username,"reg"):
        return render_template('403.html')

    msg1 = "Please enter a valid Date. Date shouldn't be before today."

    if request.method == 'POST':
        temp = request.form.to_dict()
        if temp['date'] != "":
            if database.verifyDatefromToday(temp['date']) == False:
                return render_template('Slot.html',error = msg1)
            return redirect(url_for('updatecase_slotwithdate',username = username, date = formatdatetodiff(temp['date'])))
        
        date = formatdifftodate(date)
        slot = int(temp['submit_button'][10:])
        curraddcase[15] = date
        database.updateSlots(date,slot)
        database.updateCase(curraddcase)
        curraddcase = None
        return render_template('updatecase.html',success = "Successfully Updated the Case!")

    date = formatdifftodate(date)
    x = database.getEmptySlots(date)
    finalx = []
    for i in range(6):
        if i in x:
            finalx.append(True)
        else:
            finalx.append(False)

    return render_template('Slot.html',i = finalx,date = formatdatetodiff(date))

@app.route('/reg/<username>/addcase',methods = ['POST','GET'])
def addcase(username):
    global curr_user,currcaselist,curraddcase
    if not verifyuser(username,"reg"):
        return render_template('403.html')

    msg1 = "Please Fill all the fields. None of the fields can be empty."
    msg2 = "Please enter a valid Crime Date."
    msg3 = "Please enter a valid Arrest Date."

    if request.method == 'POST':
        temp = request.form.to_dict()
        temp = list(temp.values())

        for x in temp:
            if x == "":
                return render_template('addcase.html',error = msg1)

        if database.verifyDatebeforeToday(temp[3]) == False:
            return render_template('addcase.html',error = msg2)

        if database.verifyDatebeforeToday(temp[6]) == False:
            return render_template('addcase.html',error = msg3)

        todaydate = today.strftime("%d") + "/"+ today.strftime("%m") + "/" + today.strftime("%Y")
        temp.append(todaydate) #start date of the case
        temp.append("Pending") #Case just added
        for _ in range(3):
            temp.append("") #for case summary, end date, Date of Hearing(for now)
        temp.append([])
        temp.append([])
        temp.append("")
        temp.insert(0,database.getNextCIN())

        curraddcase = temp
        # print(curraddcase)
        return redirect(url_for('addcase_slot',username = username))

    return render_template('addcase.html')

@app.route('/reg/<username>/addcase/chooseslot',methods = ['POST','GET'])
def addcase_slot(username):
    global curr_user,currcaselist,curraddcase
    url = request.referrer
    if url == None or curraddcase == None or not verifyuser(username,"reg"):
        return render_template('403.html')

    msg1 = "Please enter a valid Date. Date shouldn't be before today."

    if request.method == 'POST':
        temp = request.form.to_dict()
        
        if database.verifyDatefromToday(temp['date']) == False:
            return render_template('Slot.html',error = msg1)

        return redirect(url_for('addcase_slotwithdate',username = username, date = formatdatetodiff(temp['date'])))

    return render_template('Slot.html')

@app.route('/reg/<username>/addcase/chooseslot/<date>',methods = ['POST','GET'])
def addcase_slotwithdate(username,date):
    global curr_user,currcaselist,curraddcase
    url = request.referrer
    if url == None or curraddcase == None or not verifyuser(username,"reg"):
        return render_template('403.html')

    msg1 = "Please enter a valid Date. Date shouldn't be before today."

    if request.method == 'POST':
        temp = request.form.to_dict()
        if temp['date'] != "":
            if database.verifyDatefromToday(temp['date']) == False:
                return render_template('Slot.html',error = msg1)
            return redirect(url_for('addcase_slotwithdate',username = username, date = temp['date']))
        
        date = formatdifftodate(date)
        slot = int(temp['submit_button'][10:])
        curraddcase[15] = date
        database.updateSlots(date,slot)
        database.addCase(curraddcase)
        curraddcase = None
        return render_template('addcase.html',success = "Successfully Added the Case!")

    date = formatdifftodate(date)
    x = database.getEmptySlots(date)
    finalx = []
    for i in range(6):
        if i in x:
            finalx.append(True)
        else:
            finalx.append(False)

    return render_template('Slot.html',i = finalx,date = formatdatetodiff(date))


@app.route('/reg/<username>/signup',methods = ['POST','GET'])
def signup(username):
    global curr_user,currcaselist
    if not verifyuser(username,"reg"):
        return render_template('403.html')

    if request.method == 'POST':
        temp = request.form.to_dict()
        x = formatsingininput(temp)

        #User format: type, username, password, name

        if database.ifUserExists(x[0]):
            return render_template('signup.html',error = "Username already exists. Please try again.")
        
        msg1 = "Password Length should be atleast 8 digits. Please try again."
        if x[3]=="jud":
            if len(x[1])<8:
                return render_template('signup.html',error = msg1)
            database.createUser(x[0],x[1],x[2],x[3])
        else:
            if len(x[1])<8:
                return render_template('signup.html',error = msg1)
            database.createUser(x[0],x[1],x[2],x[3],"0")

        return render_template('signup.html',success = "Successfully Added the user!")

    return render_template('signup.html')

@app.route('/reg/<username>/delete',methods = ['POST','GET'])
def deleteuser(username):
    global curr_user,currcaselist
    if not verifyuser(username,"reg"):
        return render_template('403.html')

    if request.method == 'POST':
        temp = request.form.to_dict()

        msg1 = "No user with the given username exists. Please try again."
        
        if temp['tab'] == "jud":
            if database.ifUserExists(temp['username']) == False:
                return render_template('delete.html',error = msg1)
            database.deleteUser(temp['username'])

        else :
            if database.ifUserExists(temp['username1']) == False:
                return render_template('delete.html',error = msg1)
            database.deleteUser(temp['username1'])

        return render_template('delete.html',success = "Deleted Succesfully!")
    
    return render_template('delete.html')

@app.route('/reg/<username>/addmoney',methods = ['POST','GET'])
def addmoney(username):
    global curr_user,currcaselist
    if not verifyuser(username,"reg"):
        return render_template('403.html')

    if request.method == 'POST':
        temp = request.form.to_dict()

        msg1 = "No lawyer with the given username exists. Please try again."
        msg2 = "Please enter a valid integer for money. It should be between 1 and 1000.(Both Inclusive)"

        if database.ifUserExists(temp['name'])==False:
            return render_template('money.html',error = msg1)

        elif database.getTypeOfUser(temp['name']) != "law":
            return render_template('money.html',error = msg1)
        
        else:
            try:
                int(temp['amt'])
            except ValueError:
                return render_template('money.html',error = msg2)
            if int(temp['amt'])<1 or int(temp['amt'])>1000:
                return render_template('money.html',error=msg2)

        database.AddMoneyToUser(temp['name'],int(temp['amt']))
        # curr_user.addMoney(int(temp['amt']))
        return render_template('money.html',success = "Successfully added Money!!")
    return render_template('money.html')

@app.route('/reg/<username>/viewcasedetails',methods = ['POST','GET'])
def viewcasedetails(username):
    global curr_user,currcaselist
    if not verifyuser(username,"reg"):
        return render_template('403.html')

    if request.method == 'POST':

        if request.form['submit_button'] == "Pending Cases":
            lis = database.getCaseByStatus("Pending")
            currcaselist = lis
            return redirect(url_for('viewcaselist'))

        elif request.form['submit_button'] == "Upcoming Cases":
            return redirect(url_for('getUpcomingCases',username=username))

        elif request.form['submit_button'] == "Resolved Cases":
            return redirect(url_for('getResolvedCases',username = username))

    return render_template('viewcase.html')

@app.route('/reg/<username>/getUpcomingCases',methods = ['POST','GET'])
def getUpcomingCases(username):
    global curr_user,currcaselist
    if not verifyuser(username,"reg"):
        return render_template('403.html')

    if request.method == 'POST':
        temp = request.form.to_dict()

        if database.verifyDatefromToday(temp['date']) == False:
            return render_template('Upcoming.html',error = "Please enter a Valid date.")

        currcaselist = database.getCaseByDateOfHearing(temp['date'])
        return redirect(url_for('viewcaselist'))

    return render_template('Upcoming.html')

@app.route('/reg/<username>/getResolvedCases',methods = ['POST','GET'])
def getResolvedCases(username):
    global curr_user,currcaselist
    if not verifyuser(username,"reg"):
        return render_template('403.html')

    if request.method == 'POST':
        temp = request.form.to_dict()

        if database.verifyDate(temp['frdate']) == False or database.verifyDate(temp['todate']) == False:
            return render_template('Resolved.html',error = "Please enter valid dates.")

        currcaselist = database.getAllCasesBetweenTwoDates(temp['frdate'],temp['todate'])
        return redirect(url_for('viewcaselist'))

    return render_template('Resolved.html')

@app.route('/reg/<username>/getcasestatus',methods = ['POST','GET'])
def getcasestatus(username):
    global curr_user,currcaselist
    if not verifyuser(username,"reg"):
        return render_template('403.html')

    msg1 = "Please enter an input"
    msg2 = "Please enter an Integer for CIN."
    msg3 = "There is no case with the given CIN number. Please try again."

    if request.method == 'POST':
        temp = request.form.to_dict()
        if temp['cin'] == "":
            return render_template('status.html',error = msg1)

        else:
            try:
                int(temp['cin'])
            except ValueError:
                return render_template('status.html',error = msg2)

            if int(temp['cin'])<1 or int(temp['cin']) >= database.getNextCIN():
                return render_template('status.html',error = msg3)

            return render_template('status.html',success = database.getCaseStatus(int(temp['cin'])))

    return render_template('status.html')

@app.route('/view_case/<int:CIN>/',methods = ['POST','GET'])
def view_case(CIN):
    global curr_user,currcaselist
    url = request.referrer
    if url == None or curr_user == None:
        return render_template('403.html')

    # print(url)

    if request.method == 'POST':

        if request.form['submit_button'] == "View Hearings":
            return redirect(url_for('view_hearings',CIN = CIN))

        elif request.form['submit_button'] == "View Adjournments":
            return redirect(url_for('view_adjournments',CIN=CIN))

    temp = database.getCaseByCIN(CIN)
    return render_template('casedet.html',message = temp)

@app.route('/view_case/<int:CIN>/view_adjournments')
def view_adjournments(CIN):
    global curr_user,currcaselist
    url = request.referrer
    if url == None or curr_user == None:
        return render_template('403.html')

    temp = database.getCaseByCIN(CIN)
    return render_template('adjournment.html',message = temp[16])

@app.route('/view_case/<int:CIN>/view_hearings')
def view_hearings(CIN):
    global curr_user,currcaselist
    url = request.referrer
    if url == None or curr_user == None:
        return render_template('403.html')

    temp = database.getCaseByCIN(CIN)
    return render_template('hearing.html',message = temp[17])

@app.route('/viewcaselist/',methods = ['POST','GET'])
def viewcaselist():
    global curr_user,currcaselist
    url = request.referrer
    if url == None or curr_user == None:
        return render_template('403.html')

    msg1 = "You don't have enough balance to view a case. Please try again."

    if request.method == 'POST':

        CIN = request.form['submit_button'][11:]
        CIN = int(CIN)
        
        if curr_user.getType() == "law":
            if curr_user.getMoney()<5:
                return render_template('caselist.html',message = currcaselist, error = msg1)
            curr_user.subtractMoney()
            database.subtractMoney(curr_user.getUsername())

        return redirect(url_for('view_case',CIN = CIN))


    return render_template('caselist.html',message = currcaselist)


if __name__=="__main__":
    app.run(debug=True)