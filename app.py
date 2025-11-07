from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
import os
import requests
import json
from dotenv import load_dotenv
import base64
from PIL import Image, ImageDraw, ImageFont
import io

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='static')
app.secret_key = os.getenv("FLASK_SECRET_KEY", "apna_kisan")

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------------------------------------
# 🔹 Ollama Helper Functions
# ---------------------------------------------

def check_ollama_model(model_name="llava"):
    """Check if the specified model is available in Ollama."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models_data = response.json()
            available_models = [model.get('name', '') for model in models_data.get('models', [])]
            # Check for exact match or partial match (e.g., "llava:latest" or "llava:7b")
            for model in available_models:
                if model_name in model.lower():
                    return True, model
            return False, available_models
        return False, []
    except Exception as e:
        print(f"Error checking Ollama models: {e}")
        return False, []


def ollama_predict_crop_disease(image_path):
    """Use Ollama vision model to predict crop and disease."""
    try:
        # First check if llava model is available
        model_available, model_info = check_ollama_model("llava")
        if not model_available:
            error_msg = (
                "The 'llava' vision model is not installed in Ollama.\n\n"
                "To install it, run this command in your terminal:\n"
                "ollama pull llava\n\n"
                f"Available models: {', '.join(model_info) if isinstance(model_info, list) else 'None'}"
            )
            print(error_msg)
            return {
                'label': 'Error - Model Not Found',
                'score': 0.0,
                'crop_name': 'Error',
                'disease_name': 'llava Model Not Installed',
                'description': error_msg,
                'treatment_tip': 'Please install the llava model: ollama pull llava'
            }
        
        # Use the available model (could be "llava:latest", "llava:7b", etc.)
        model_to_use = model_info if isinstance(model_info, str) else "llava"
        
        # Encode image to base64
        with open(image_path, "rb") as f:
            img_bytes = f.read()
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")

        # Prompt for Ollama - expert agricultural assistant format
        prompt = (
            "You are an expert agricultural assistant specializing in plant pathology. "
            "Analyze the given crop image carefully.\n\n"
            "Identify and describe:\n"
            "1. Any visible disease symptoms (such as black spots, fungal patches, white powder, yellowing, holes, or discoloration).\n"
            "2. Possible disease name (e.g., leaf spot, blight, rust, mildew, nutrient deficiency, etc.).\n"
            "3. Confidence level (Low / Medium / High) — based on how distinct the symptoms appear.\n"
            "4. A short, actionable treatment suggestion that a farmer can follow (use simple, local terms and natural remedies if possible).\n\n"
            "Output only in JSON format:\n"
            '{\n'
            '  "flora_detected": true/false,\n'
            '  "crop_name": "name or unknown",\n'
            '  "disease_name": "name or healthy or unknown",\n'
            '  "symptoms_detected": ["symptom1", "symptom2"],\n'
            '  "confidence_level": "Low/Medium/High",\n'
            '  "treatment_tip": "one short paragraph of advice",\n'
            '  "disease_location": "location description like center, top-left, bottom-right, entire leaf, or none if healthy"\n'
            '}\n\n'
            "If NO plants are found, set flora_detected to false and disease_name to 'No Flora Detected'.\n"
            "If the leaf looks healthy, clearly mention it as 'healthy' with confidence_level 'High'."
        )

        # Call Ollama local API
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_to_use,
                "prompt": prompt,
                "images": [img_base64],
                "stream": False
            },
            timeout=120  # Increased timeout for image processing
        )

        if response.status_code == 200:
            result_data = response.json()
            
            # Extract the response text
            response_text = result_data.get('response', '')
            
            # Try to parse JSON from the response
            try:
                # Sometimes Ollama wraps JSON in markdown code blocks
                if '```json' in response_text:
                    json_start = response_text.find('```json') + 7
                    json_end = response_text.find('```', json_start)
                    response_text = response_text[json_start:json_end].strip()
                elif '```' in response_text:
                    json_start = response_text.find('```') + 3
                    json_end = response_text.find('```', json_start)
                    response_text = response_text[json_start:json_end].strip()
                
                result_json = json.loads(response_text)
                
                # Check if flora was detected
                flora_detected = result_json.get('flora_detected', True)  # Default to True for backward compatibility
                
                if not flora_detected:
                    # No flora detected in the image
                    return {
                        'label': 'No Flora Detected',
                        'score': 1.0,
                        'crop_name': 'No Flora',
                        'disease_name': 'No Flora Detected',
                        'description': result_json.get('treatment_tip', 'No flora (plants, crops, or vegetation) detected in this image.'),
                        'treatment_tip': result_json.get('treatment_tip', 'Please upload an image containing plants, crops, or vegetation for analysis.'),
                        'disease_location': 'none',
                        'symptoms_detected': [],
                        'confidence_level': 'High',
                        'no_flora': True
                    }
                
                # Extract new format fields
                disease_name = result_json.get('disease_name', 'Unknown')
                symptoms = result_json.get('symptoms_detected', [])
                confidence_level = result_json.get('confidence_level', 'Medium')
                treatment_tip = result_json.get('treatment_tip', 'No treatment recommendation available.')
                disease_location = result_json.get('disease_location', 'center')
                crop_name = result_json.get('crop_name', 'Unknown')
                
                # Convert confidence level to numeric score for display
                confidence_map = {'Low': 0.6, 'Medium': 0.75, 'High': 0.9}
                confidence_score = confidence_map.get(confidence_level, 0.75)
                
                # Format the result to match template expectations
                disease_label = f"{crop_name} - {disease_name}"
                
                return {
                    'label': disease_label,
                    'score': confidence_score,
                    'crop_name': crop_name,
                    'disease_name': disease_name,
                    'description': f"Symptoms: {', '.join(symptoms) if symptoms else 'No specific symptoms detected'}",
                    'treatment_tip': treatment_tip,
                    'disease_location': disease_location,
                    'symptoms_detected': symptoms,
                    'confidence_level': confidence_level,
                    'no_flora': False
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, extract information from text
                print("Failed to parse JSON, extracting from text...")
                return parse_text_response(response_text)
        else:
            error_text = response.text[:200] if response.text else "Unknown error"
            print(f"Ollama Error: {response.status_code} - {error_text}")
            
            # Provide specific error messages based on status code
            if response.status_code == 404:
                error_desc = "Model 'llava' not found. Please install it: ollama pull llava"
            elif response.status_code == 400:
                error_desc = f"Invalid request to Ollama: {error_text}"
            else:
                error_desc = f"Ollama API returned error {response.status_code}: {error_text}"
            
            return {
                'label': 'Error - Could not analyze',
                'score': 0.0,
                'crop_name': 'Error',
                'disease_name': 'Analysis Failed',
                'description': error_desc,
                'treatment_tip': 'Please ensure Ollama is running and the llava model is installed: ollama pull llava'
            }

    except requests.exceptions.ConnectionError:
        print("Connection Error: Could not connect to Ollama. Is it running?")
        return {
            'label': 'Error - Ollama not running',
            'score': 0.0,
            'crop_name': 'Error',
            'disease_name': 'Ollama Connection Failed',
            'description': 'Could not connect to Ollama. Please ensure Ollama is running on localhost:11434',
            'treatment_tip': 'Start Ollama service and ensure the llava model is installed: ollama pull llava'
        }
    except Exception as e:
        print(f"Ollama Prediction Error: {e}")
        return {
            'label': 'Error - Analysis failed',
            'score': 0.0,
            'crop_name': 'Error',
            'disease_name': 'Analysis Error',
            'description': f'An error occurred: {str(e)}',
            'treatment_tip': 'Please try again with a different image.'
        }


def highlight_disease_area(image_path, disease_location, disease_name):
    """Highlight the diseased area in red on the image based on location description."""
    try:
        # Open the image
        img = Image.open(image_path)
        img = img.convert('RGB')
        width, height = img.size
        
        # Determine highlight area based on location description
        location_lower = disease_location.lower() if disease_location else 'none'
        
        # Skip highlighting if healthy or no disease
        if 'healthy' in disease_name.lower() or location_lower == 'none' or 'no disease' in location_lower:
            return img
        
        # Convert to RGBA for overlay
        img_rgba = img.convert('RGBA')
        
        # Create a red overlay with transparency
        overlay = Image.new('RGBA', (width, height), (255, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Define highlight regions based on location description
        if 'center' in location_lower or 'middle' in location_lower:
            # Highlight center area
            x1, y1 = int(width * 0.2), int(height * 0.2)
            x2, y2 = int(width * 0.8), int(height * 0.8)
        elif 'top' in location_lower and 'left' in location_lower:
            x1, y1 = 0, 0
            x2, y2 = int(width * 0.5), int(height * 0.5)
        elif 'top' in location_lower and 'right' in location_lower:
            x1, y1 = int(width * 0.5), 0
            x2, y2 = width, int(height * 0.5)
        elif 'bottom' in location_lower and 'left' in location_lower:
            x1, y1 = 0, int(height * 0.5)
            x2, y2 = int(width * 0.5), height
        elif 'bottom' in location_lower and 'right' in location_lower:
            x1, y1 = int(width * 0.5), int(height * 0.5)
            x2, y2 = width, height
        elif 'top' in location_lower:
            x1, y1 = 0, 0
            x2, y2 = width, int(height * 0.5)
        elif 'bottom' in location_lower:
            x1, y1 = 0, int(height * 0.5)
            x2, y2 = width, height
        elif 'left' in location_lower:
            x1, y1 = 0, 0
            x2, y2 = int(width * 0.5), height
        elif 'right' in location_lower:
            x1, y1 = int(width * 0.5), 0
            x2, y2 = width, height
        elif 'entire' in location_lower or 'whole' in location_lower or 'all' in location_lower:
            x1, y1 = 0, 0
            x2, y2 = width, height
        else:
            # Default: highlight center area
            x1, y1 = int(width * 0.25), int(height * 0.25)
            x2, y2 = int(width * 0.75), int(height * 0.75)
        
        # Draw red rectangle with transparency
        overlay_draw.rectangle([x1, y1, x2, y2], fill=(255, 0, 0, 100), outline=(255, 0, 0, 255), width=5)
        
        # Blend the overlay with the original image
        highlighted_img = Image.alpha_composite(img_rgba, overlay)
        
        # Add disease name label
        draw = ImageDraw.Draw(highlighted_img)
        try:
            # Try to use a default font, fallback to basic if not available
            font_size = max(24, int(width / 25))
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Draw disease name label at the top
        text = f"Disease: {disease_name}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Draw background for text (red background)
        draw.rectangle([10, 10, 10 + text_width + 20, 10 + text_height + 20], fill=(255, 0, 0, 220), outline=(255, 0, 0, 255), width=2)
        draw.text((20, 20), text, fill=(255, 255, 255), font=font)
        
        # Convert back to RGB for display
        return highlighted_img.convert('RGB')
        
    except Exception as e:
        print(f"Error highlighting image: {e}")
        import traceback
        traceback.print_exc()
        # Return original image if highlighting fails
        return Image.open(image_path).convert('RGB')


def parse_text_response(text):
    """Parse text response when JSON parsing fails."""
    text_lower = text.lower()
    
    # First check if no flora is detected
    no_flora_keywords = ["no flora", "no plant", "no crop", "no vegetation", "no vegetation detected", 
                         "does not contain", "no plants", "no crops", "no leaves", "no flora detected"]
    if any(keyword in text_lower for keyword in no_flora_keywords):
            return {
                'label': 'No Flora Detected',
                'score': 1.0,
                'crop_name': 'No Flora',
                'disease_name': 'No Flora Detected',
                'description': 'No flora (plants, crops, or vegetation) detected in this image.',
                'treatment_tip': 'Please upload an image containing plants, crops, or vegetation for analysis.',
                'disease_location': 'none',
                'no_flora': True
            }
    
    # Try to extract information from text
    crop_name = "Unknown"
    disease_name = "Unknown"
    confidence = 0.75
    
    # Simple extraction logic
    if "healthy" in text_lower:
        disease_name = "Healthy"
    elif "disease" in text_lower or "blight" in text_lower or "rust" in text_lower:
        # Try to extract disease name
        if "blight" in text_lower:
            disease_name = "Blight"
        elif "rust" in text_lower:
            disease_name = "Rust"
        else:
            disease_name = "Disease Detected"
    
    # Try to extract crop name
    crops = ["tomato", "potato", "apple", "corn", "pepper", "grape", "cherry"]
    for crop in crops:
        if crop in text_lower:
            crop_name = crop.capitalize()
            break
    
    disease_label = f"{crop_name} - {disease_name}"
    
    return {
        'label': disease_label,
        'score': confidence,
        'crop_name': crop_name,
        'disease_name': disease_name,
        'description': text[:200] if len(text) > 200 else text,
        'treatment_tip': 'Please consult with an agricultural expert for specific treatment recommendations.',
        'disease_location': 'center',  # Default location
        'no_flora': False
    }


def ollama_get_fertilizer_recommendation(crop_name, soil_type, water_availability):
    """Get fertilizer recommendations from Ollama based on crop, soil type, and water availability."""
    try:
        # First check if llava model is available (or use any available model)
        model_available, model_info = check_ollama_model("llava")
        if not model_available:
            # Try to use any available model
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    models_data = response.json()
                    available_models = [model.get('name', '') for model in models_data.get('models', [])]
                    if available_models:
                        model_to_use = available_models[0]  # Use first available model
                    else:
                        return None, "No Ollama models available. Please install a model: ollama pull llama3"
                else:
                    return None, "Could not connect to Ollama"
            except:
                return None, "Could not connect to Ollama. Please ensure Ollama is running."
        else:
            model_to_use = model_info if isinstance(model_info, str) else "llama3"
        
        # Create a simple, farmer-friendly prompt for fertilizer recommendation
        prompt = (
            f"You are a helpful agricultural advisor speaking to a farmer. Give simple, clear fertilizer advice.\n\n"
            f"Farmer wants to grow: {crop_name}\n"
            f"Their soil type is: {soil_type}\n"
            f"Water availability: {water_availability}%\n\n"
            f"Give simple advice in plain language that a farmer can easily understand. Use simple words, avoid technical jargon.\n\n"
            f"Respond in JSON format:\n"
            f'{{"recommendation": "simple explanation in 2-3 sentences about what fertilizer to use and why, in easy language", '
            f'"fertilizer_type": "name of fertilizer (like NPK 19:19:19 or Urea) - keep it simple", '
            f'"application_method": "simple step-by-step instructions in plain language (2-3 steps only)", '
            f'"timing": "when to apply in simple words (like before planting or during flowering)", '
            f'"soil_analysis": "one simple sentence about {soil_type} soil and {crop_name}"}}\n\n'
            f"Remember: Use simple words. Write like you are talking to a friend who farms. No complicated terms."
        )
        
        # Call Ollama API
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_to_use,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result_data = response.json()
            response_text = result_data.get('response', '')
            
            # Try to parse JSON from the response
            try:
                # Clean up JSON if wrapped in markdown
                if '```json' in response_text:
                    json_start = response_text.find('```json') + 7
                    json_end = response_text.find('```', json_start)
                    response_text = response_text[json_start:json_end].strip()
                elif '```' in response_text:
                    json_start = response_text.find('```') + 3
                    json_end = response_text.find('```', json_start)
                    response_text = response_text[json_start:json_end].strip()
                
                result_json = json.loads(response_text)
                return result_json, None
            except json.JSONDecodeError:
                # If JSON parsing fails, format the text response
                formatted_recommendation = format_fertilizer_text_response(response_text, crop_name, soil_type, water_availability)
                return formatted_recommendation, None
        else:
            return None, f"Ollama API error: {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return None, "Could not connect to Ollama. Please ensure Ollama is running."
    except Exception as e:
        print(f"Fertilizer recommendation error: {e}")
        return None, f"An error occurred: {str(e)}"


def format_fertilizer_text_response(text, crop_name, soil_type, water_availability):
    """Format text response when JSON parsing fails."""
    return {
        "recommendation": text[:500] if len(text) > 500 else text,
        "fertilizer_type": "General NPK fertilizer",
        "application_method": "Follow standard agricultural practices based on soil type and water availability",
        "timing": "Apply during growing season",
        "soil_analysis": f"Analysis for {crop_name} in {soil_type} soil with {water_availability}% water availability"
    }


def generate_fertilizer_recommendation(disease_name, description, treatment_tip, no_flora=False):
    """Generate fertilizer recommendation based on Ollama analysis."""
    # Handle no flora case
    if no_flora or "no flora" in disease_name.lower():
        return {
            'fertilizer': 'N/A',
            'details': 'No flora detected in the image. Please upload an image containing plants, crops, or vegetation.',
            'application_method': 'N/A - No analysis possible without flora in the image.'
        }
    
    disease_lower = disease_name.lower()
    
    # Use treatment tip from Ollama if available
    if treatment_tip and treatment_tip != 'No treatment recommendation available':
        return {
            'fertilizer': 'Treatment Recommended',
            'details': treatment_tip,
            'application_method': 'Follow the specific treatment recommendations provided above.'
        }
    
    # Fallback recommendations based on disease type
    if "healthy" in disease_lower:
        return {
            'fertilizer': 'General-purpose Fertilizer',
            'details': 'Plant appears healthy. Apply 50g per plant, every two weeks during growing season.',
            'application_method': 'Spread evenly around the base of the plant and water thoroughly.'
        }
    elif "blight" in disease_lower:
        return {
            'fertilizer': 'Copper-based Fungicide',
            'details': 'Apply 150ml per plant. High humidity increases risk, so apply every 7 days.',
            'application_method': 'Mix with water and spray evenly over the leaves.'
        }
    elif "rust" in disease_lower:
        return {
            'fertilizer': 'Sulfur-based Fungicide',
            'details': 'Use 100g per plant. Apply every 5-7 days until symptoms improve.',
            'application_method': 'Dilute in 1L of water and spray thoroughly on affected areas.'
        }
    else:
        return {
            'fertilizer': 'General-purpose Treatment',
            'details': description[:150] if description else 'Consult with an agricultural expert for specific treatment.',
            'application_method': 'Follow standard agricultural practices and monitor plant health regularly.'
        }


# ---------------------------------------------
# 🔹 Flask Routes
# ---------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home')
def home():
    """Redirect to index for the Home link."""
    return redirect(url_for('index'))


@app.route('/crop-recommend')
def crop_recommend():
    """Placeholder route for crop recommendation."""
    return render_template('crop.html', title='Crop Recommendation')


@app.route('/fertilizer')
def fertilizer_recommendation():
    """Placeholder route for fertilizer recommendation."""
    return render_template('fertilizer.html', title='Fertilizer Suggestion')


@app.route('/fertilizer-predict', methods=['POST'])
def fert_recommend():
    """Get fertilizer recommendations using Ollama."""
    title = 'Fertilizer Suggestion'
    
    try:
        # Get form data
        crop_name = request.form.get('cropname', '').strip()
        soil_type = request.form.get('soil_type', '').strip()
        water_availability = int(request.form.get('water_availability', 0))
        
        # Validate inputs
        if not crop_name:
            flash('Please select a crop.', 'error')
            return redirect(url_for('fertilizer_recommendation'))
        
        if not soil_type:
            flash('Please select a soil type.', 'error')
            return redirect(url_for('fertilizer_recommendation'))
        
        if water_availability < 0 or water_availability > 100:
            flash('Water availability must be between 0 and 100%.', 'error')
            return redirect(url_for('fertilizer_recommendation'))
        
        # Get recommendation from Ollama
        recommendation_data, error = ollama_get_fertilizer_recommendation(
            crop_name, soil_type, water_availability
        )
        
        if error:
            flash(f'Error getting recommendation: {error}', 'error')
            return redirect(url_for('fertilizer_recommendation'))
        
        if not recommendation_data:
            flash('Could not generate recommendation. Please try again.', 'error')
            return redirect(url_for('fertilizer_recommendation'))
        
        # Format recommendation as HTML for display
        recommendation_html = format_fertilizer_recommendation_html(recommendation_data, crop_name, soil_type, water_availability)
        
        return render_template('fertilizer-result.html', 
                             recommendation=recommendation_html, 
                             title=title,
                             crop_name=crop_name,
                             soil_type=soil_type,
                             water_availability=water_availability)
        
    except ValueError:
        flash('Please enter a valid water availability percentage (0-100).', 'error')
        return redirect(url_for('fertilizer_recommendation'))
    except Exception as e:
        print(f"Error in fert_recommend: {e}")
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('fertilizer_recommendation'))


def format_fertilizer_recommendation_html(recommendation_data, crop_name, soil_type, water_availability):
    """Format fertilizer recommendation data as simple, farmer-friendly HTML."""
    if isinstance(recommendation_data, dict):
        # Extract key information
        fertilizer_type = recommendation_data.get('fertilizer_type', 'General NPK Fertilizer')
        recommendation = recommendation_data.get('recommendation', 'No specific recommendation available.')
        application = recommendation_data.get('application_method', 'Follow standard agricultural practices.')
        timing = recommendation_data.get('timing', 'Apply during the growing season.')
        soil_analysis = recommendation_data.get('soil_analysis', '')
        
        # Simple, farmer-friendly HTML format
        html = f"""
        <div class="fertilizer-recommendation" style="line-height: 1.8; font-size: 1.1rem;">
            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid #6b8e23;">
                <h3 style="color: #2d5016; margin: 0 0 1rem 0; font-size: 1.4rem;">
                    {crop_name.capitalize()} - Simple Fertilizer Guide
                </h3>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; gap: 1rem; font-size: 1rem;">
                    <div><strong>Crop:</strong> {crop_name.capitalize()}</div>
                    <div><strong>Soil:</strong> {soil_type.capitalize()}</div>
                    <div><strong>Water:</strong> {water_availability}%</div>
                </div>
            </div>
            
            <div style="background: #e8f5e9; padding: 1.2rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid #4caf50;">
                <h4 style="color: #2d5016; margin: 0 0 0.8rem 0; font-size: 1.3rem;">What Fertilizer to Use</h4>
                <p style="font-size: 1.2rem; font-weight: 600; color: #1b5e20; margin: 0;">{fertilizer_type}</p>
            </div>
            
            <div style="margin-bottom: 1.5rem;">
                <h4 style="color: #6b8e23; margin-bottom: 0.5rem; font-size: 1.2rem;">Simple Explanation</h4>
                <p style="margin: 0; color: #333; font-size: 1.05rem;">{recommendation}</p>
            </div>
            
            {f'<div style="margin-bottom: 1.5rem; background: #fff9e6; padding: 1rem; border-radius: 6px;"><h4 style="color: #856404; margin-bottom: 0.5rem; font-size: 1.1rem;">About Your Soil</h4><p style="margin: 0; color: #333;">{soil_analysis}</p></div>' if soil_analysis else ''}
            
            <div style="margin-bottom: 1.5rem;">
                <h4 style="color: #6b8e23; margin-bottom: 0.5rem; font-size: 1.2rem;">How to Use</h4>
                <p style="margin: 0; color: #333; font-size: 1.05rem;">{application}</p>
            </div>
            
            <div style="background: #e3f2fd; padding: 1rem; border-radius: 6px; border-left: 4px solid #2196f3;">
                <h4 style="color: #1565c0; margin-bottom: 0.5rem; font-size: 1.2rem;">When to Use</h4>
                <p style="margin: 0; color: #333; font-size: 1.05rem; font-weight: 500;">{timing}</p>
            </div>
        </div>
        """
    else:
        # Fallback - simple text display
        html = f"""
        <div class="fertilizer-recommendation">
            <h3 style="color: #2d5016; margin-bottom: 1rem;">Recommendation for {crop_name.capitalize()}</h3>
            <p style="line-height: 1.8; color: #333;">{str(recommendation_data)}</p>
        </div>
        """
    
    return html


@app.route('/soil-predict', methods=['POST'])
def soil_prediction():
    """Placeholder route for soil prediction."""
    flash('Soil prediction feature is currently under development.', 'info')
    return redirect(url_for('crop_recommend'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Simple login route - placeholder."""
    if request.method == 'POST':
        flash('Login feature is currently under development. Disease detection is available without login.', 'info')
        return redirect(url_for('disease_prediction'))
    
    # Try to render login template if it exists, otherwise redirect
    login_template = os.path.join(app.template_folder, 'login.html')
    if os.path.exists(login_template):
        return render_template('login.html')
    else:
        flash('Please use the disease detection feature directly.', 'info')
        return redirect(url_for('disease_prediction'))


