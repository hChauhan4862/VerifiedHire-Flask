import flask
from flask import render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
from web3 import Web3
import json
from hexbytes import HexBytes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import hashlib
import os
import datetime
import random 
import requests
from third_party.hs_api import UPBOARD_HS_MARKSHEET_API
from third_party.ss_api import UPBOARD_SS_MARKSHEET_API

app = flask.Flask(__name__, template_folder='Templates')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

web3 = Web3(Web3.HTTPProvider('http://localhost:7545'))


with open("build/contracts/EmployeeManagement.json") as f:
    employee_management_compiled = json.load(f)
employee_contract_address = "0xC8341F73E7Af5C261aC29be65b281A1649Fa1681" 
employee_contract_instance = web3.eth.contract(
    address=employee_contract_address,
    abi=employee_management_compiled["abi"]
)

with open("build/contracts/RecruiterManagement.json") as f:
    recruiter_management_compiled = json.load(f)
recruiter_contract_address = "0xea7564af4C237B0f1f77F3CC701E350BCA305599"
recruiter_contract_instance = web3.eth.contract(
    address=recruiter_contract_address,
    abi=recruiter_management_compiled["abi"]
)

with open("build/contracts/EmployeeInfo.json") as f:
    employee_info_management_compiled = json.load(f)
employee_info_contract_address = "0xbDf781546EA6910C04DDf8F5922899148721F3E2" 
employee_info_contract_instance = web3.eth.contract(
    address=employee_info_contract_address,
    abi=employee_info_management_compiled["abi"]
)



tx_params = {
    'from': "0x49bb737E407798dB0E3c00c3D81D885973ace78B",
    'gas': 2000000,  # Adjust gas limit as needed
}

@app.route('/employeelogin', methods=['GET', 'POST'])
def employeelogin():
    if flask.request.method == 'GET':
        return(flask.render_template('signin-employee.html'))
    
@app.route('/employeeindex', methods=['GET', 'POST'])
def employeeindex():
    if flask.request.method == 'GET':
        if "role" in session:
            return flask.render_template('employee-index.html')
        else:
            return(flask.render_template('signin-employee.html'))
        
@app.route('/getallemployee', methods=['GET', 'POST'])
def getallemployee():
    if flask.request.method == 'POST':
        employee_data = employee_contract_instance.functions.getAllEmployees().call()
        return jsonify(employee_data)
    
@app.route('/getallrecruitor', methods=['GET', 'POST'])
def getallrecruitor():
    if flask.request.method == 'POST':
        employee_data = recruiter_contract_instance.functions.getAllRecruiters().call()
        return jsonify(employee_data)
    
@app.route('/getallverification', methods=['GET', 'POST'])
def getallverification():
    if flask.request.method == 'POST':
        employee_data = recruiter_contract_instance.functions.getAllVerificationRecords().call()
        return jsonify(employee_data)
        
@app.route('/recruitorindex', methods=['GET', 'POST'])
def recruitorindex():
    if flask.request.method == 'GET':
        return flask.render_template('recruitor-index.html')
    
@app.route('/employeeregister', methods=['GET', 'POST'])
def employeeregister():
    if flask.request.method == 'GET':
        return(flask.render_template('signup-employee.html'))

s = smtplib.SMTP('smtp.gmail.com', 587)
s.starttls()
s.login("hchauhan4862@gmail.com", "kfsy dhbk msha cwhr")
sender_email_id = "hchauhan4862@gmail.com"

