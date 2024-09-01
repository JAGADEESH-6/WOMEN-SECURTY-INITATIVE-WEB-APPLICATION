from flask import Flask, render_template, request, redirect, url_for,flash , jsonify
import json 
import utils

app = Flask(__name__)

map = "map"

global police_station_name
global destination
global routes_map 
global source
global latitude
global longitude

news_list = utils.get_news()["articles"][:6]

class Post:
    def __init__(self, title, image_url):
        self.title = title
        self.image_url = image_url


with open("details.json", "r") as jf:
    data = json.load(jf)


# Sample posts
posts = []
for i in range(len(news_list)):
    posts.append(Post(news_list[i]["title"], news_list[i]["urlToImage"]))

print(posts)


@app.route('/', methods=['GET', 'POST'])
def login():
    message = request.args.get('message')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password1']
        
        # You can add your authentication logic here.
        # For demonstration purposes, we'll just print the input data.
        print(f'username: {username}, password1: {password}')

        if username in data["login"].keys() and data["login"][username]==password:
            return redirect(url_for('home'))
    
    return render_template('./login.html' )


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password1']
        confirmpassword = request.form['confirmpassword']
        
        # You can add your authentication logic here.
        # For demonstration purposes, we'll just print the input data.
        print(f'email: {email},username: {username}, password1: {password} ,  confirmpassword: {confirmpassword}')
        
        with open("details.json", "w") as jfk:
            data["login"][username] = password
            json.dump(data, jfk)

        return redirect(url_for('login'))

    return render_template('./signup.html')


@app.route('/home' , methods=['GET', 'POST'] )
def home():
    # message = request.args.get('message')
    global source
    global destination
    if request.method == 'POST':
        source = request.form.get('source')
        destination = request.form.get('destination')
        print('src ' + source+ "dest"+ destination)
        # optimize_safety = 'Optimize Safety' in request.form
        # avoid_dark_areas = 'Avoid Dark Areas' in request.form

         # You can process the form data here or perform any other desired actions
        source_lat, source_long = utils.get_lat_long_from_address(source)
        destination_lat, destination_long = utils.get_lat_long_from_address(destination)
        route = utils.get_route(source_lat, source_long, destination_lat, destination_long)
        print( route)
        routes_map = utils.create_map(route)

        print(f'Source: {source}, Destination: {destination}')
       

       
        # return redirect(url_for('map_1' , map=routes_map._repr_html_()) )
        return render_template('map_1.html' , map=routes_map._repr_html_(), source=source, destination=destination)
    
    return render_template('home.html' , posts=posts)

@app.route('/dashboard' , methods=['GET', 'POST'] )
def dashboardv():
    message = request.args.get('message')

    user_details = data["profile"]

    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        contact_number = request.form.get('contact-number')
        home_address = request.form.get('home-address')
        emergency_number = request.form.get('emergency-number')

        # Print the form data to the console
        print(f'Email: {email}')
        print(f'Username: {username}')
        print(f'Contact Number: {contact_number}')
        print(f'Home Address: {home_address}')
        print(f'Emergency Number: {emergency_number}')
        
        # return redirect(url_for('home'))
        with open("details.json", "w") as jfd:
            profile_data = {"username": username, "email":email, "contact":contact_number, "address":home_address, "emergency": emergency_number.strip()}
            data["profile"] = profile_data
            json.dump(data, jfd)
    
    return render_template('dashboard.html', user_details=user_details)



@app.route('/dashboard/profile-picture-update', methods=['POST'])
def update_profile_picture():
    try:
        # Check if the 'profilePicture' file is in the request
        if 'profilePicture' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
         
        file = request.files['profilePicture']
        print(file)
        # Check if the file is empty
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Save the file to the upload folder
       
        
        # Return the path to the uploaded file
        return jsonify({'profilePicturePath': file.filename})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/map_1' , methods=['GET', 'POST'] )
def map_1():
    message = request.args.get('message')
    # if request.method == 'POST':
        # source = request.form.get('source')
        # destination = request.form.get('destination')
        # # optimize_safety = 'Optimize Safety' in request.form
        # # avoid_dark_areas = 'Avoid Dark Areas' in request.form

        #  # You can process the form data here or perform any other desired actions

        # print(f'Source: {source}, Destination: {destination}')

        # return redirect(url_for('home'))
        
    
    return render_template('map_1.html', source=source)

# # Initialize variables
# police_station_name = ""
# destination = ""
# routes_map = ""


@app.route('/map_2' , methods=['GET', 'POST'] )
def map_2():
  
   try:
        # police_station_name = "Lalbagh Police Station"
        # destination = "XH3P+H62, Lalbagh Gate, Lal Bagh Rd, Jaya Nagar"
        # routes_map = ""
        
        global police_station_name
        global destination
        global routes_map 
        global latitude
        global longitude
       
        data = request.get_json()
        longitude = data.get('longitude')
        latitude = data.get('latitude')
        print(f'longitude: {longitude}')
        print(f'latitude: {latitude}')

        police_station_list = utils.get_nearest(latitude, longitude)["results"][0]
        police_station_name = police_station_list["name"]
        destination = police_station_list["address"]
        dest_lat, dest_long = police_station_list["location"]["lat"], police_station_list["location"]["lng"]
        route = utils.get_route(latitude, longitude, dest_lat, dest_long)
        routes_map = utils.create_map(route)
        print(f'Police Station: {police_station_name}')
        
       
        return jsonify({"status": "success", "police_station_name": police_station_name , "destination": destination, "map": routes_map._repr_html_(), })
   
   except Exception as e:
         return render_template('map_2.html')



@app.route('/map_2/police' , methods=['GET', 'POST'] )
def map_2_police():
    global police_station_name
    global destination
    global routes_map 
   
    if request.method == 'POST':
        print("Contact to police")
        # return redirect(url_for('home'))
        message =  "Connected to police"
        return render_template('map_2.html',message = message )

    # Pass the data to the HTML template
    return render_template('map_2.html', police_station_name=police_station_name,destination=destination , map=routes_map)



@app.route('/help', methods=['GET', 'POST'])
def help():
    message = request.args.get('message')
    
    global latitude
    global longitude

    # Placeholder for emergency contact number (replace with actual logic to fetch or set the number)
    emergency_contact = data["profile"]["emergency"]
    user_name = data["profile"]["username"]

    if request.method == 'POST':
        print("SOS Request received!")

        try:
            utils.send_email(emergency_contact, user_name, latitude, longitude)
        except Exception as e:
            print(e)
            return jsonify({"status": "Failed", "emergency_contact_number": emergency_contact})

        return jsonify({"status": "success", "emergency_contact_number": emergency_contact})

    return render_template('help.html', emergency_contact_number=emergency_contact, lat=latitude, long=longitude)



if __name__ == '__main__':
    app.run(debug=True)