@app.route('/signup', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Simple registration route - placeholder."""
    if request.method == 'POST':
        flash('Registration feature is currently under development. Disease detection is available without registration.', 'info')
        return redirect(url_for('disease_prediction'))
    
    # Try to render signup template if it exists, otherwise redirect
    signup_template = os.path.join(app.template_folder, 'signup.html')
    if os.path.exists(signup_template):
        return render_template('signup.html')
    else:
        flash('Please use the disease detection feature directly.', 'info')
        return redirect(url_for('disease_prediction'))


@app.route('/disease-predict', methods=['GET', 'POST'])
def disease_prediction():
    title = 'Disease Detection'

    if request.method == 'POST':
        if 'file' not in request.files:
            error = 'No file part in the request'
            return render_template('disease.html', title=title, error=error)
        
        file = request.files.get('file')
        if not file or file.filename == '':
            error = 'No file selected for uploading'
            return render_template('disease.html', title=title, error=error)
        
        if not allowed_file(file.filename):
            error = 'Allowed file types are png, jpg, jpeg'
            return render_template('disease.html', title=title, error=error)

        try:
            # Save the uploaded file
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Get prediction from Ollama
            prediction = ollama_predict_crop_disease(file_path)
            print("Prediction:", prediction)

            # Get no_flora flag
            no_flora = prediction.get('no_flora', False)
            
            # Highlight disease area if disease is detected
            disease_name = prediction.get('disease_name', 'Unknown')
            disease_location = prediction.get('disease_location', 'none')
            
            if not no_flora and 'healthy' not in disease_name.lower():
                # Highlight the diseased area
                highlighted_img = highlight_disease_area(file_path, disease_location, disease_name)
                
                # Convert highlighted image to base64
                buffered = io.BytesIO()
                highlighted_img.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            else:
                # Use original image if healthy or no flora
                with open(file_path, "rb") as f:
                    img_bytes = f.read()
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            # Generate fertilizer recommendation
            fertilizer_info = generate_fertilizer_recommendation(
                prediction.get('disease_name', 'Unknown'),
                prediction.get('description', ''),
                prediction.get('treatment_tip', ''),
                no_flora=no_flora
            )

            # Format prediction for template (matching expected format)
            formatted_prediction = {
                'label': prediction.get('label', 'Unknown'),
                'score': prediction.get('score', 0.0)
            }

            return render_template('disease-result.html', 
                                 prediction=formatted_prediction, 
                                 fertilizer=fertilizer_info, 
                                 image_base64=img_base64, 
                                 title=title,
                                 crop_name=prediction.get('crop_name', 'Unknown'),
                                 disease_name=prediction.get('disease_name', 'Unknown'),
                                 description=prediction.get('description', ''),
                                 treatment_tip=prediction.get('treatment_tip', ''),
                                 symptoms_detected=prediction.get('symptoms_detected', []),
                                 confidence_level=prediction.get('confidence_level', 'Medium'),
                                 no_flora=no_flora)
        
        except Exception as e:
            print(f"Error: {e}")
            error = f'An error occurred during prediction: {str(e)}'
            return render_template('disease.html', title=title, error=error)

    return render_template('disease.html', title=title)


@app.route('/predict', methods=['POST'])
def predict_crop_disease():
    """API endpoint for JSON responses."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Get prediction from Ollama
        prediction = ollama_predict_crop_disease(file_path)
        print("Prediction:", prediction)

        return jsonify(prediction)

    return jsonify({"error": "Something went wrong"}), 500


# ---------------------------------------------
# 🔹 Run Flask App
# ---------------------------------------------
if __name__ == '__main__':
    print("=" * 50)
    print("🌱 AgroLens - Crop Disease Detection")
    print("=" * 50)
    
    # Check Ollama connection and model availability
    try:
        ollama_check = requests.get("http://localhost:11434/api/tags", timeout=3)
        if ollama_check.status_code == 200:
            print("✅ Ollama is running on http://localhost:11434")
            model_available, model_info = check_ollama_model("llava")
            if model_available:
                print(f"✅ llava model is available: {model_info}")
            else:
                print("⚠️  WARNING: 'llava' model is NOT installed!")
                print("   To install, run: ollama pull llava")
                print(f"   Available models: {', '.join(model_info) if isinstance(model_info, list) else 'None'}")
        else:
            print("⚠️  Ollama responded with an error")
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to Ollama!")
        print("   Please start Ollama: ollama serve")
    except Exception as e:
        print(f"⚠️  Could not check Ollama status: {e}")
    
    print("=" * 50)
    print("🚀 Starting Flask server...")
    print("📍 Server URL: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