@app.route('/registeremployeeRequest', methods=['POST'])
def registeremployeeRequest():
    
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        aadhaar = request.form['aadhaar']
        gender = request.form['gender']

        from third_party.aadhaar import demographic_auth

        try:
            print(aadhaar, name, gender)
            a = demographic_auth(aadhaar, name, gender)
            print(a)

            if a["error"] != "success":
                return jsonify({'status': 'error', 'message': str(a["error"])})
            
        except Exception as e:
            return jsonify({'status': 'error', 'message': "Could Not Verify Aadhaar Details"})
        
        

        uid =  str(random.randint(100000, 999999))
        try:
            tx_hash = employee_contract_instance.functions.registerEmployee(name, email, password, phone, str(uid)).transact(tx_params)
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            
            out = {'status': 'success', 
                   'message': 'Employee registered successfully', 
                   'transactionstatus': receipt.status,
                   'gasused': receipt.cumulativeGasUsed,
                   'block':receipt.blockNumber}
            
           
            
            subject = "Welcome to Verified-Hire Portal"
            

            # Message content
            body = f"Hi Mr./Mrs. {name},\n\nWelcome to the Verified-Hire portal!\n\nWe are providing a blockchain empowered background verification for professionals. Here is your user Unique ID for recognizing your records:\nUID: {uid}.\nYou can share this ID with the recruiters for the background verification process.\n\nRegards,\nVerified-Hire Team."
        
            msg = MIMEMultipart()
            msg['From'] = sender_email_id
            msg['To'] = email
            msg['Subject'] = subject
            
            # Attach the message body
            msg.attach(MIMEText(body, 'plain'))
            
            # sending the mail
            s.sendmail(sender_email_id, email, msg.as_string())
            
            
            
            
            return jsonify(out)
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
        

@app.route('/registerrecuitorRequest', methods=['POST'])
def registerrecuitorRequest():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        company = request.form['company']
        admin = "0"
        try:
            tx_hash = recruiter_contract_instance.functions.registerRecruiter(name, email, password, phone, company, admin).transact(tx_params)
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            
            out = {'status': 'success', 
                   'message': 'Employee registered successfully', 
                   'transactionstatus': receipt.status,
                   'gasused': receipt.cumulativeGasUsed,
                   'block':receipt.blockNumber}
        
            return jsonify(out)
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
        
@app.route('/loginemployeeRequest', methods=['POST'])
def loginemployeeRequest():
    if request.method == 'POST':
        password = request.form['password']
        email = request.form['email']
        
        try:
            tx_hash = employee_contract_instance.functions.employeeLogin(email, password).transact(tx_params)
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt.status == 1:
                session["role"] = "employee"
                session["email"] = email
            out = {'status': receipt.status, 
                   'message': 'Recruiter login successfully', 
                   'transactionstatus': receipt.status,
                   'gasused': receipt.cumulativeGasUsed,
                   'block':receipt.blockNumber,
                   }
        
            return jsonify(out)
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})


@app.route('/loginrecuitorRequest', methods=['POST'])
def loginrecuitorRequest():
    if request.method == 'POST':
        password = request.form['password']
        email = request.form['email']
    
        try:
            rec_data = recruiter_contract_instance.functions.getRecruiterByEmail(email).call()
            if rec_data[2] == password:
                if rec_data[5] == "0":
                    msg = "2"
                else:
                    session["email"] = rec_data[1]
                    session["role"] = 'recruiter'
                    msg = "1"
            else:
                msg = "0"
            return jsonify(msg)
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
        
@app.route('/loginadminrequest', methods=['POST'])
def loginadminrequest():
    if request.method == 'POST':
        password = request.form['password']
        email = request.form['email']
        try:
            if email == 'verifiedhireadmin@gmail.com' and password == "Admin@123":
                session["role"] = "admin"
                session["email"] = email
                return jsonify("1")
            else:
                return jsonify("0")
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
        
@app.route('/getemployeeData', methods=['POST'])
def getemployeeData():
    if request.method == 'POST':
        if "role" not in session:
            return flask.render_template('employee-index.html')
        
        email = session.get("email")
        try:
            employee_data = employee_contract_instance.functions.getEmployeeByEmail(email).call()
            basic_info = employee_info_contract_instance.functions.getBasicInfoByEmail(email).call()
            working_info = employee_info_contract_instance.functions.getWorkingInfoByEmail(email).call()
            academic_info = employee_info_contract_instance.functions.getAcademicInfoByEmail(email).call()
            files_info = employee_info_contract_instance.functions.getProofInfoByEmail(email).call()
            endor_info = employee_info_contract_instance.functions.getAllEndorestInfo().call()
            out = {
                'employee_data':employee_data,
                'basic_info':basic_info,
                'working_info':working_info,
                'academic_info':academic_info,
                'proof_info':files_info,
                "endor_info":endor_info
            }

            return jsonify(out)
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
        
