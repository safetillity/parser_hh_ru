from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import traceback
import json
import pickle

# Add the parent directory to the Python path to import the parser
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
hh_dir = os.path.join(parent_dir, 'hh')
sys.path.append(hh_dir)

print(f"[INFO] Current directory: {current_dir}")
print(f"[INFO] Parent directory: {parent_dir}")
print(f"[INFO] HH directory: {hh_dir}")

# Import the researcher module
from researcher import ResearcherHH

app = Flask(__name__)
# Enable CORS for all domains on all routes
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/search', methods=['POST', 'OPTIONS'])
def search():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        print("[INFO] Received request:", request.get_json())
        data = request.get_json()
        query = data.get('query')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400

        print(f"[INFO] Received search query: {query}")
        
        # Initialize and run the parser
        print("[INFO] Initializing researcher...")
        settings_path = os.path.join(hh_dir, 'settings.json')
        print(f"[INFO] Settings path: {settings_path}")
        
        if not os.path.exists(settings_path):
            print(f"[ERROR] Settings file not found at: {settings_path}")
            return jsonify({'error': 'Settings file not found'}), 500
            
        # Read and update settings
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            settings['options'] = {'text': query}
            print(f"[INFO] Updated settings: {settings}")
            
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
            
        researcher = ResearcherHH(config_path=settings_path)
        
        print("[INFO] Updating researcher with query...")
        researcher.update()
        
        print("[INFO] Running researcher...")
        researcher()
        
        print("[INFO] Reading results from CSV...")
        # Read the results from the CSV file
        results = []
        csv_path = os.path.join(hh_dir, 'hh_results.csv')
        print(f"[INFO] CSV path: {csv_path}")
        
        if not os.path.exists(csv_path):
            print(f"[ERROR] CSV file not found at: {csv_path}")
            return jsonify({'error': 'Results file not found'}), 500
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            # Skip header
            next(f)
            for line in f:
                # Parse the CSV line and create a vacancy object
                parts = line.strip().split(',')
                if len(parts) >= 5:  # Ensure we have all required fields
                    vacancy = {
                        'name': parts[0],
                        'employer': parts[1],
                        'salary': parts[2],
                        'experience': parts[3],
                        'skills': parts[4].split(';') if parts[4] else []
                    }
                    results.append(vacancy)
        
        print(f"[INFO] Found {len(results)} vacancies")
        return jsonify({'vacancies': results})

    except Exception as e:
        print(f"[ERROR] Exception occurred: {str(e)}")
        print(traceback.format_exc())
        # Try to return cached results if available
        try:
            cache_file = os.path.join(hh_dir, 'src', 'cache', '266d99164354e79f0020caa881714d63')
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                    results = []
                    for i in range(len(cached_data['Name'])):
                        vacancy = {
                            'name': cached_data['Name'][i],
                            'employer': cached_data['Employer'][i],
                            'salary': 'N/A',
                            'experience': cached_data['Experience'][i],
                            'skills': cached_data['Keys'][i]
                        }
                        results.append(vacancy)
                    return jsonify({'vacancies': results, 'note': 'Using cached data'})
        except Exception as cache_error:
            print(f"[ERROR] Failed to load cached data: {str(cache_error)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("[INFO] Starting server on http://localhost:5001")
    app.run(debug=True, port=5001, host='0.0.0.0') 