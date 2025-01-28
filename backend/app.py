from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import tensorflow as tf
import numpy as np
from PIL import Image as PILImage
from class_names import CLASS_NAMES

print("Loaded CLASS_NAMES length:", len(CLASS_NAMES))
print("First few classes:", CLASS_NAMES[:5])

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
# Update this path
app.config['MODEL_PATH'] = '/Users/urishamir/Desktop/GitHub/_ai_model_api/backend/ai_model/working_model_food101_v2'
db = SQLAlchemy(app)

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Load the TensorFlow model
model = None


def load_model():
    global model
    try:
        print(f"TensorFlow version: {tf.__version__}")
        print(f"Attempting to load model from: {app.config['MODEL_PATH']}")

        # Use TFSMLayer for Keras 3 compatibility
        model = tf.keras.layers.TFSMLayer(
            app.config['MODEL_PATH'],
            call_endpoint='serving_default'
        )
        print("Model loaded successfully!")
        print(f"Model type: {type(model)}")
        print(f"Model summary: {model}")

    except Exception as e:
        print(f"Error loading model: {str(e)}")
        print(f"Full error details: {e.__class__.__name__}")





# Database Model


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    prediction = db.Column(db.String(255))
    confidence = db.Column(db.Float)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def preprocess_image(image_path):
    """Preprocess image for model prediction"""
    try:
        # Load and resize image
        img = PILImage.open(image_path)
        img = img.resize((224, 224))  # Adjust size to match your model's input
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)  # Create batch axis
        img_array = img_array / 255.0  # Normalize pixel values
        return img_array
    except Exception as e:
        print(f"Error preprocessing image: {str(e)}")
        return None


def get_prediction(image_path):
    """Get model prediction for an image"""
    try:
        print(f"Starting prediction for: {image_path}")

        if model is None:
            print("Error: Model not loaded")
            return "Model not loaded", 0.0

        # Preprocess the image
        print("Preprocessing image...")
        processed_image = preprocess_image(image_path)
        if processed_image is None:
            print("Error: Image preprocessing failed")
            return "Error processing image", 0.0

        print("Making prediction...")
        # Get prediction - TFSMLayer returns a dict of outputs
        predictions = model(processed_image)
        print(f"Raw predictions: {predictions}")

        # Get the output tensor
        prediction_tensor = list(predictions.values())[0]
        print(f"Prediction tensor shape: {prediction_tensor.shape}")

        predicted_class_idx = np.argmax(prediction_tensor[0])
        confidence = float(prediction_tensor[0][predicted_class_idx])

        print(f"Predicted class index: {predicted_class_idx}")
        print(f"Confidence: {confidence}")

        return CLASS_NAMES[predicted_class_idx], confidence

    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        print(f"Error type: {type(e)}")
        return "Error in prediction", 0.0


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        try:
            # Save file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Get prediction
            prediction, confidence = get_prediction(filepath)

            # Save to database
            image = Image(
                filename=filename,
                prediction=prediction,
                confidence=confidence
            )
            db.session.add(image)
            db.session.commit()

            return jsonify({
                'filename': filename,
                'prediction': prediction,
                'confidence': confidence
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/predictions', methods=['GET'])
def get_predictions():
    """Endpoint to get all predictions"""
    predictions = Image.query.all()
    return jsonify([{
        'id': p.id,
        'filename': p.filename,
        'prediction': p.prediction,
        'confidence': p.confidence
    } for p in predictions])


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        load_model()  # Load the model when starting the app
    app.run(debug=True)
