from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
OPENCAGE_API_KEY = '5f438d095b474eb1ac1acf98a0a138f0'

@app.route('/get-location', methods=['POST'])
def get_location():
    data = request.json
    pincode = data.get('pincode')

    if not pincode:
        return jsonify({'error': 'Pincode is required'}), 400
    response = requests.get(f'https://api.postalpincode.in/pincode/{pincode}')
    
    if response.status_code == 200:
        result = response.json()
        
        if result[0]['Status'] == 'Success':
            location_info = result[0]['PostOffice'][0]
            latitude = location_info.get('Latitude')
            longitude = location_info.get('Longitude')


            if not latitude or not longitude:
                geocode_response = requests.get(
                    f'https://api.opencagedata.com/geocode/v1/json?q={pincode}&key={OPENCAGE_API_KEY}'
                )
                
                if geocode_response.status_code == 200:
                    geocode_result = geocode_response.json()
                    if geocode_result['results']:
                        latitude = geocode_result['results'][0]['geometry']['lat']
                        longitude = geocode_result['results'][0]['geometry']['lng']
                    else:
                        latitude = 'Data not available'
                        longitude = 'Data not available'
                else:
                    latitude = 'Data not available'
                    longitude = 'Data not available'

            response_data = {
                'Town': location_info.get('Name'),
                'City': location_info.get('District'),
                'State': location_info.get('State'),
                'Latitude': latitude,
                'Longitude': longitude
            }
            return jsonify(response_data), 200
        else:
            return jsonify({'error': 'Invalid pincode'}), 404
    else:
        return jsonify({'error': 'Could not fetch data'}), 500

if __name__ == '__main__':
    app.run(debug=True)
