import requests
import folium
from geopy.geocoders import Nominatim
import pandas as pd
from newsapi.newsapi_client import NewsApiClient
from email.message import EmailMessage
import ssl
import smtplib
from email.mime.image import MIMEImage

def get_news():
    url = "https://newsapi.org/v2/everything?q=women%20safety&apiKey=edaddbc3add54ca8920075e114cfec09"
    response = requests.get(url).json()
    return response


def get_lat_long_from_address(address):
    locator = Nominatim(user_agent='myapp')
    location = locator.geocode(address)
    return location.latitude, location.longitude

def get_route(lat1, long1, lat2, long2):
    url = "https://trueway-directions2.p.rapidapi.com/FindDrivingRoute"

    querystring = {"stops":"{0},{1}; {2},{3}".format(lat1, long1, lat2, long2)}

    headers = {
        "X-RapidAPI-Key": "d136a898admsh769a12d85806a56p1d0f24jsna19b023692ae",
        "X-RapidAPI-Host": "trueway-directions2.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response


def create_map(response):
    mls = response.json()['route']['geometry']['coordinates']
    points = [(mls[i][0], mls[i][1]) for i in range(len(mls))]
    m = folium.Map()
    for point in [points[0], points[-1]]:
        folium.Marker(point).add_to(m)
    folium.PolyLine(points, weight=5, opacity=1).add_to(m)
    df = pd.DataFrame(mls).rename(columns={0: 'Lon', 1: 'Lat'})[['Lat', 'Lon']]
    sw = df[['Lon', 'Lat']].min().values.tolist()
    ne = df[['Lon', 'Lat']].max().values.tolist()
    m.fit_bounds([sw, ne])
    return m


def get_nearest(my_lat, my_long):
    url = "https://trueway-places.p.rapidapi.com/FindPlacesNearby"

    querystring = {"location": "{}, {}".format(my_lat, my_long), "type": "police_station", "radius": "2000", "language": "en"}

    headers = {
        "X-RapidAPI-Key": "d136a898admsh769a12d85806a56p1d0f24jsna19b023692ae",
        "X-RapidAPI-Host": "trueway-places.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.json()


def send_email(mail_receiver, name, lat, long):
    print("*************Send Email Function************")
    mail_sender = ''
    mail_password = ''
    subject = 'Emergency Alert'
    text = f'Emergency Help Request from {name} from location: ({lat}, {long})'

    em = EmailMessage()
    em['From'] = mail_sender
    em['To'] = mail_receiver
    em['Subject'] = subject  # Corrected the key to 'Subject'

    # Set the formatted body content to the email
    em.set_content(text)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(mail_sender, mail_password)
        smtp.send_message(em)