@app.route('/getendoresedata', methods=['POST'])
def getendoresedata():
    if request.method == 'POST':
        try:
            endor_info = employee_info_contract_instance.functions.getAllEndorestInfo().call()
            
            unique_records = {}
            for record in endor_info:
                key = record[0] 
                if key in unique_records and record[5] == "none":
                    continue
        
                unique_records[key] = record
            filtered_records = list(unique_records.values())
            return jsonify(filtered_records)
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
        
        
@app.route('/getrecruitorData', methods=['POST'])
def getrecruitorData():
    if request.method == 'POST':
        if "role" not in session:
            return flask.render_template('recruitor-index.html')
        
        email = session.get("email")
        try:
            rec_data = recruiter_contract_instance.functions.getRecruiterByEmail(email).call()
            out = {
                'employee_data':rec_data
                }
            return jsonify(out)
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})

@app.route('/acceptrecruiter', methods=['POST'])
def acceptrecruiter():
    if request.method == 'POST':
        iddata = request.form['id']
        typedata = request.form['type']
        
        tx_hash = recruiter_contract_instance.functions.updateAdmin(iddata, typedata).transact(tx_params)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        
        if typedata == "1":
            subject = "Verified Hire Acceptance Mail"
            body = f"Dear Recruiter,\n\nWelcome to the Verified-Hire portal!. Our Team has approved your registeration request and now you can login with our system using your credentials.\n\n\nThanks & Regards,\nVerified-Hire Team."
        
            msg = MIMEMultipart()
            msg['From'] = sender_email_id
            msg['To'] = iddata
            msg['Subject'] = subject
            
            # Attach the message body
            msg.attach(MIMEText(body, 'plain'))
            
            # sending the mail
            s.sendmail(sender_email_id, iddata, msg.as_string())
            
        out = {'status': receipt.status, 
               'message': 'Recruiter update successfully', 
               'transactionstatus': receipt.status,
               'gasused': receipt.cumulativeGasUsed,
               'block':receipt.blockNumber,
               }
    
        return jsonify(out)
        
@app.route('/recuitorSearch', methods=['POST'])
def recuitorSearch():
    if request.method == 'POST':
        uid = request.form['uid']
        try:
            
            email = employee_contract_instance.functions.getEmailByUID(uid).call()
            
            employee_data = employee_contract_instance.functions.getEmployeeByEmail(email).call()
            basic_info = employee_info_contract_instance.functions.getBasicInfoByEmail(email).call()
            working_info = employee_info_contract_instance.functions.getWorkingInfoByEmail(email).call()
            academic_info = employee_info_contract_instance.functions.getAcademicInfoByEmail(email).call()
            files_info = employee_info_contract_instance.functions.getProofInfoByEmail(email).call()
            endor_info = employee_info_contract_instance.functions.getEndorestInfoByEmail(email).call()
            out = {
                'employee_data':employee_data,
                'basic_info':basic_info,
                'working_info':working_info,
                'academic_info':academic_info,
                'proof_info':files_info,
                "endor_info":endor_info
            }
            
            recruiter = session.get("email")
            recdata = recruiter_contract_instance.functions.getRecruiterByEmail(recruiter).call()
            
            recname = recdata[0]
            recemail = recdata[1]
            company = recdata[4]
            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            verifytime = str(formatted_datetime)
            if email != "":
                uid = uid
            else:
                uid=str(uid)+'notfound'
            tx_hash = recruiter_contract_instance.functions.addVerificationRecord(recname, company, recemail, uid, verifytime).transact(tx_params)
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return jsonify(out)
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
        


