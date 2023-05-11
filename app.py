import datetime
import tempfile
from flask import Flask, jsonify, request, send_file
import sqlite3
from dateutil.relativedelta import relativedelta
import corona_stock
import matplotlib.pyplot as plt


app = Flask(__name__)



corona_stock.creat_db()



@app.route('/personalDetails', methods=['POST'])
def add_personalDetails():
    # Add a new personal to the database
    data = request.json
    name = data['firstLastName']
    id = data['id']
    city = data['city']
    street = data['street']
    number = data['number']
    dateOfBirth = data['dateOfBirth']
    telephone = data['telephone']
    mobilePhone = data['mobilePhone']
    dateRecePositiveResult = data['dateRecePositiveResult']
    recoveryDate = data['recoveryDate']
    if not name.isalpha():
        return jsonify({"error": " Must contain only letters "})
    if name == 'None' or id == 'None' or city == 'None' or street == 'None' or number == 'None' or dateOfBirth == 'None' or telephone == 'None' or mobilePhone == 'None':
        return jsonify({"error": " The values are invalid "})
    # If the recovery date is earlier than the sick date
    if recoveryDate != 'None' and dateRecePositiveResult == 'None':
        return jsonify({"error": " The values are invalid "})
    if recoveryDate < dateRecePositiveResult:
        return jsonify({"error": " The date of recovery is earlier than the date of illness "})
    dateOfBirth1 = datetime.datetime.strptime(dateOfBirth, '%Y-%m-%d').date()
    if dateOfBirth1 > datetime.date.today():
        return jsonify({"error": " Date of birth is incorrect"})
    id1 = str(id)
    if not len(id1) == 9:
        return jsonify({'invalid sintax ': ' id must be len = 9 '})
    if not id1.isdigit():
        return jsonify({'invalid sintax ': ' Must contain only numbers '})
    # if not is_valid_phone_number(mobilePhone):
    #     return jsonify({'invalid sintax ': ' The phone number '})
    ides = corona_stock.execute_query('SELECT id FROM personalDetails WHERE id = ?', (id,))
    if ides:
        return jsonify({"error": " This key exists in the table "})
    corona_stock.execute_query(
        'INSERT INTO personalDetails (firstLastName, id,city,street,number,dateOfBirth,telephone,mobilePhone, dateRecePositiveResult , recoveryDate  ) VALUES (?, ?,?,?,?,?,?,?,?,?)',
        (name, id, city, street, number, dateOfBirth, telephone, mobilePhone, dateRecePositiveResult, recoveryDate))
    return jsonify({"seccedd": "User added successfully"})


@app.route('/coronaDetails', methods=['POST'])
def add_coronaDetails():
    # Add a new user to the database
    data = request.json
    # print("data", data)
    id = data['id']
    dateReceVaccin = data['dateReceVaccin']
    manufacturerVaccine = data['manufacturerVaccine']
    if id == 'None' or dateReceVaccin == 'None' or manufacturerVaccine == 'None':
        return jsonify({"error": " The values are invalid "})
    # Checks whether such a key already exists in the table
    num = corona_stock.execute_query('SELECT * FROM coronaDetails WHERE id = ? and dateReceVaccin = ?', (id, dateReceVaccin))
    if num:
        return jsonify({"error": " This key exists in the table "})
    # Checking if there is such a member in the health fund
    ides = corona_stock.execute_query('SELECT id FROM personalDetails WHERE id = ?', (id,))
    if not ides:
        return jsonify({'error ': ' You are not a member of a health fund '})
    ides = corona_stock.execute_query('SELECT id FROM coronaDetails WHERE id = ?', (id,))
    if len(ides) == 4:
        return jsonify({'error ': ' There are already 4 vaccines in the system '})

    corona_stock.execute_query('INSERT INTO coronaDetails (id, dateReceVaccin, manufacturerVaccine ) VALUES (?, ?,?)',
              (id, dateReceVaccin, manufacturerVaccine))
    return jsonify({"seccedd": "User added successfully"})



@app.route('/images', methods=['POST'])
def add_image():
    request_id = request.form['id']
    image_file = request.files.get('imageFile')
    image_bytes = image_file.read()  # convert to bytes
    schema = corona_stock.execute_query('SELECT id FROM images WHERE id = ?', (request_id,))
    if schema:
        return jsonify({"error": " This key exists in the table "})
    schema = corona_stock.execute_query('SELECT id FROM personalDetails WHERE id = ?', (request_id,))
    if not schema:
        return jsonify({'error ': ' You are not a member of a health fund '})
    corona_stock.execute_query('INSERT INTO images (id, image) VALUES (?,?)', (request_id, sqlite3.Binary(image_bytes),))
    return "OK", 200


