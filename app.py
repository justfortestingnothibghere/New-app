from flask import Flask, request, jsonify, render_template, send_from_directory
from supabase import create_client, Client
from werkzeug.utils import secure_filename
import os

# Flask setup
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Temporary folder for file uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Supabase credentials
SUPABASE_URL = "https://buenbdkodjrpzsfjsddu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ1ZW5iZGtvZGpycHpzZmpzZGR1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIwOTM3MjQsImV4cCI6MjA3NzY2OTcyNH0.8AOdXZtF3kaNnJ8dSEpEinD4RZM7GEy-nVtTV3o81B4"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Serve static files (HTML, JS, CSS)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

# API: Signup with auth and profile image
@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.form
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        username = data.get('username')
        password = data.get('password')
        profile_image = request.files.get('profile_image')

        # Validate required fields
        if not all([name, email, phone, username, password]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Sign up with Supabase Auth
        auth_response = supabase.auth.sign_up({
            'email': email,
            'password': password,
            'options': {
                'data': {
                    'name': name,
                    'username': username
                }
            }
        })
        
        if auth_response.user is None:
            return jsonify({'error': auth_response.error.message if auth_response.error else 'Signup failed'}), 400

        user = auth_response.user
        image_url = None
        if profile_image:
            filename = secure_filename(f"{user.id}.{profile_image.filename.split('.')[-1]}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_image.save(file_path)

            # Upload to Supabase storage
            with open(file_path, 'rb') as f:
                upload_response = supabase.storage.from_('profiles').upload(filename, f)
            os.remove(file_path)  # Clean up

            if upload_response.error:
                return jsonify({'error': 'Image upload failed: ' + upload_response.error.message}), 400

            # Get public URL
            image_url = supabase.storage.from_('profiles').get_public_url(filename).data['publicUrl']

        # Insert into users table
        user_data = {
            'id': user.id,
            'name': name,
            'email': email,
            'phone': phone,
            'username': username,
            'profile_image': image_url
        }
        db_response = supabase.table('users').insert(user_data).execute()

        if db_response.error:
            return jsonify({'error': 'Database error: ' + db_response.error.message}), 400

        return jsonify({'message': 'Signup successful', 'user': db_response.data}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Login
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not all([email, password]):
            return jsonify({'error': 'Missing email or password'}), 400

        auth_response = supabase.auth.sign_in_with_password({
            'email': email,
            'password': password
        })

        if auth_response.user is None:
            return jsonify({'error': auth_response.error.message if auth_response.error else 'Login failed'}), 400

        return jsonify({'message': 'Login successful', 'user': auth_response.user.id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Get all users (for testing, requires RLS policy)
@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        res = supabase.table('users').select('*').execute()
        if res.error:
            return jsonify({'error': res.error.message}), 400
        return jsonify(res.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Update user
@app.route('/api/update_user/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.form
        name = data.get('name')
        username = data.get('username')
        phone = data.get('phone')
        profile_image = request.files.get('profile_image')

        update_data = {}
        if name:
            update_data['name'] = name
        if username:
            update_data['username'] = username
        if phone:
            update_data['phone'] = phone

        if profile_image:
            filename = secure_filename(f"{user_id}.{profile_image.filename.split('.')[-1]}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_image.save(file_path)

            with open(file_path, 'rb') as f:
                upload_response = supabase.storage.from_('profiles').upload(filename, f, {'upsert': True})
            os.remove(file_path)

            if upload_response.error:
                return jsonify({'error': 'Image upload failed: ' + upload_response.error.message}), 400

            update_data['profile_image'] = supabase.storage.from_('profiles').get_public_url(filename).data['publicUrl']

        if not update_data:
            return jsonify({'error': 'No data provided to update'}), 400

        res = supabase.table('users').update(update_data).eq('id', user_id).execute()
        if res.error:
            return jsonify({'error': res.error.message}), 400
        return jsonify(res.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Delete user
@app.route('/api/delete_user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        res = supabase.table('users').delete().eq('id', user_id).execute()
        if res.error:
            return jsonify({'error': res.error.message}), 400
        return jsonify({'message': 'User deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