@app.route('/uploaddp', methods=['POST'])
def uploaddp():
    if request.method == 'POST':
    
        file = request.files['image']
        uploadpath = 'static/profileimages'
        filename = file.filename
        file.save(os.path.join(uploadpath, filename))
        return jsonify("1")
    

@app.route('/uploadproofs', methods=['POST'])
def uploadproofs():
    files = request.files.getlist('file[]')
    file_paths = []
    filenames = []
    for file in files:
        filename = file.filename
        filenames.append(filename)
        file_path = os.path.join('static/userproofs', filename)
        file.save(file_path)
        file_paths.append(file_path)
    
    try:
       fname0 = filenames[0]
    except IndexError:
       fname0 = ""
    
    try:
       fname1 = filenames[1]
    except IndexError:
       fname1 = ""
       
    try:
       fname2 = filenames[2]
    except IndexError:
       fname2 = ""
       
    try:
       fname3 = filenames[3]
    except IndexError:
       fname3 = ""
       
    try:
       fname4 = filenames[4]
    except IndexError:
       fname4 = ""
    
    
    email = session.get("email")
    tx_hash1 = employee_info_contract_instance.functions.setProofInfo(email, fname0, fname1, fname2, fname3, fname4).transact(tx_params)
    tx_receipt1 = web3.eth.wait_for_transaction_receipt(tx_hash1)

    return jsonify({'message': 'Proofs are uploaded successfully', 'file_paths': file_paths}), 200


@app.route('/fetchDocumentUsingAPI', methods=['POST'])
def fetchDocumentUsingAPI():
    if request.method == 'POST':
        document_data = request.json
        if document_data["document_type"] == "10th" or document_data["document_type"] == "12th":
            if document_data["district"] is None or document_data["passing_year"] is None:
                return jsonify({'status': 'error', 'message': 'Invalid data'})

            if document_data["document_type"] == "10th":
                data = UPBOARD_HS_MARKSHEET_API(int(document_data["passing_year"]), document_data["district"], document_data["roll_number"])
            else:
                data = UPBOARD_SS_MARKSHEET_API(int(document_data["passing_year"]), document_data["district"], document_data["roll_number"])

            if "error" in data and data["error"] is not None:
                return jsonify({'status': 'error', 'message': data["error"]})

            return jsonify({'status': 'success', 'data': data["data"]})

        if document_data["document_type"] == "pan":
            if document_data["panno"] is None:
                return jsonify({'status': 'error', 'message': 'Invalid data'})

            URL = "https://app-moneyview.whizdm.com/loans/services/api/lending/nsdl"
            req = requests.post(URL, data={"pan": document_data["panno"]}, verify=False, headers={"x-mv-app-version": "433"})
            if req.status_code == 200:
                return jsonify({
                    "DOCUMENT_TYPE": "PAN_CARD",
                    "pan": document_data["panno"],
                    "name": req.json()
                })

            return jsonify({'status': 'error', 'message': 'Pan Number Details Could Not Found'})

        return jsonify({'status': 'error', 'message': 'Invalid data'})

@app.route('/addDocument', methods=['POST'])
def addDocument():
    if request.method == 'POST':
        document_data = request.json
        json_data_str = json.dumps(document_data['json_data'])  # Convert dict to JSON string
        tx_hash1 = employee_info_contract_instance.functions.addDocument(
            session.get("email"),
            document_data['title'],
            document_data['document_id'],
            document_data['file_name'],
            document_data['file_url'],
            json_data_str,  # Pass the JSON string instead of dict
            document_data['verified_by']
        ).transact(tx_params)
        tx_receipt1 = web3.eth.wait_for_transaction_receipt(tx_hash1)
        return jsonify(detail="Document added successfully")
    