# Displays the POS members table
@app.route('/personalDetails', methods=['GET'])
def get_personalDetails():
    schema = corona_stock.execute_query('SELECT * FROM personalDetails')
    return jsonify(schema)



# Displays the table of POS members by ID card
@app.route('/personalDetails/<int:id>', methods=['GET'])
def get_schema_by_id(id):
    schema = corona_stock.execute_query('SELECT * FROM personalDetails WHERE id = ?', (id,))
    if not schema:
        return jsonify({"error": " You are not a member of a health fund "})
    return jsonify(schema)



# Shows the vaccinations of a member of a health fund according to an ID card
@app.route('/coronaDetails/<int:id>')
def get_record(id):
    schema = corona_stock.execute_query('SELECT * FROM coronaDetails WHERE id = ?', (id,))
    if not schema:
        return jsonify({"error": " You are not a member of a health fund "})
    return jsonify(schema)




@app.route('/images/<int:image_id>', methods=['GET'])
def get_image(image_id):
    image = corona_stock.get_image_from_db(image_id)
    if image is None:
        return "Image not found", 404

    # Create a temporary file to store the image
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(image)
        tmp_file.flush()
        # Return the file as a response with the appropriate content type header
        return send_file(tmp_file.name, mimetype='image/jpeg' )



# The number of vaccinations a particular person has received
@app.route('/numVaccinations/<int:id>', methods=['GET'])
def get_numVaccinations(id):
    num_vaccinations = corona_stock.get_num_vaccinations(id)
    if num_vaccinations is None:
        return jsonify({"error": " This key doesnt exists in the table "})
    return jsonify(num_vaccinations)



# Brings the address list of members of the health insurance fund
@app.route('/addresses', methods=['GET'])
def get_addresses():
    query = 'SELECT city, street FROM personalDetails'
    result = corona_stock.execute_query(query)
    return jsonify(result)




# The number of members who are not vaccinated
@app.route('/numNotVaccinated', methods=['GET'])
def get_numNotVaccinated():
    query = ('SELECT count(id) FROM personalDetails WHERE id not in '
             '(SELECT DISTINCT id FROM coronaDetails)')
    result = corona_stock.execute_query(query)
    return jsonify(result[0])



@app.route('/ActivePatientsInLastMonth', methods=['GET'])
def get_ActivePatientsInLastMonth():
    date_now = datetime.date.today()
    new_date = datetime.date(date_now.year, date_now.month - 1, date_now.day)
    first_day_of_month = new_date.replace(day=1)
    last_day_of_month = first_day_of_month + relativedelta(months=1, days=-1)
    query = '''SELECT dateRecePositiveResult, recoveryDate 
                   FROM personalDetails 
                   WHERE dateRecePositiveResult >= ? AND dateRecePositiveResult <= ? 
                   OR recoveryDate >= ? 
                   OR recoveryDate = ? AND dateRecePositiveResult != ?'''
    args = (first_day_of_month, last_day_of_month, first_day_of_month, None, None)
    active_patients = corona_stock.execute_query(query, args)
    Graph_active_patients_in_last_month = {}
    number_active_patients = 0
    day_in_month = first_day_of_month
    while day_in_month <= last_day_of_month:
        for date in active_patients:
            date_illness = datetime.datetime.strptime(date[0], '%Y-%m-%d').date()
            if date[1] == 'None':
                if date_illness <= day_in_month:
                    number_active_patients += 1
            else:
                date_recovery = datetime.datetime.strptime(date[1], '%Y-%m-%d').date()
                if date_illness <= day_in_month and day_in_month <= date_recovery or date_illness <= day_in_month and date_recovery is None:
                    number_active_patients += 1
        Graph_active_patients_in_last_month[str(day_in_month)] = number_active_patients
        if day_in_month == last_day_of_month:
            break
        day_in_month = day_in_month.replace(day=day_in_month.day + 1)
        number_active_patients = 0
    x = list()
    y = list()
    for date, value in Graph_active_patients_in_last_month.items():
        x.append(date)
        y.append(value)

    fig, ax = plt.subplots()
    ax.plot(x, y)
    # Save the plot to a file
    fig.savefig('plot.png')
    # Return the file as a response
    return send_file('plot.png', mimetype='image/png')





if __name__ == '__main__':
    app.run()