@app.route('/requestEndorest', methods=['POST'])
def requestEndorest():
    if request.method == 'POST':
       
        skill =  request.form['endoskill']
        describe = request.form['describe']
        current_date_time = datetime.datetime.now()
        current_date_str = current_date_time.strftime("%d/%m/%Y")
        email = session.get("email")
        endid = str(random.randint(1000, 9999))
        tx_hash1 = employee_info_contract_instance.functions.setEndorestInfo(endid, email, skill, describe, "0", "none", "no", current_date_str).transact(tx_params)
        tx_receipt1 = web3.eth.wait_for_transaction_receipt(tx_hash1)
        
        return jsonify({'message': 'Endorest request successfully'}), 200
    
@app.route('/rejectendorest', methods=['POST'])
def reject_endorest():
    if request.method == 'POST':
        endid = request.form['endid']
        email = request.form['email']
        subject = request.form['subject']
        description = request.form['description']
        score = request.form['score']
        status = request.form['status']
        hasupdated = request.form['hasupdated']
        on = request.form['on']
        
        tx_hash1 = employee_info_contract_instance.functions.setEndorestInfo(endid, email, subject, description, score, status, hasupdated, on).transact(tx_params)
        tx_receipt1 = web3.eth.wait_for_transaction_receipt(tx_hash1)
        
        return jsonify({'message': 'Endorest request successfully'}), 200
        
    
@app.route('/sendendoresexam', methods=['POST'])
def sendendoresexam():
    if request.method == 'POST':
        
        endid = request.form['endid']
        email = request.form['email']
        subject = request.form['subject']
        description = request.form['description']
        score = request.form['score']
        status = request.form['status']
        hasupdated = request.form['hasupdated']
        on = request.form['on']
        
        tx_hash1 = employee_info_contract_instance.functions.setEndorestInfo(endid, email, subject, description, score, status, hasupdated, on).transact(tx_params)
        tx_receipt1 = web3.eth.wait_for_transaction_receipt(tx_hash1)
        
        msubject = "Verified Hire Endorestment Test"
        
        url = 'http://127.0.0.1:5000/exampage?endid='+endid+'&subject='+str(subject)
    
        body = f"Hi There, \n\nYou received this mail because you have requested for skill updation from the verified-hire portal for the skill {subject} on {on} !\n\nYou can take the test from the URL : {url}\n\nRegards,\nVerified-Hire Team."
    
        msg = MIMEMultipart()
        msg['From'] = sender_email_id
        msg['To'] = email
        msg['Subject'] = msubject
        
        # Attach the message body
        msg.attach(MIMEText(body, 'plain'))
        
        # sending the mail
        s.sendmail(sender_email_id, email, msg.as_string())
        
    return jsonify("1")

@app.route('/updateEmployeeScore', methods=['POST'])
def updateEmployeeScore():
    if request.method == 'POST':
        score = request.form['score']
        endid = request.form['endid']
        
        infoid = employee_info_contract_instance.functions.getEndorestInfoByEndorestId(endid).call()
        
        endid = infoid[0]
        email = infoid[1]
        skill = infoid[2]
        describe = infoid[3]
        curscore = int(score)
        if curscore >= 5:
            status = "pass"
        else:
            status = "fail"
        hasupdated = "no"
        current_date_str = infoid[7]
        
        #tx_hash = employee_info_contract_instance.functions.updateScoreByEndoresid(endid, score).transact(tx_params)
        tx_hash1 = employee_info_contract_instance.functions.setEndorestInfo(endid, email, skill, describe, score, status, hasupdated, current_date_str).transact(tx_params)

        return jsonify(infoid)
        
@app.route('/declareresult', methods=['POST'])
def declareresult():
    if request.method == 'POST':
        endid = request.form['endid']
        
        infoid = employee_info_contract_instance.functions.getEndorestInfoByEndorestId(endid).call()
        
        endid = infoid[0]
        email = infoid[1]
        skill = infoid[2]
        describe = infoid[3]
        curscore = int(infoid[4])
        
        if curscore >= 5:
            status = "pass"
            notifyresult(email, status, skill, infoid[4])
        else:
            status = "fail"
            notifyresult(email, status, skill, infoid[4])
        
        hasupdated = "yes"
        current_date_str = infoid[7]
        
        working_info = employee_info_contract_instance.functions.getWorkingInfoByEmail(email).call()
        existingskill = working_info[7]
        
        newskill = existingskill+", "+skill
        
        tx_hash = employee_info_contract_instance.functions.updateSkillByEmail(email, newskill).transact(tx_params)

    return jsonify(newskill)
        
        
        
def notifyresult(email, status, skill, score):
    subject = "Verified Hire - Endorestement Exam Result Declaration"
    if status == "fail":
        body = f"""Dear {email},
        We regret to inform you that your score is {score} in the {skill} test, which is less than the required threshold of 5. We encourage you to try again next time.
        \n\n
        Best regards,
        The Verified Hire Team"""
    else:
        body = f"""Dear {email},
            \n\n
            Congratulations! We are pleased to inform you that your score is {score} in the {skill} test. Your skill in {skill} has been recognized and updated in our system.
            
            Best regards,
            The Verified Hire Team"""
        
    msg = MIMEMultipart()
    msg['From'] = sender_email_id
    msg['To'] = email
    msg['Subject'] = subject
    
    # Attach the message body
    msg.attach(MIMEText(body, 'plain'))
    
    # sending the mail
    s.sendmail(sender_email_id, email, msg.as_string())

        
    return "endid"
        
@app.route('/addEmployee', methods=['POST'])
def addEmployee():
    if request.method == 'POST':
        data = request.get_json()
        firstName = data['firstName']
        lastName = data['lastName']
        email = data['email']
        phone = data['phone']
        employeeAddress = data['employeeaddress']
        organizationName = data['organizationname']
        designation = data['designation']
        responsibility = data['responsibility']
        salary = int(data['salary'])
        officeCity = data['officecity']
        totalExperience = int(data['totalexperience'])
        collegeName = data['collegename']
        course = data['course']
        score = int(data['score'])
        university = data['university']
        collegeCity = data['collegecity']
        year = int(data['year'])
        filename = data['filename']
        skill = ''

        tx_hash1 = employee_info_contract_instance.functions.setBasicInfo(firstName, lastName, email, phone, employeeAddress, filename).transact(tx_params)
        tx_receipt1 = web3.eth.wait_for_transaction_receipt(tx_hash1)
        
        tx_hash2 = employee_info_contract_instance.functions.setWorkingInfo(email, organizationName, designation, responsibility, salary, officeCity, totalExperience, skill).transact(tx_params)
        tx_receipt2 = web3.eth.wait_for_transaction_receipt(tx_hash2)
        
        tx_hash3 = employee_info_contract_instance.functions.setAcademicInfo(email, collegeName, course, score, university, collegeCity, year).transact(tx_params)
        tx_receipt3 = web3.eth.wait_for_transaction_receipt(tx_hash3)
        
        

        return {'status': 'success', 'message': 'Employee background details updated successfully into the blocks'}
    else:
        return {'status': 'error', 'message': 'Invalid request method'}
        

@app.route('/')
  
@app.route('/main', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'GET':
        return(flask.render_template('homeindex.html'))
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('logged_out'))

@app.route('/logged_out')
def logged_out():
    return """
    <script>
        window.location.href = "/";
    </script>
    <p>You have been logged out.</p>
    """
        
@app.route('/exampage', methods=['GET', 'POST'])
def exampage():
    if flask.request.method == 'GET':
        return(flask.render_template('exampage.html'))
    
@app.route('/adminsignin', methods=['GET', 'POST'])
def adminsignin():
    if flask.request.method == 'GET':
        return(flask.render_template('signin-admin.html'))
    
@app.route('/employeelist', methods=['GET', 'POST'])
def employeelist():
    if flask.request.method == 'GET':
        return(flask.render_template('admin-employees.html'))
    
@app.route('/recuitorlist', methods=['GET', 'POST'])
def recuitorlist():
    if flask.request.method == 'GET':
        return(flask.render_template('admin-recruitors.html'))
    
@app.route('/endorestmentlist', methods=['GET', 'POST'])
def endorestmentlist():
    if flask.request.method == 'GET':
        return(flask.render_template('admin-endorsement.html'))
    
@app.route('/adminverification', methods=['GET', 'POST'])
def adminverification():
    if flask.request.method == 'GET':
        return(flask.render_template('admin-verification.html'))
    
@app.route('/adminindex', methods=['GET', 'POST'])
def adminindex():
    if flask.request.method == 'GET':
        return(flask.render_template('admin-index.html'))
    
@app.route('/about', methods=['GET', 'POST'])
def about():
    if flask.request.method == 'GET':
        return(flask.render_template('about.html'))
    
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if flask.request.method == 'GET':
        return(flask.render_template('contact.html'))

@app.route('/services', methods=['GET', 'POST'])
def services():
    if flask.request.method == 'GET':
        return(flask.render_template('services.html'))

@app.route('/recruiterlogin', methods=['GET', 'POST'])
def recruiterlogin():
    if flask.request.method == 'GET':
        return(flask.render_template('signin-recruiter.html'))
@app.route('/recruiterregister', methods=['GET', 'POST'])
def recruiterregister():
    if flask.request.method == 'GET':
        return(flask.render_template('signup-recruiter.html'))
@app.route('/joinrequest', methods=['GET', 'POST'])
def joinrequest():
    if flask.request.method == 'GET':
        return(flask.render_template('joinrequest.html'))
    


@app.route('/sendotp', methods=['POST'])
def sendotp():
    if flask.request.method == 'POST':
        
        subject = "OTP for register with blockchain powered verified hire portal"
    
        email = request.form['email']
        phone = request.form['phone']
        name = request.form['name']
        otp = str(random.randint(100000, 999999))

        # Message content
        body = f"Hi Mr./Mrs. {name},\n\nWelcome to the Verified-Hire portal!.\n\nWe are providing a blockchain empowered background verification for the professionals. Here is your user OTP for your registeration: \nOTP : {otp}\n\n\nRegards,\nVerified-Hire Team."
    
        msg = MIMEMultipart()
        msg['From'] = sender_email_id
        msg['To'] = email
        msg['Subject'] = subject
        
        # Attach the message body
        msg.attach(MIMEText(body, 'plain'))
        
        # sending the mail
        s.sendmail(sender_email_id, email, msg.as_string())


        url = "https://www.fast2sms.com/dev/voice?authorization=G1Dpjh3pyY72hQJyNAiTY10REmBKb2RPZrL1VciuZwLjEpzeE5EBBdcaej3e&route=otp&variables_values="+otp+"&numbers="+phone
        response = requests.request("GET", url)
        if response.status_code != 200:
            pass
        
        
        noisy_otp = ""
        for digit in otp:
            noisy_otp += digit
            noisy_otp += chr(random.randint(65, 90)) 

        return jsonify({"out":noisy_otp})

@app.route('/savefile', methods=['POST'])
def save_file():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    # Save the file to a desired location
    file.save('candidatefiles/' + file.filename)
    return jsonify('1')

@app.route('/verifyfile', methods=['POST'])
def verifyfile():
    try:
        # Check if the 'file' key exists in the request
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']

        # Check if the file is empty
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        uploaded_file_data = file.read()
        uploaded_file_hash = hashlib.sha256(uploaded_file_data).hexdigest()

        candidate_file_directory = 'candidatefiles/'

        # Read the corresponding file from the candidate file directory and calculate its hash
        candidate_file_path = candidate_file_directory+(file.filename)
        with open(candidate_file_path, 'rb') as candidate_file:
            candidate_file_data = candidate_file.read()
            candidate_file_hash = hashlib.sha256(candidate_file_data).hexdigest()

        # Compare the hashes
        match = (uploaded_file_hash == candidate_file_hash)

        return jsonify({'match': match}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 
    




        
    
    
if __name__ == '__main__':
    app.run(debug=True)