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
# 🔹 Multilingual Support (English & Kannada)
# ---------------------------------------------

TRANSLATIONS = {
    'en': {
        # Navigation
        'home': 'Home',
        'crop_recommendation': 'Crop Recommendation',
        'fertilizer': 'Fertilizer',
        'disease_detection': 'Disease Detection',
        'login': 'Login',
        
        # Disease Detection
        'disease_detected': 'Disease Detected',
        'crop_name': 'Crop Name',
        'symptoms_detected': 'Symptoms Detected',
        'confidence_level': 'Confidence Level',
        'treatment_recommendation': 'Treatment Recommendation',
        'no_flora_detected': 'No Flora Detected',
        'no_soil_detected': 'No Soil Detected',
        'healthy': 'Healthy',
        'low': 'Low',
        'medium': 'Medium',
        'high': 'High',
        
        # Soil Analysis
        'soil_type': 'Soil Type',
        'recommended_crops': 'Recommended Crops',
        'soil_analysis': 'Soil Analysis',
        'crop_recommendations': 'Crop Recommendations',
        
        # Fertilizer
        'fertilizer_recommendation': 'Fertilizer Recommendation',
        'crop_to_grow': 'Crop to Grow',
        'type_of_soil': 'Type of Soil',
        'water_availability': 'Water Availability Percentage',
        'what_fertilizer_to_use': 'What Fertilizer to Use',
        'simple_explanation': 'Simple Explanation',
        'how_to_use': 'How to Use',
        'when_to_use': 'When to Use',
        'about_your_soil': 'About Your Soil',
        
        # Common
        'upload_image': 'Upload Image',
        'analyze': 'Analyze',
        'select_image': 'Select Image',
        'back_to_home': 'Back to Home',
        'try_another': 'Try Another Image',
        'prediction_complete': 'Prediction Complete',
        'analysis_results': 'Analysis results for your uploaded image',
        'confidence_score': 'Confidence Score',
        'description': 'Description',
        'confidence': 'Confidence',
        'prediction_accuracy': 'Prediction Accuracy',
        'analysis': 'Analysis',
        'treatment_advice': 'Treatment Advice',
        'recommended_fertilizer': 'Recommended Fertilizer',
        'details': 'Details',
        'application_method': 'Application Method',
        'follow_application': 'Follow the application method carefully for best results',
        'analyze_another_image': 'Analyze Another Image',
        'quick_response': 'Quick Response',
        'early_detection_prevents': 'Early detection helps prevent disease spread',
        'accurate_diagnosis': 'Accurate Diagnosis',
        'ai_powered_analysis': 'AI-powered analysis with high precision',
        'expert_guidance': 'Expert Guidance',
        'personalized_treatment': 'Personalized treatment recommendations',
        'predicted_disease': 'Predicted Disease',
        'detect_disease': 'Detect Disease',
        'upload_plant_image': 'Upload Plant Image',
        'ai_will_analyze': 'Our AI will analyze your plant and identify any diseases',
        'select_plant_image': 'Select Plant Image',
        'upload_file': 'Upload File',
        'use_camera': 'Use Camera',
        'choose_image_file': 'Choose Image File',
        'image_preview': 'Image Preview',
        'start_camera': 'Start Camera',
        'capture_photo': 'Capture Photo',
        'stop_camera': 'Stop Camera',
        'retake': 'Retake',
        'what_we_detect': 'What We Detect',
        'best_practices': 'Best Practices',
        'use_clear_images': 'Use clear, well-lit images',
        'focus_on_leaves': 'Focus on affected leaves',
        'include_angles': 'Include multiple angles if possible',
        'ensure_quality': 'Ensure good image quality',
        'instant_results': 'Instant Results',
        'results_in_seconds': 'Get disease detection results in seconds, not days',
        'early_detection': 'Early Detection',
        'catch_diseases_early': 'Catch diseases early before they spread to your entire crop',
        'treatment_guide': 'Treatment Guide',
        'specific_recommendations': 'Receive specific treatment recommendations for each disease',
        'save_costs': 'Save Costs',
        'reduce_crop_loss': 'Reduce crop loss and minimize treatment expenses',
        'get_expert_recommendations': 'Get Expert Fertilizer Recommendations',
        'enter_crop_details': 'Enter your crop details and soil nutrient levels to receive personalized fertilizer recommendations for optimal growth.',
        'enter_crop_soil_info': 'Enter Crop & Soil Information',
        'select_crop_soil_water': 'Select your crop, soil type, and water availability for personalized fertilizer recommendations',
        'select_a_crop': 'Select a crop...',
        'select_soil_type': 'Select soil type...',
        'enter_water_availability': 'Enter water availability (0-100)',
        'enter_water_hint': 'Enter water availability percentage (0-100%)',
        'get_recommendations': 'Get Fertilizer Recommendations',
        'how_it_works': 'How It Works',
        'select_crop_type': 'Select your crop type from the dropdown',
        'select_soil_field': 'Select the type of soil in your field',
        'enter_water_percentage': 'Enter water availability percentage (0-100%)',
        'system_analyzes': 'Our system analyzes soil type and water availability for your crop',
        'receive_recommendations': 'Receive detailed fertilizer recommendations',
        'understanding_inputs': 'Understanding Inputs',
        'soil_type_explanation': 'Different soils have different nutrient retention and drainage properties',
        'water_availability_explanation': 'Affects fertilizer application timing and quantity',
        'crop_selection_explanation': 'Each crop has specific nutrient and water requirements',
        'optimized_growth': 'Optimized Growth',
        'right_nutrients': 'Get the right nutrients at the right time for maximum yield',
        'cost_effective': 'Cost Effective',
        'avoid_over_fertilization': 'Avoid over-fertilization and reduce unnecessary expenses',
        'healthy_crops': 'Healthy Crops',
        'optimal_nutrient_balance': 'Maintain optimal nutrient balance for robust plant health',
        'your_personalized_guide': 'Your Personalized Fertilizer Guide',
        'based_on_analysis': 'Based on your crop and soil analysis, here are our expert recommendations.',
        'get_another_recommendation': 'Get Another Recommendation',
        'always_follow_instructions': "Always follow manufacturer's instructions when applying fertilizers",
        'test_soil_regularly': 'Test your soil regularly to monitor nutrient levels',
        'consider_environmental': 'Consider environmental factors like weather and season',
        'apply_during_stages': 'Apply fertilizers during the recommended growth stages',
        'water_after_application': 'Water your crops after fertilizer application',
        'store_fertilizers': 'Store fertilizers in a cool, dry place',
        'use_organic_options': 'Use organic options when possible for sustainable farming',
        'detect_plant_diseases': 'Detect Plant Diseases Instantly',
        'upload_photo_description': 'Upload a photo of your plant leaves and get instant AI-powered disease detection with treatment recommendations',
        # Home Page
        'smart_agriculture': 'Smart Agriculture',
        'for_modern_farmers': 'for Modern Farmers',
        'harness_ai_power': 'Harness the power of AI to optimize your crops, detect diseases early, and maximize your yield with data-driven insights',
        'get_started': 'Get Started',
        'learn_more': 'Learn More',
        'our_services': 'Our Services',
        'everything_for_smart_farming': 'Everything You Need for Smart Farming',
        'comprehensive_ai_tools': 'Comprehensive AI-powered tools to help you make informed decisions and grow better crops',
        'crop_recommendation_desc': 'Get personalized crop recommendations based on your soil type, weather conditions, and location for optimal yield',
        'try_now': 'Try Now',
        'disease_detection_desc': 'Upload a photo of your plant leaves and instantly identify diseases with our advanced AI-powered detection system',
        'detect_now': 'Detect Now',
        'fertilizer_guide_desc': 'Receive expert fertilizer recommendations tailored to your crop\'s specific nutrient needs and soil conditions',
        'get_guide': 'Get Guide',
        'soil_analysis_desc': 'Analyze your soil type from images and get recommendations for the best crops suited for your land',
        'analyze_now': 'Analyze Now',
        'about_us': 'About Us',
        'empowering_farmers': 'Empowering Farmers with Technology',
        'about_description': 'At AgriTech, we believe in combining traditional farming wisdom with cutting-edge technology. Our mission is to help farmers make data-driven decisions that lead to better yields, reduced costs, and sustainable agricultural practices',
        'active_farmers': 'Active Farmers',
        'accuracy_rate': 'Accuracy Rate',
        'crop_types': 'Crop Types',
        'simple_process': 'Simple Process',
        'how_it_works_title': 'How It Works',
        'get_started_steps': 'Get started in three simple steps',
        'upload_data': 'Upload Data',
        'upload_data_desc': 'Upload images of your crops, soil, or enter your field parameters',
        'ai_analysis': 'AI Analysis',
        'ai_analysis_desc': 'Our advanced AI algorithms analyze your data in seconds',
        'get_results': 'Get Results',
        'get_results_desc': 'Receive detailed insights and actionable recommendations',
        'ready_to_transform': 'Ready to Transform Your Farming?',
        'join_thousands': 'Join thousands of farmers who are already using AgriTech to improve their yields and reduce costs',
        'sign_up_free': 'Sign Up Free',
        # Footer
        'quick_links': 'Quick Links',
        'fertilizer_guide': 'Fertilizer Guide',
        'services': 'Services',
        'soil_analysis': 'Soil Analysis',
        'weather_forecast': 'Weather Forecast',
        'crop_planning': 'Crop Planning',
        'expert_consultation': 'Expert Consultation',
        'contact': 'Contact',
        'all_rights_reserved': 'All rights reserved',
        'made_for_farmers': 'Made with love for farmers',
        'empowering_farmers_footer': 'Empowering farmers with AI-driven agriculture solutions for better yields and sustainable farming',
        # Crop Recommendation Page
        'find_perfect_crop': 'Find the Perfect Crop for Your Soil',
        'upload_soil_description': 'Upload a soil image or enter your field parameters to get AI-powered crop recommendations tailored to your land',
        'upload_soil_image': 'Upload Soil Image',
        'get_instant_recommendations': 'Get instant crop recommendations based on your soil type',
        'select_soil_image': 'Select Soil Image',
        'analyze_soil_get_recommendations': 'Analyze Soil & Get Recommendations',
        'upload_clear_soil_image': 'Upload a clear image of your soil',
        'ai_analyzes_soil': 'Our AI analyzes the soil type and composition',
        'get_personalized_crops': 'Get personalized crop recommendations',
        'view_detailed_info': 'View detailed information about each crop',
        'tips_for_best_results': 'Tips for Best Results',
        'tips_soil_image': 'Use good lighting, ensure the image is clear and focused, and include a representative sample of your soil',
        'soil_type_detection': 'Soil Type Detection',
        'identify_soil_types': 'Automatically identify alluvial, black, clay, and red soil types',
        'crop_matching': 'Crop Matching',
        'crops_for_soil': 'Get crops perfectly suited for your soil composition',
        'yield_optimization': 'Yield Optimization',
        'maximize_harvest': 'Maximize your harvest with data-driven recommendations',
    },
    'kn': {
        # Navigation
        'home': 'ಮುಖಪುಟ',
        'crop_recommendation': 'ಬೆಳೆ ಶಿಫಾರಸು',
        'fertilizer': 'ಗೊಬ್ಬರ',
        'disease_detection': 'ರೋಗ ಪತ್ತೆ',
        'login': 'ಲಾಗಿನ್',
        
        # Disease Detection
        'disease_detected': 'ರೋಗ ಪತ್ತೆಯಾಗಿದೆ',
        'crop_name': 'ಬೆಳೆಯ ಹೆಸರು',
        'symptoms_detected': 'ಪತ್ತೆಯಾದ ರೋಗಲಕ್ಷಣಗಳು',
        'confidence_level': 'ನಂಬಿಕೆಯ ಮಟ್ಟ',
        'treatment_recommendation': 'ಚಿಕಿತ್ಸೆಯ ಶಿಫಾರಸು',
        'no_flora_detected': 'ಯಾವುದೇ ಸಸ್ಯ ಕಂಡುಬಂದಿಲ್ಲ',
        'no_soil_detected': 'ಯಾವುದೇ ಮಣ್ಣು ಕಂಡುಬಂದಿಲ್ಲ',
        'healthy': 'ಆರೋಗ್ಯಕರ',
        'low': 'ಕಡಿಮೆ',
        'medium': 'ಮಧ್ಯಮ',
        'high': 'ಅಧಿಕ',
        
        # Soil Analysis
        'soil_type': 'ಮಣ್ಣಿನ ಪ್ರಕಾರ',
        'recommended_crops': 'ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳೆಗಳು',
        'soil_analysis': 'ಮಣ್ಣಿನ ವಿಶ್ಲೇಷಣೆ',
        'crop_recommendations': 'ಬೆಳೆ ಶಿಫಾರಸುಗಳು',
        
        # Fertilizer
        'fertilizer_recommendation': 'ಗೊಬ್ಬರ ಶಿಫಾರಸು',
        'crop_to_grow': 'ಬೆಳೆಯಬೇಕಾದ ಬೆಳೆ',
        'type_of_soil': 'ಮಣ್ಣಿನ ಪ್ರಕಾರ',
        'water_availability': 'ನೀರಿನ ಲಭ್ಯತೆ ಶೇಕಡಾವಾರು',
        'what_fertilizer_to_use': 'ಯಾವ ಗೊಬ್ಬರ ಬಳಸಬೇಕು',
        'simple_explanation': 'ಸರಳ ವಿವರಣೆ',
        'how_to_use': 'ಹೇಗೆ ಬಳಸುವುದು',
        'when_to_use': 'ಯಾವಾಗ ಬಳಸುವುದು',
        'about_your_soil': 'ನಿಮ್ಮ ಮಣ್ಣಿನ ಬಗ್ಗೆ',
        
        # Common
        'upload_image': 'ಚಿತ್ರವನ್ನು ಅಪ್ಲೋಡ್ ಮಾಡಿ',
        'analyze': 'ವಿಶ್ಲೇಷಿಸಿ',
        'select_image': 'ಚಿತ್ರವನ್ನು ಆಯ್ಕೆಮಾಡಿ',
        'back_to_home': 'ಮುಖಪುಟಕ್ಕೆ ಹಿಂತಿರುಗಿ',
        'try_another': 'ಮತ್ತೊಂದು ಚಿತ್ರವನ್ನು ಪ್ರಯತ್ನಿಸಿ',
        'prediction_complete': 'ಪ್ರಕ್ಷೇಪಣ ಪೂರ್ಣಗೊಂಡಿದೆ',
        'analysis_results': 'ನಿಮ್ಮ ಅಪ್ಲೋಡ್ ಮಾಡಿದ ಚಿತ್ರದ ವಿಶ್ಲೇಷಣೆ ಫಲಿತಾಂಶಗಳು',
        'confidence_score': 'ನಂಬಿಕೆಯ ಸ್ಕೋರ್',
        'description': 'ವಿವರಣೆ',
        'confidence': 'ನಂಬಿಕೆ',
        'prediction_accuracy': 'ಪ್ರಕ್ಷೇಪಣ ನಿಖರತೆ',
        'analysis': 'ವಿಶ್ಲೇಷಣೆ',
        'treatment_advice': 'ಚಿಕಿತ್ಸೆಯ ಸಲಹೆ',
        'recommended_fertilizer': 'ಶಿಫಾರಸು ಮಾಡಿದ ಗೊಬ್ಬರ',
        'details': 'ವಿವರಗಳು',
        'application_method': 'ಅನ್ವಯಿಕೆ ವಿಧಾನ',
        'follow_application': 'ಉತ್ತಮ ಫಲಿತಾಂಶಗಳಿಗಾಗಿ ಅನ್ವಯಿಕೆ ವಿಧಾನವನ್ನು ಎಚ್ಚರಿಕೆಯಿಂದ ಅನುಸರಿಸಿ',
        'analyze_another_image': 'ಮತ್ತೊಂದು ಚಿತ್ರವನ್ನು ವಿಶ್ಲೇಷಿಸಿ',
        'quick_response': 'ತ್ವರಿತ ಪ್ರತಿಕ್ರಿಯೆ',
        'early_detection_prevents': 'ಆರಂಭಿಕ ಪತ್ತೆಹಚ್ಚುವಿಕೆಯು ರೋಗದ ಹರಡುವಿಕೆಯನ್ನು ತಡೆಯಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ',
        'accurate_diagnosis': 'ನಿಖರ ರೋಗನಿರ್ಣಯ',
        'ai_powered_analysis': 'ಅಧಿಕ ನಿಖರತೆಯೊಂದಿಗೆ AI-ಚಾಲಿತ ವಿಶ್ಲೇಷಣೆ',
        'expert_guidance': 'ತಜ್ಞ ಮಾರ್ಗದರ್ಶನ',
        'personalized_treatment': 'ವೈಯಕ್ತಿಕ ಚಿಕಿತ್ಸೆಯ ಶಿಫಾರಸುಗಳು',
        'predicted_disease': 'ಪ್ರಕ್ಷೇಪಿಸಿದ ರೋಗ',
        'detect_disease': 'ರೋಗವನ್ನು ಪತ್ತೆಹಚ್ಚಿ',
        'upload_plant_image': 'ಸಸ್ಯದ ಚಿತ್ರವನ್ನು ಅಪ್ಲೋಡ್ ಮಾಡಿ',
        'ai_will_analyze': 'ನಮ್ಮ AI ನಿಮ್ಮ ಸಸ್ಯವನ್ನು ವಿಶ್ಲೇಷಿಸಿ ಮತ್ತು ಯಾವುದೇ ರೋಗಗಳನ್ನು ಗುರುತಿಸುತ್ತದೆ',
        'select_plant_image': 'ಸಸ್ಯದ ಚಿತ್ರವನ್ನು ಆಯ್ಕೆಮಾಡಿ',
        'upload_file': 'ಫೈಲ್ ಅಪ್ಲೋಡ್ ಮಾಡಿ',
        'use_camera': 'ಕ್ಯಾಮೆರಾ ಬಳಸಿ',
        'choose_image_file': 'ಚಿತ್ರ ಫೈಲ್ ಆಯ್ಕೆಮಾಡಿ',
        'image_preview': 'ಚಿತ್ರ ಪೂರ್ವವೀಕ್ಷಣೆ',
        'start_camera': 'ಕ್ಯಾಮೆರಾ ಪ್ರಾರಂಭಿಸಿ',
        'capture_photo': 'ಫೋಟೋ ತೆಗೆಯಿರಿ',
        'stop_camera': 'ಕ್ಯಾಮೆರಾ ನಿಲ್ಲಿಸಿ',
        'retake': 'ಮತ್ತೆ ತೆಗೆಯಿರಿ',
        'what_we_detect': 'ನಾವು ಏನನ್ನು ಪತ್ತೆಹಚ್ಚುತ್ತೇವೆ',
        'best_practices': 'ಉತ್ತಮ ಅಭ್ಯಾಸಗಳು',
        'use_clear_images': 'ಸ್ಪಷ್ಟ, ಚೆನ್ನಾಗಿ ಬೆಳಕಿನ ಚಿತ್ರಗಳನ್ನು ಬಳಸಿ',
        'focus_on_leaves': 'ಪ್ರಭಾವಿತ ಎಲೆಗಳ ಮೇಲೆ ಗಮನ ಕೇಂದ್ರೀಕರಿಸಿ',
        'include_angles': 'ಸಾಧ್ಯವಾದರೆ ಅನೇಕ ಕೋನಗಳನ್ನು ಸೇರಿಸಿ',
        'ensure_quality': 'ಉತ್ತಮ ಚಿತ್ರದ ಗುಣಮಟ್ಟವನ್ನು ಖಚಿತಪಡಿಸಿ',
        'instant_results': 'ತ್ವರಿತ ಫಲಿತಾಂಶಗಳು',
        'results_in_seconds': 'ರೋಗ ಪತ್ತೆಹಚ್ಚುವಿಕೆಯ ಫಲಿತಾಂಶಗಳನ್ನು ದಿನಗಳಲ್ಲಿ ಅಲ್ಲ, ಸೆಕೆಂಡುಗಳಲ್ಲಿ ಪಡೆಯಿರಿ',
        'early_detection': 'ಆರಂಭಿಕ ಪತ್ತೆಹಚ್ಚುವಿಕೆ',
        'catch_diseases_early': 'ನಿಮ್ಮ ಇಡೀ ಬೆಳೆಗೆ ಹರಡುವ ಮೊದಲು ರೋಗಗಳನ್ನು ಆರಂಭದಲ್ಲಿ ಹಿಡಿಯಿರಿ',
        'treatment_guide': 'ಚಿಕಿತ್ಸೆಯ ಮಾರ್ಗದರ್ಶಿ',
        'specific_recommendations': 'ಪ್ರತಿ ರೋಗಕ್ಕೆ ನಿರ್ದಿಷ್ಟ ಚಿಕಿತ್ಸೆಯ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಿರಿ',
        'save_costs': 'ವೆಚ್ಚವನ್ನು ಉಳಿಸಿ',
        'reduce_crop_loss': 'ಬೆಳೆಯ ನಷ್ಟವನ್ನು ಕಡಿಮೆ ಮಾಡಿ ಮತ್ತು ಚಿಕಿತ್ಸೆಯ ವೆಚ್ಚಗಳನ್ನು ಕನಿಷ್ಠಗೊಳಿಸಿ',
        'get_expert_recommendations': 'ತಜ್ಞ ಗೊಬ್ಬರ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಿರಿ',
        'enter_crop_details': 'ನಿಮ್ಮ ಬೆಳೆಯ ವಿವರಗಳು ಮತ್ತು ಮಣ್ಣಿನ ಪೋಷಕಾಂಶದ ಮಟ್ಟವನ್ನು ನಮೂದಿಸಿ ಮತ್ತು ಸೂಕ್ತ ಬೆಳವಣಿಗೆಗಾಗಿ ವೈಯಕ್ತಿಕ ಗೊಬ್ಬರ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಿರಿ.',
        'enter_crop_soil_info': 'ಬೆಳೆ ಮತ್ತು ಮಣ್ಣಿನ ಮಾಹಿತಿಯನ್ನು ನಮೂದಿಸಿ',
        'select_crop_soil_water': 'ವೈಯಕ್ತಿಕ ಗೊಬ್ಬರ ಶಿಫಾರಸುಗಳಿಗಾಗಿ ನಿಮ್ಮ ಬೆಳೆ, ಮಣ್ಣಿನ ಪ್ರಕಾರ ಮತ್ತು ನೀರಿನ ಲಭ್ಯತೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ',
        'select_a_crop': 'ಬೆಳೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ...',
        'select_soil_type': 'ಮಣ್ಣಿನ ಪ್ರಕಾರವನ್ನು ಆಯ್ಕೆಮಾಡಿ...',
        'enter_water_availability': 'ನೀರಿನ ಲಭ್ಯತೆಯನ್ನು ನಮೂದಿಸಿ (0-100)',
        'enter_water_hint': 'ನೀರಿನ ಲಭ್ಯತೆ ಶೇಕಡಾವಾರು ನಮೂದಿಸಿ (0-100%)',
        'get_recommendations': 'ಗೊಬ್ಬರ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಿರಿ',
        'how_it_works': 'ಇದು ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ',
        'select_crop_type': 'ಡ್ರಾಪ್ಡೌನ್ ನಿಂದ ನಿಮ್ಮ ಬೆಳೆಯ ಪ್ರಕಾರವನ್ನು ಆಯ್ಕೆಮಾಡಿ',
        'select_soil_field': 'ನಿಮ್ಮ ಕ್ಷೇತ್ರದಲ್ಲಿ ಮಣ್ಣಿನ ಪ್ರಕಾರವನ್ನು ಆಯ್ಕೆಮಾಡಿ',
        'enter_water_percentage': 'ನೀರಿನ ಲಭ್ಯತೆ ಶೇಕಡಾವಾರು ನಮೂದಿಸಿ (0-100%)',
        'system_analyzes': 'ನಮ್ಮ ವ್ಯವಸ್ಥೆಯು ನಿಮ್ಮ ಬೆಳೆಗಾಗಿ ಮಣ್ಣಿನ ಪ್ರಕಾರ ಮತ್ತು ನೀರಿನ ಲಭ್ಯತೆಯನ್ನು ವಿಶ್ಲೇಷಿಸುತ್ತದೆ',
        'receive_recommendations': 'ವಿವರವಾದ ಗೊಬ್ಬರ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಿರಿ',
        'understanding_inputs': 'ಇನ್ಪುಟ್ಗಳನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳುವುದು',
        'soil_type_explanation': 'ವಿಭಿನ್ನ ಮಣ್ಣುಗಳು ವಿಭಿನ್ನ ಪೋಷಕಾಂಶದ ಧಾರಣ ಮತ್ತು ಡ್ರೈನೇಜ್ ಗುಣಲಕ್ಷಣಗಳನ್ನು ಹೊಂದಿವೆ',
        'water_availability_explanation': 'ಗೊಬ್ಬರ ಅನ್ವಯಿಕೆಯ ಸಮಯ ಮತ್ತು ಪ್ರಮಾಣವನ್ನು ಪ್ರಭಾವಿಸುತ್ತದೆ',
        'crop_selection_explanation': 'ಪ್ರತಿ ಬೆಳೆಗೆ ನಿರ್ದಿಷ್ಟ ಪೋಷಕಾಂಶ ಮತ್ತು ನೀರಿನ ಅವಶ್ಯಕತೆಗಳಿವೆ',
        'optimized_growth': 'ಉತ್ತಮಗೊಳಿಸಿದ ಬೆಳವಣಿಗೆ',
        'right_nutrients': 'ಗರಿಷ್ಠ ಇಳುವರಿಗಾಗಿ ಸರಿಯಾದ ಸಮಯದಲ್ಲಿ ಸರಿಯಾದ ಪೋಷಕಾಂಶಗಳನ್ನು ಪಡೆಯಿರಿ',
        'cost_effective': 'ವೆಚ್ಚ-ಪರಿಣಾಮಕಾರಿ',
        'avoid_over_fertilization': 'ಅತಿಯಾದ ಗೊಬ್ಬರವನ್ನು ತಪ್ಪಿಸಿ ಮತ್ತು ಅನ必要ವಾದ ವೆಚ್ಚಗಳನ್ನು ಕಡಿಮೆ ಮಾಡಿ',
        'healthy_crops': 'ಆರೋಗ್ಯಕರ ಬೆಳೆಗಳು',
        'optimal_nutrient_balance': 'ಬಲವಾದ ಸಸ್ಯ ಆರೋಗ್ಯಕ್ಕಾಗಿ ಸೂಕ್ತ ಪೋಷಕಾಂಶದ ಸಮತೋಲನವನ್ನು ನಿರ್ವಹಿಸಿ',
        'your_personalized_guide': 'ನಿಮ್ಮ ವೈಯಕ್ತಿಕ ಗೊಬ್ಬರ ಮಾರ್ಗದರ್ಶಿ',
        'based_on_analysis': 'ನಿಮ್ಮ ಬೆಳೆ ಮತ್ತು ಮಣ್ಣಿನ ವಿಶ್ಲೇಷಣೆಯ ಆಧಾರದ ಮೇಲೆ, ಇಲ್ಲಿ ನಮ್ಮ ತಜ್ಞ ಶಿಫಾರಸುಗಳು.',
        'get_another_recommendation': 'ಮತ್ತೊಂದು ಶಿಫಾರಸನ್ನು ಪಡೆಯಿರಿ',
        'always_follow_instructions': 'ಗೊಬ್ಬರವನ್ನು ಅನ್ವಯಿಸುವಾಗ ಯಾವಾಗಲೂ ತಯಾರಕರ ಸೂಚನೆಗಳನ್ನು ಅನುಸರಿಸಿ',
        'test_soil_regularly': 'ಪೋಷಕಾಂಶದ ಮಟ್ಟವನ್ನು ಮೇಲ್ವಿಚಾರಣೆ ಮಾಡಲು ನಿಮ್ಮ ಮಣ್ಣನ್ನು ನಿಯಮಿತವಾಗಿ ಪರೀಕ್ಷಿಸಿ',
        'consider_environmental': 'ವಾತಾವರಣ ಮತ್ತು ಋತುವಿನಂತಹ ಪರಿಸರೀಯ ಅಂಶಗಳನ್ನು ಪರಿಗಣಿಸಿ',
        'apply_during_stages': 'ಶಿಫಾರಸು ಮಾಡಿದ ಬೆಳವಣಿಗೆಯ ಹಂತಗಳಲ್ಲಿ ಗೊಬ್ಬರವನ್ನು ಅನ್ವಯಿಸಿ',
        'water_after_application': 'ಗೊಬ್ಬರ ಅನ್ವಯಿಕೆಯ ನಂತರ ನಿಮ್ಮ ಬೆಳೆಗಳಿಗೆ ನೀರು ನೀಡಿ',
        'store_fertilizers': 'ಗೊಬ್ಬರವನ್ನು ತಂಪಾದ, ಶುಷ್ಕ ಸ್ಥಳದಲ್ಲಿ ಸಂಗ್ರಹಿಸಿ',
        'use_organic_options': 'ಸುಸ್ಥಿರ ಕೃಷಿಗಾಗಿ ಸಾಧ್ಯವಾದಾಗ ಸಾವಯವ ಆಯ್ಕೆಗಳನ್ನು ಬಳಸಿ',
        'detect_plant_diseases': 'ಸಸ್ಯ ರೋಗಗಳನ್ನು ತಕ್ಷಣ ಪತ್ತೆಹಚ್ಚಿ',
        'upload_photo_description': 'ನಿಮ್ಮ ಸಸ್ಯದ ಎಲೆಗಳ ಫೋಟೋವನ್ನು ಅಪ್ಲೋಡ್ ಮಾಡಿ ಮತ್ತು ಚಿಕಿತ್ಸೆಯ ಶಿಫಾರಸುಗಳೊಂದಿಗೆ ತಕ್ಷಣ AI-ಚಾಲಿತ ರೋಗ ಪತ್ತೆಹಚ್ಚುವಿಕೆಯನ್ನು ಪಡೆಯಿರಿ',
        # Home Page
        'smart_agriculture': 'ಸ್ಮಾರ್ಟ್ ಕೃಷಿ',
        'for_modern_farmers': 'ಆಧುನಿಕ ರೈತರಿಗಾಗಿ',
        'harness_ai_power': 'ನಿಮ್ಮ ಬೆಳೆಗಳನ್ನು ಉತ್ತಮಗೊಳಿಸಲು, ರೋಗಗಳನ್ನು ಆರಂಭದಲ್ಲಿ ಪತ್ತೆಹಚ್ಚಲು ಮತ್ತು ಡೇಟಾ-ಚಾಲಿತ ಒಳನೋಟಗಳೊಂದಿಗೆ ನಿಮ್ಮ ಇಳುವರಿಯನ್ನು ಗರಿಷ್ಠಗೊಳಿಸಲು AI ಶಕ್ತಿಯನ್ನು ಬಳಸಿ',
        'get_started': 'ಪ್ರಾರಂಭಿಸಿ',
        'learn_more': 'ಹೆಚ್ಚು ತಿಳಿಯಿರಿ',
        'our_services': 'ನಮ್ಮ ಸೇವೆಗಳು',
        'everything_for_smart_farming': 'ಸ್ಮಾರ್ಟ್ ಕೃಷಿಗಾಗಿ ನಿಮಗೆ ಬೇಕಾದ ಎಲ್ಲವೂ',
        'comprehensive_ai_tools': 'ನಿಮ್ಮನ್ನು ಸೂಕ್ತ ನಿರ್ಧಾರಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳಲು ಮತ್ತು ಉತ್ತಮ ಬೆಳೆಗಳನ್ನು ಬೆಳೆಯಲು ಸಹಾಯ ಮಾಡಲು ಸಮಗ್ರ AI-ಚಾಲಿತ ಉಪಕರಣಗಳು',
        'crop_recommendation_desc': 'ಸೂಕ್ತ ಇಳುವರಿಗಾಗಿ ನಿಮ್ಮ ಮಣ್ಣಿನ ಪ್ರಕಾರ, ಹವಾಮಾನ ಪರಿಸ್ಥಿತಿಗಳು ಮತ್ತು ಸ್ಥಳದ ಆಧಾರದ ಮೇಲೆ ವೈಯಕ್ತಿಕ ಬೆಳೆ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಿರಿ',
        'try_now': 'ಈಗ ಪ್ರಯತ್ನಿಸಿ',
        'disease_detection_desc': 'ನಿಮ್ಮ ಸಸ್ಯದ ಎಲೆಗಳ ಫೋಟೋವನ್ನು ಅಪ್ಲೋಡ್ ಮಾಡಿ ಮತ್ತು ನಮ್ಮ ಸುಧಾರಿತ AI-ಚಾಲಿತ ಪತ್ತೆಹಚ್ಚುವಿಕೆಯ ವ್ಯವಸ್ಥೆಯೊಂದಿಗೆ ತಕ್ಷಣ ರೋಗಗಳನ್ನು ಗುರುತಿಸಿ',
        'detect_now': 'ಈಗ ಪತ್ತೆಹಚ್ಚಿ',
        'fertilizer_guide_desc': 'ನಿಮ್ಮ ಬೆಳೆಯ ನಿರ್ದಿಷ್ಟ ಪೋಷಕಾಂಶದ ಅವಶ್ಯಕತೆಗಳು ಮತ್ತು ಮಣ್ಣಿನ ಪರಿಸ್ಥಿತಿಗಳಿಗೆ ಹೊಂದಿಕೊಂಡ ತಜ್ಞ ಗೊಬ್ಬರ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಿರಿ',
        'get_guide': 'ಮಾರ್ಗದರ್ಶಿ ಪಡೆಯಿರಿ',
        'soil_analysis_desc': 'ಚಿತ್ರಗಳಿಂದ ನಿಮ್ಮ ಮಣ್ಣಿನ ಪ್ರಕಾರವನ್ನು ವಿಶ್ಲೇಷಿಸಿ ಮತ್ತು ನಿಮ್ಮ ಭೂಮಿಗೆ ಸೂಕ್ತವಾದ ಅತ್ಯುತ್ತಮ ಬೆಳೆಗಳಿಗೆ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಿರಿ',
        'analyze_now': 'ಈಗ ವಿಶ್ಲೇಷಿಸಿ',
        'about_us': 'ನಮ್ಮ ಬಗ್ಗೆ',
        'empowering_farmers': 'ತಂತ್ರಜ್ಞಾನದೊಂದಿಗೆ ರೈತರನ್ನು ಶಕ್ತೀಕರಿಸುವುದು',
        'about_description': 'AgriTech ನಲ್ಲಿ, ನಾವು ಸಾಂಪ್ರದಾಯಿಕ ಕೃಷಿ ಬುದ್ಧಿವಂತಿಕೆಯನ್ನು ಅತ್ಯಾಧುನಿಕ ತಂತ್ರಜ್ಞಾನದೊಂದಿಗೆ ಸಂಯೋಜಿಸುವಲ್ಲಿ ನಂಬಿಕೆ ಇಡುತ್ತೇವೆ. ಉತ್ತಮ ಇಳುವರಿ, ಕಡಿಮೆ ವೆಚ್ಚ ಮತ್ತು ಸುಸ್ಥಿರ ಕೃಷಿ ಅಭ್ಯಾಸಗಳಿಗೆ ಕಾರಣವಾಗುವ ಡೇಟಾ-ಚಾಲಿತ ನಿರ್ಧಾರಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳಲು ರೈತರಿಗೆ ಸಹಾಯ ಮಾಡುವುದು ನಮ್ಮ ಧ್ಯೇಯವಾಗಿದೆ',
        'active_farmers': 'ಸಕ್ರಿಯ ರೈತರು',
        'accuracy_rate': 'ನಿಖರತೆಯ ದರ',
        'crop_types': 'ಬೆಳೆಯ ಪ್ರಕಾರಗಳು',
        'simple_process': 'ಸರಳ ಪ್ರಕ್ರಿಯೆ',
        'how_it_works_title': 'ಇದು ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ',
        'get_started_steps': 'ಮೂರು ಸರಳ ಹಂತಗಳಲ್ಲಿ ಪ್ರಾರಂಭಿಸಿ',
        'upload_data': 'ಡೇಟಾ ಅಪ್ಲೋಡ್ ಮಾಡಿ',
        'upload_data_desc': 'ನಿಮ್ಮ ಬೆಳೆಗಳ, ಮಣ್ಣಿನ ಚಿತ್ರಗಳನ್ನು ಅಪ್ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ನಿಮ್ಮ ಕ್ಷೇತ್ರದ ನಿಯತಾಂಕಗಳನ್ನು ನಮೂದಿಸಿ',
        'ai_analysis': 'AI ವಿಶ್ಲೇಷಣೆ',
        'ai_analysis_desc': 'ನಮ್ಮ ಸುಧಾರಿತ AI ಅಲ್ಗಾರಿದಮ್ಗಳು ಸೆಕೆಂಡುಗಳಲ್ಲಿ ನಿಮ್ಮ ಡೇಟಾವನ್ನು ವಿಶ್ಲೇಷಿಸುತ್ತವೆ',
        'get_results': 'ಫಲಿತಾಂಶಗಳನ್ನು ಪಡೆಯಿರಿ',
        'get_results_desc': 'ವಿವರವಾದ ಒಳನೋಟಗಳು ಮತ್ತು ಕ್ರಿಯಾತ್ಮಕ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಿರಿ',
        'ready_to_transform': 'ನಿಮ್ಮ ಕೃಷಿಯನ್ನು ರೂಪಾಂತರಿಸಲು ಸಿದ್ಧರಿದ್ದೀರಾ?',
        'join_thousands': 'ತಮ್ಮ ಇಳುವರಿಯನ್ನು ಸುಧಾರಿಸಲು ಮತ್ತು ವೆಚ್ಚವನ್ನು ಕಡಿಮೆ ಮಾಡಲು ಈಗಾಗಲೇ AgriTech ಅನ್ನು ಬಳಸುತ್ತಿರುವ ಸಾವಿರಾರು ರೈತರೊಂದಿಗೆ ಸೇರಿ',
        'sign_up_free': 'ಉಚಿತವಾಗಿ ಸೈನ್ ಅಪ್ ಮಾಡಿ',
        # Footer
        'quick_links': 'ತ್ವರಿತ ಲಿಂಕ್ಗಳು',
        'fertilizer_guide': 'ಗೊಬ್ಬರ ಮಾರ್ಗದರ್ಶಿ',
        'services': 'ಸೇವೆಗಳು',
        'soil_analysis': 'ಮಣ್ಣಿನ ವಿಶ್ಲೇಷಣೆ',
        'weather_forecast': 'ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ',
        'crop_planning': 'ಬೆಳೆ ಯೋಜನೆ',
        'expert_consultation': 'ತಜ್ಞ ಸಲಹೆ',
        'contact': 'ಸಂಪರ್ಕ',
        'all_rights_reserved': 'ಎಲ್ಲ ಹಕ್ಕುಗಳನ್ನು ಕಾಯ್ದಿರಿಸಲಾಗಿದೆ',
        'made_for_farmers': 'ರೈತರಿಗಾಗಿ ಪ್ರೀತಿಯೊಂದಿಗೆ ಮಾಡಲಾಗಿದೆ',
        'empowering_farmers_footer': 'ಉತ್ತಮ ಇಳುವರಿ ಮತ್ತು ಸುಸ್ಥಿರ ಕೃಷಿಗಾಗಿ AI-ಚಾಲಿತ ಕೃಷಿ ಪರಿಹಾರಗಳೊಂದಿಗೆ ರೈತರನ್ನು ಶಕ್ತೀಕರಿಸುವುದು',
        # Crop Recommendation Page
        'find_perfect_crop': 'ನಿಮ್ಮ ಮಣ್ಣಿಗೆ ಸೂಕ್ತವಾದ ಬೆಳೆಯನ್ನು ಹುಡುಕಿ',
        'upload_soil_description': 'ನಿಮ್ಮ ಭೂಮಿಗೆ ಹೊಂದಿಕೊಂಡ AI-ಚಾಲಿತ ಬೆಳೆ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಲು ಮಣ್ಣಿನ ಚಿತ್ರವನ್ನು ಅಪ್ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ನಿಮ್ಮ ಕ್ಷೇತ್ರದ ನಿಯತಾಂಕಗಳನ್ನು ನಮೂದಿಸಿ',
        'upload_soil_image': 'ಮಣ್ಣಿನ ಚಿತ್ರವನ್ನು ಅಪ್ಲೋಡ್ ಮಾಡಿ',
        'get_instant_recommendations': 'ನಿಮ್ಮ ಮಣ್ಣಿನ ಪ್ರಕಾರದ ಆಧಾರದ ಮೇಲೆ ತಕ್ಷಣ ಬೆಳೆ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಿರಿ',
        'select_soil_image': 'ಮಣ್ಣಿನ ಚಿತ್ರವನ್ನು ಆಯ್ಕೆಮಾಡಿ',
        'analyze_soil_get_recommendations': 'ಮಣ್ಣನ್ನು ವಿಶ್ಲೇಷಿಸಿ ಮತ್ತು ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಿರಿ',
        'upload_clear_soil_image': 'ನಿಮ್ಮ ಮಣ್ಣಿನ ಸ್ಪಷ್ಟ ಚಿತ್ರವನ್ನು ಅಪ್ಲೋಡ್ ಮಾಡಿ',
        'ai_analyzes_soil': 'ನಮ್ಮ AI ಮಣ್ಣಿನ ಪ್ರಕಾರ ಮತ್ತು ಸಂಯೋಜನೆಯನ್ನು ವಿಶ್ಲೇಷಿಸುತ್ತದೆ',
        'get_personalized_crops': 'ವೈಯಕ್ತಿಕ ಬೆಳೆ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಿರಿ',
        'view_detailed_info': 'ಪ್ರತಿ ಬೆಳೆಯ ಬಗ್ಗೆ ವಿವರವಾದ ಮಾಹಿತಿಯನ್ನು ವೀಕ್ಷಿಸಿ',
        'tips_for_best_results': 'ಉತ್ತಮ ಫಲಿತಾಂಶಗಳಿಗಾಗಿ ಸಲಹೆಗಳು',
        'tips_soil_image': 'ಉತ್ತಮ ಬೆಳಕನ್ನು ಬಳಸಿ, ಚಿತ್ರವು ಸ್ಪಷ್ಟ ಮತ್ತು ಕೇಂದ್ರೀಕೃತವಾಗಿದೆ ಎಂದು ಖಚಿತಪಡಿಸಿ ಮತ್ತು ನಿಮ್ಮ ಮಣ್ಣಿನ ಪ್ರತಿನಿಧಿ ಮಾದರಿಯನ್ನು ಸೇರಿಸಿ',
        'soil_type_detection': 'ಮಣ್ಣಿನ ಪ್ರಕಾರ ಪತ್ತೆಹಚ್ಚುವಿಕೆ',
        'identify_soil_types': 'ಸ್ವಯಂಚಾಲಿತವಾಗಿ ಅಲ್ಯುವಿಯಲ್, ಕಪ್ಪು, ಜೇಡಿ ಮತ್ತು ಕೆಂಪು ಮಣ್ಣಿನ ಪ್ರಕಾರಗಳನ್ನು ಗುರುತಿಸಿ',
        'crop_matching': 'ಬೆಳೆ ಹೊಂದಾಣಿಕೆ',
        'crops_for_soil': 'ನಿಮ್ಮ ಮಣ್ಣಿನ ಸಂಯೋಜನೆಗೆ ಸೂಕ್ತವಾದ ಬೆಳೆಗಳನ್ನು ಪಡೆಯಿರಿ',
        'yield_optimization': 'ಇಳುವರಿ ಉತ್ತಮಗೊಳಿಸುವಿಕೆ',
        'maximize_harvest': 'ಡೇಟಾ-ಚಾಲಿತ ಶಿಫಾರಸುಗಳೊಂದಿಗೆ ನಿಮ್ಮ ಕೊಯ್ಲನ್ನು ಗರಿಷ್ಠಗೊಳಿಸಿ',
    }
}

def get_language():
    """Get current language from session, default to English."""
    return session.get('language', 'en')

def translate(key, lang=None):
    """Translate a key to the specified language or current session language."""
    if lang is None:
        lang = get_language()
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

def get_translations(lang=None):
    """Get all translations for a language."""
    if lang is None:
        lang = get_language()
    return TRANSLATIONS.get(lang, TRANSLATIONS['en'])

# Make translate function available to templates
app.jinja_env.globals['translate'] = translate
app.jinja_env.globals['get_translations'] = get_translations
app.jinja_env.globals['get_language'] = get_language

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

        # Get current language
        lang = get_language()
        lang_instruction = ""
        if lang == 'kn':
            lang_instruction = " IMPORTANT: Respond in Kannada (ಕನ್ನಡ) language. All text in the JSON response should be in Kannada script."

        # Enhanced Prompt for Ollama - expert agricultural assistant format with improved accuracy
        prompt = (
            "You are an expert agricultural pathologist with 20+ years of experience in plant disease diagnosis. "
            "Analyze the given image with EXTREME CARE and ACCURACY.\n\n"
            
            "=== STEP 1: FLORA DETECTION (CRITICAL) ===\n"
            "First, determine if this image contains ANY FLORA (plants, crops, vegetation):\n"
            "- Look for: plants, crops, trees, shrubs, leaves, stems, flowers, fruits, agricultural vegetation\n"
            "- Be VERY CAREFUL: Only set flora_detected=false if there are ABSOLUTELY NO plants visible\n"
            "- If you see ANY plant parts (even partially visible), flora_detected MUST be true\n"
            "- Examples of NO FLORA: only soil, animals, objects, people, buildings, sky, vehicles, tools\n"
            "- Examples of FLORA PRESENT: any leaves, stems, fruits, flowers, or plant parts\n\n"
            
            "=== STEP 2: CROP IDENTIFICATION (CRITICAL - MUST BE ACCURATE) ===\n"
            "If flora is detected, FIRST identify the crop/plant type ACCURATELY:\n\n"
            "A. EXAMINE LEAF CHARACTERISTICS:\n"
            "   - Leaf shape: long and narrow (wheat, rice, corn), broad and round (tomato, potato), oval (apple), heart-shaped (grape), etc.\n"
            "   - Leaf texture: smooth, rough, waxy, hairy, glossy\n"
            "   - Leaf color: green shades, yellow, brown, red\n"
            "   - Leaf size: small, medium, large\n"
            "   - Leaf arrangement: single, compound, alternate, opposite\n"
            "   - Leaf margins: smooth, serrated, lobed, toothed\n\n"
            
            "B. EXAMINE PLANT CHARACTERISTICS:\n"
            "   - Stem type: woody, herbaceous, climbing, upright\n"
            "   - Plant structure: grass-like (wheat, rice, corn), bushy (tomato, pepper), tree-like (apple, mango), vine (grape, cucumber)\n"
            "   - Overall appearance: cereal crop, vegetable, fruit tree, legume, etc.\n\n"
            
            "C. CROP IDENTIFICATION GUIDELINES:\n"
            "   - WHEAT: Long, narrow, linear leaves with parallel veins, grass-like appearance, typically green to yellow-green\n"
            "   - RICE: Similar to wheat but often in water, long narrow leaves, grass-like\n"
            "   - CORN/MAIZE: Very long, broad leaves with prominent midrib, grass-like but larger\n"
            "   - TOMATO: Broad, lobed leaves with serrated edges, compound leaves, distinctive tomato plant structure\n"
            "   - POTATO: Compound leaves with multiple leaflets, distinctive potato plant appearance\n"
            "   - APPLE: Oval to elliptical leaves, serrated margins, tree-like structure\n"
            "   - MANGO: Lanceolate leaves, glossy, tree-like structure\n"
            "   - GRAPE: Heart-shaped or lobed leaves, vine structure\n"
            "   - PEPPER: Similar to tomato but smaller leaves, bushy structure\n"
            "   - COTTON: Broad, lobed leaves, distinctive cotton plant appearance\n"
            "   - SUGARCANE: Very long, narrow leaves, grass-like but very tall\n"
            "   - BANANA: Very large, broad leaves, distinctive banana plant structure\n"
            "   - COCONUT: Long, pinnate leaves, palm tree structure\n"
            "   - ORANGE: Oval, glossy leaves, citrus tree structure\n"
            "   - POMEGRANATE: Small, glossy, oval leaves, shrub-like structure\n\n"
            
            "D. ACCURACY REQUIREMENTS:\n"
            "   - Look at the ACTUAL image content, not assumptions\n"
            "   - If you see wheat leaves (long, narrow, grass-like), crop_name MUST be 'Wheat'\n"
            "   - If you see tomato leaves (broad, lobed, compound), crop_name MUST be 'Tomato'\n"
            "   - If you see potato leaves (compound with leaflets), crop_name MUST be 'Potato'\n"
            "   - If uncertain about crop type, use 'Unknown' - DO NOT GUESS\n"
            "   - Be SPECIFIC: 'Wheat' not 'Grain', 'Tomato' not 'Vegetable', 'Apple' not 'Fruit'\n\n"
            
            "=== STEP 3: DISEASE ANALYSIS (Only after accurate crop identification) ===\n"
            "After identifying the crop correctly, perform DETAILED disease analysis:\n\n"
            
            "A. VISUAL SYMPTOM IDENTIFICATION:\n"
            "   - Examine the image carefully for disease symptoms\n"
            "   - Look for: black/brown spots, yellowing, wilting, fungal growth, white powder, holes, discoloration, lesions, blisters\n"
            "   - Note the pattern: scattered spots, concentrated areas, edge damage, center damage, entire leaf affected\n"
            "   - Check color changes: yellowing, browning, blackening, whitening\n"
            "   - Observe texture: powdery, fuzzy, slimy, dry, wet\n\n"
            
            "B. DISEASE IDENTIFICATION:\n"
            "   - Identify the SPECIFIC disease name if possible (e.g., 'Early Blight', 'Late Blight', 'Leaf Spot', 'Rust', 'Powdery Mildew', 'Downy Mildew', 'Anthracnose', 'Bacterial Spot')\n"
            "   - Consider the CROP TYPE when identifying disease (wheat diseases are different from tomato diseases)\n"
            "   - Wheat diseases: Rust, Powdery Mildew, Leaf Blight, Septoria, Fusarium\n"
            "   - Tomato diseases: Early Blight, Late Blight, Leaf Spot, Bacterial Spot, Powdery Mildew\n"
            "   - Potato diseases: Late Blight, Early Blight, Scab, Blackleg\n"
            "   - If symptoms are unclear, use 'Unknown Disease' with Low confidence\n"
            "   - If plant appears healthy (no symptoms), disease_name = 'Healthy'\n"
            "   - Be SPECIFIC: 'Wheat Rust' or 'Tomato Early Blight' - include crop name in disease if helpful\n"
            "   - DO NOT confuse diseases from different crops\n\n"
            
            "C. CONFIDENCE ASSESSMENT:\n"
            "   - High: Clear, distinct symptoms matching known disease patterns\n"
            "   - Medium: Symptoms visible but not perfectly matching known patterns\n"
            "   - Low: Unclear symptoms or ambiguous signs\n"
            "   - If healthy: Always High confidence\n\n"
            
            "D. SYMPTOM LISTING:\n"
            "   - List ALL visible symptoms in detail\n"
            "   - Be specific: 'Black circular spots with yellow halos' not just 'spots'\n"
            "   - Include location: 'Yellowing on lower leaves', 'Brown spots on leaf edges'\n\n"
            
            "E. TREATMENT RECOMMENDATION:\n"
            "   - Provide ACTIONABLE, PRACTICAL advice for farmers\n"
            "   - Include: specific treatment methods, timing, frequency\n"
            "   - Mention: organic/natural remedies if applicable\n"
            "   - Consider: prevention measures for future\n"
            "   - Use simple language farmers can understand\n\n"
            
            "F. DISEASE LOCATION:\n"
            "   - Describe WHERE the disease appears: 'center of leaf', 'top-left', 'bottom-right', 'entire leaf', 'leaf edges', 'stem base', etc.\n"
            "   - Be specific about location for accurate highlighting\n"
            "   - If healthy: use 'none'\n\n"
            
            "=== CRITICAL RULES ===\n"
            "1. CROP IDENTIFICATION MUST BE ACCURATE - Look at the actual image, not assumptions\n"
            "2. If you see wheat leaves (long, narrow, grass-like), crop_name MUST be 'Wheat' - NOT 'Tomato'\n"
            "3. If you see tomato leaves (broad, lobed), crop_name MUST be 'Tomato' - NOT 'Wheat'\n"
            "4. If disease_name is NOT 'No Flora Detected' or 'Unknown', then flora_detected MUST be true\n"
            "5. If disease_name is 'Healthy', flora_detected MUST be true\n"
            "6. Only set flora_detected=false if image contains ZERO plants\n"
            "7. If flora_detected=false, disease_name MUST be 'No Flora Detected'\n"
            "8. Be ACCURATE: Don't guess crops or diseases - use 'Unknown' if uncertain\n"
            "9. Confidence should reflect certainty: High only for clear cases\n"
            "10. CROP IDENTIFICATION IS CRITICAL - Wrong crop = Wrong disease identification\n\n"
            
            f"{lang_instruction}\n\n"
            
            "=== OUTPUT FORMAT ===\n"
            "Output ONLY valid JSON (no markdown, no explanations, just JSON):\n"
            '{\n'
            '  "flora_detected": true/false,\n'
            '  "crop_name": "ACCURATE crop name based on actual image (e.g., Wheat, Rice, Corn, Tomato, Potato, Apple, Mango, Grape, Pepper, Cotton, Sugarcane, Banana, Coconut, Orange, Pomegranate) or unknown if uncertain",\n'
            '  "disease_name": "specific disease name matching the identified crop (e.g., Wheat Rust, Tomato Early Blight, Potato Late Blight, Leaf Spot, Powdery Mildew) or healthy or unknown",\n'
            '  "symptoms_detected": ["detailed symptom 1", "detailed symptom 2", "detailed symptom 3"],\n'
            '  "confidence_level": "Low/Medium/High",\n'
            '  "treatment_tip": "detailed, actionable treatment recommendation in 2-3 sentences specific to the identified crop and disease",\n'
            '  "disease_location": "specific location description (e.g., center of leaf, top-left corner, entire leaf, leaf edges, stem base, or none if healthy)"\n'
            '}\n\n'
            
            "REMEMBER:\n"
            "- CROP IDENTIFICATION IS CRITICAL - Identify the crop FIRST by examining leaf shape, texture, and plant structure\n"
            "- If you see wheat leaves, crop_name MUST be 'Wheat' - do NOT say 'Tomato'\n"
            "- If you see tomato leaves, crop_name MUST be 'Tomato' - do NOT say 'Wheat'\n"
            "- Accuracy is critical. If uncertain about crop, use 'Unknown' with Low confidence rather than guessing.\n"
            "- Wrong crop identification leads to wrong disease identification."
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
                
                # Extract new format fields first
                disease_name = result_json.get('disease_name', 'Unknown').strip()
                symptoms = result_json.get('symptoms_detected', [])
                confidence_level = result_json.get('confidence_level', 'Medium')
                treatment_tip = result_json.get('treatment_tip', 'No treatment recommendation available.').strip()
                disease_location = result_json.get('disease_location', 'center').strip()
                crop_name = result_json.get('crop_name', 'Unknown').strip()
                
                # Validate and normalize crop_name - ensure it's accurate
                valid_crops = [
                    'Wheat', 'Rice', 'Corn', 'Maize', 'Tomato', 'Potato', 'Apple', 'Mango',
                    'Grape', 'Pepper', 'Cherry', 'Banana', 'Coconut', 'Orange', 'Pomegranate',
                    'Cotton', 'Sugarcane', 'Cucumber', 'Pumpkin', 'Watermelon', 'Muskmelon',
                    'Chickpea', 'Kidneybeans', 'Pigeonpeas', 'Mothbeans', 'Mungbean', 'Blackgram', 'Lentil'
                ]
                
                # Normalize crop name (capitalize first letter, handle variations)
                if crop_name and crop_name.lower() != 'unknown':
                    crop_name_normalized = crop_name.strip().capitalize()
                    crop_lower = crop_name.lower().strip()
                    
                    # Check for exact match or close match in valid crops
                    matched = False
                    for valid_crop in valid_crops:
                        if valid_crop.lower() == crop_lower:
                            crop_name = valid_crop
                            matched = True
                            print(f"[CROP VALIDATION] Validated crop: {crop_name}")
                            break
                        # Check for partial matches (e.g., "wheat leaf" -> "Wheat")
                        elif crop_lower in valid_crop.lower() or valid_crop.lower() in crop_lower:
                            crop_name = valid_crop
                            matched = True
                            print(f"[CROP VALIDATION] Matched crop: {crop_name} (from '{crop_name_normalized}')")
                            break
                    
                    if not matched:
                        # If not found in valid crops but not 'unknown', keep it but log warning
                        print(f"[CROP VALIDATION] Warning: Crop name '{crop_name}' not in standard list, keeping as is")
                        crop_name = crop_name_normalized
                    
                    # Additional validation: Check if crop name makes sense with disease
                    # Log if there's a mismatch (e.g., wheat disease but crop is tomato)
                    if disease_name and disease_name.lower() not in ['healthy', 'unknown', 'no flora detected']:
                        print(f"[CROP VALIDATION] Crop: {crop_name}, Disease: {disease_name}")
                else:
                    crop_name = 'Unknown'
                    print(f"[CROP VALIDATION] Crop name not provided, using 'Unknown'")
                
                # Check if flora was detected - prioritize explicit flora_detected flag
                flora_detected = result_json.get('flora_detected', True)  # Default to True for backward compatibility
                
                # Get disease name and check
                disease_lower = disease_name.lower() if disease_name else ''
                
                # VALIDATION: Ensure logical consistency
                # Rule 1: If disease is detected (not "No Flora Detected", "Unknown", or empty), flora MUST be present
                if disease_lower not in ['no flora detected', 'unknown', '', 'healthy'] and disease_lower:
                    flora_detected = True  # Force flora_detected to true if disease is detected
                
                # Rule 2: If disease_name explicitly says "No Flora Detected", override flora_detected
                if disease_lower == 'no flora detected':
                    flora_detected = False
                
                # Rule 3: If disease is "Healthy", flora MUST be present
                if disease_lower == 'healthy':
                    flora_detected = True
                
                # Rule 4: If flora_detected is false, disease_name should be "No Flora Detected"
                if not flora_detected:
                    disease_name = 'No Flora Detected'
                    disease_lower = 'no flora detected'
                
                # Only show "no flora" if explicitly stated and validated
                if not flora_detected or disease_lower == 'no flora detected':
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
                
                # Convert confidence level to numeric score for display
                confidence_map = {'Low': 0.6, 'Medium': 0.75, 'High': 0.9}
                confidence_score = confidence_map.get(confidence_level, 0.75)
                
                # Validate and clean symptoms list
                if not symptoms or not isinstance(symptoms, list):
                    symptoms = ['Symptoms detected' if disease_lower not in ['healthy', 'no flora detected'] else '']
                else:
                    # Filter out empty strings and ensure all are strings
                    symptoms = [str(s).strip() for s in symptoms if s and str(s).strip()]
                    if not symptoms and disease_lower not in ['healthy', 'no flora detected']:
                        symptoms = ['Symptoms detected']
                
                # Format description with symptoms
                if symptoms and disease_lower not in ['healthy', 'no flora detected']:
                    description = f"Symptoms: {', '.join(symptoms)}"
                elif disease_lower == 'healthy':
                    description = "The plant appears healthy with no visible disease symptoms."
                else:
                    description = f"Analysis complete. {disease_name} detected."
                
                # Format the result to match template expectations
                if crop_name and crop_name.lower() != 'unknown':
                    disease_label = f"{crop_name} - {disease_name}"
                else:
                    disease_label = disease_name
                
                return {
                    'label': disease_label,
                    'score': confidence_score,
                    'crop_name': crop_name if crop_name and crop_name.lower() != 'unknown' else 'Unknown Crop',
                    'disease_name': disease_name,
                    'description': description,
                    'treatment_tip': treatment_tip if treatment_tip else 'Please consult with an agricultural expert for specific treatment recommendations.',
                    'disease_location': disease_location if disease_location else 'center',
                    'symptoms_detected': symptoms,
                    'confidence_level': confidence_level,
                    'no_flora': False
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, extract information from text
                print("Failed to parse JSON, extracting from text...")
                parsed_result = parse_text_response(response_text)
                
                # Enhanced validation: Double-check flora detection from text
                response_lower = response_text.lower()
                
                # Check for explicit "no flora" statements
                explicit_no_flora_phrases = [
                    "no flora detected", "no plant detected", "no crop detected",
                    "no vegetation detected", "does not contain flora", "does not contain plants",
                    "no flora found", "no plants found", "no crops found"
                ]
                
                has_explicit_no_flora = any(phrase in response_lower for phrase in explicit_no_flora_phrases)
                
                # Check for disease/plant indicators
                has_plant_indicators = any(keyword in response_lower for keyword in [
                    "disease", "blight", "rust", "spot", "mildew", "leaf", "plant", "crop",
                    "symptom", "healthy", "tomato", "potato", "apple", "corn", "pepper"
                ])
                
                # Only set no_flora if explicitly stated AND no plant indicators
                if has_explicit_no_flora and not has_plant_indicators:
                    parsed_result['no_flora'] = True
                    parsed_result['disease_name'] = 'No Flora Detected'
                    parsed_result['crop_name'] = 'No Flora'
                # If disease/plant indicators are present, ensure no_flora is False
                elif has_plant_indicators:
                    parsed_result['no_flora'] = False
                    # Ensure disease_name is not "No Flora Detected" if plants are present
                    if parsed_result.get('disease_name', '').lower() == 'no flora detected':
                        parsed_result['disease_name'] = 'Unknown'
                        parsed_result['confidence_level'] = 'Low'
                
                # Validate and clean the parsed result
                if not parsed_result.get('symptoms_detected') or not isinstance(parsed_result.get('symptoms_detected'), list):
                    if parsed_result.get('disease_name', '').lower() not in ['healthy', 'no flora detected']:
                        parsed_result['symptoms_detected'] = ['Symptoms detected']
                    else:
                        parsed_result['symptoms_detected'] = []
                
                return parsed_result
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
    """Parse text response when JSON parsing fails - Enhanced for accuracy."""
    text_lower = text.lower()
    
    # Enhanced disease/plant indicators - more comprehensive
    has_disease_indicators = any(keyword in text_lower for keyword in [
        "disease", "blight", "rust", "spot", "mildew", "fungal", "symptom", 
        "healthy", "leaf", "plant", "crop", "vegetation", "tomato", "potato", 
        "apple", "corn", "pepper", "grape", "cherry", "rice", "wheat", "maize",
        "banana", "mango", "orange", "pomegranate", "coconut", "cotton", "sugarcane",
        "anthracnose", "bacterial", "virus", "infection", "lesion", "discoloration",
        "yellowing", "wilting", "rotting", "blister", "canker"
    ])
    
    # More specific "no flora" detection - must be explicit
    explicit_no_flora = any(phrase in text_lower for phrase in [
        "no flora detected", "no plant detected", "no crop detected", 
        "no vegetation detected", "does not contain flora", "does not contain plants",
        "no flora found", "no plants found", "no crops found",
        "image does not show", "no plants visible", "no crops visible"
    ])
    
    # Only return "no flora" if explicitly stated AND no disease/plant indicators
    # This prevents false positives when disease is mentioned
    if explicit_no_flora and not has_disease_indicators:
        return {
            'label': 'No Flora Detected',
            'score': 1.0,
            'crop_name': 'No Flora',
            'disease_name': 'No Flora Detected',
            'description': 'No flora (plants, crops, or vegetation) detected in this image.',
            'treatment_tip': 'Please upload an image containing plants, crops, or vegetation for analysis.',
            'disease_location': 'none',
            'symptoms_detected': [],
            'confidence_level': 'High',
            'no_flora': True
        }
    
    # Enhanced extraction logic for better accuracy
    crop_name = "Unknown"
    disease_name = "Unknown"
    confidence = 0.75
    
    # Extract disease name with more specificity
    if "healthy" in text_lower and ("plant" in text_lower or "crop" in text_lower or "leaf" in text_lower):
        disease_name = "Healthy"
    elif "early blight" in text_lower:
        disease_name = "Early Blight"
    elif "late blight" in text_lower:
        disease_name = "Late Blight"
    elif "leaf spot" in text_lower or "bacterial spot" in text_lower:
        disease_name = "Leaf Spot"
    elif "powdery mildew" in text_lower:
        disease_name = "Powdery Mildew"
    elif "downy mildew" in text_lower:
        disease_name = "Downy Mildew"
    elif "rust" in text_lower:
        disease_name = "Rust"
    elif "anthracnose" in text_lower:
        disease_name = "Anthracnose"
    elif "blight" in text_lower:
        disease_name = "Blight"
    elif "spot" in text_lower:
        disease_name = "Leaf Spot"
    elif "mildew" in text_lower:
        disease_name = "Mildew"
    elif "disease" in text_lower:
        disease_name = "Disease Detected"
    
    # Enhanced crop name extraction with priority and word boundary matching
    import re
    
    # Priority order: Check distinctive crops first (cereals/grains have unique characteristics)
    crops_priority = [
        # Cereals/Grains (check first - they have distinctive long, narrow leaves)
        ("wheat", "Wheat"),
        ("rice", "Rice"),
        ("corn", "Corn"),
        ("maize", "Maize"),
        ("sugarcane", "Sugarcane"),
        # Vegetables with distinctive leaves
        ("potato", "Potato"),
        ("tomato", "Tomato"),
        ("pepper", "Pepper"),
        ("cucumber", "Cucumber"),
        ("pumpkin", "Pumpkin"),
        ("watermelon", "Watermelon"),
        ("muskmelon", "Muskmelon"),
        # Fruits
        ("banana", "Banana"),
        ("coconut", "Coconut"),
        ("mango", "Mango"),
        ("apple", "Apple"),
        ("grape", "Grape"),
        ("cherry", "Cherry"),
        ("orange", "Orange"),
        ("pomegranate", "Pomegranate"),
        # Other crops
        ("cotton", "Cotton"),
        ("chickpea", "Chickpea"),
        ("kidneybeans", "Kidneybeans"),
        ("pigeonpeas", "Pigeonpeas"),
        ("mothbeans", "Mothbeans"),
        ("mungbean", "Mungbean"),
        ("blackgram", "Blackgram"),
        ("lentil", "Lentil")
    ]
    
    # Use word boundaries to find exact crop matches (prevents partial matches)
    for crop_key, crop_value in crops_priority:
        # Check for word boundary match (exact word, not part of another word)
        pattern = r'\b' + re.escape(crop_key) + r'\b'
        if re.search(pattern, text_lower):
            crop_name = crop_value
            print(f"Extracted crop from text: {crop_name}")
            break
    
    # Enhanced symptom extraction
    symptoms = []
    symptom_patterns = {
        "black spots": "Black spots",
        "brown spots": "Brown spots",
        "yellow spots": "Yellow spots",
        "circular spots": "Circular spots",
        "yellowing": "Yellowing",
        "wilting": "Wilting",
        "powdery": "Powdery growth",
        "fuzzy": "Fuzzy growth",
        "holes": "Holes in leaves",
        "discoloration": "Discoloration",
        "lesions": "Lesions",
        "blisters": "Blisters",
        "rotting": "Rotting"
    }
    for pattern, symptom_name in symptom_patterns.items():
        if pattern in text_lower:
            symptoms.append(symptom_name)
    
    # If no specific symptoms found but disease mentioned, add generic
    if not symptoms and disease_name.lower() != "healthy" and disease_name.lower() != "unknown":
        symptoms.append("Disease symptoms detected")
    
    # Enhanced confidence level determination
    confidence_level = 'Medium'
    if "high confidence" in text_lower or ("high" in text_lower and "certain" in text_lower):
        confidence_level = 'High'
    elif "low confidence" in text_lower or ("uncertain" in text_lower or "unclear" in text_lower):
        confidence_level = 'Low'
    elif "healthy" in text_lower:
        confidence_level = 'High'
    elif disease_name.lower() == "unknown":
        confidence_level = 'Low'
    
    # Extract disease location if mentioned
    disease_location = 'center'
    if "top" in text_lower and "left" in text_lower:
        disease_location = "top-left"
    elif "top" in text_lower and "right" in text_lower:
        disease_location = "top-right"
    elif "bottom" in text_lower and "left" in text_lower:
        disease_location = "bottom-left"
    elif "bottom" in text_lower and "right" in text_lower:
        disease_location = "bottom-right"
    elif "entire" in text_lower or "whole" in text_lower:
        disease_location = "entire leaf"
    elif "edge" in text_lower or "edges" in text_lower:
        disease_location = "leaf edges"
    elif "center" in text_lower or "middle" in text_lower:
        disease_location = "center"
    
    # Format description
    if symptoms:
        description = f"Symptoms: {', '.join(symptoms)}"
    elif disease_name.lower() == "healthy":
        description = "The plant appears healthy with no visible disease symptoms."
    else:
        description = f"Disease detected: {disease_name}"
    
    disease_label = f"{crop_name} - {disease_name}" if crop_name != "Unknown" else disease_name
    
    return {
        'label': disease_label,
        'score': confidence,
        'crop_name': crop_name,
        'disease_name': disease_name,
        'description': description,
        'treatment_tip': 'Please consult with an agricultural expert for specific treatment recommendations. Consider organic treatments and proper crop management practices.',
        'disease_location': disease_location,
        'symptoms_detected': symptoms if symptoms else [],
        'confidence_level': confidence_level,
        'no_flora': False  # If we got here, flora is present
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
        
        # Get current language
        lang = get_language()
        lang_instruction = ""
        if lang == 'kn':
            lang_instruction = " IMPORTANT: Respond in Kannada (ಕನ್ನಡ) language. All text in the JSON response should be in Kannada script."
        
        # Create a detailed, condition-specific prompt for fertilizer recommendation
        prompt = (
            f"You are an expert agricultural advisor with deep knowledge of crop nutrition, soil science, and irrigation management. "
            f"Provide SPECIFIC, DETAILED fertilizer recommendations based on the exact conditions provided.\n\n"
            f"CROP TO GROW: {crop_name}\n"
            f"SOIL TYPE: {soil_type}\n"
            f"WATER AVAILABILITY: {water_availability}%\n\n"
            f"ANALYSIS REQUIRED:\n"
            f"1. Analyze the specific nutrient needs of {crop_name} at different growth stages.\n"
            f"2. Consider how {soil_type} soil affects nutrient availability and what adjustments are needed.\n"
            f"3. Factor in water availability ({water_availability}%) - low water may require different fertilizer types or application methods.\n"
            f"4. Provide SPECIFIC fertilizer recommendations (exact NPK ratios, organic alternatives, micronutrients if needed).\n"
            f"5. Give detailed application instructions tailored to these specific conditions.\n"
            f"6. Explain timing based on {crop_name}'s growth cycle and {soil_type} soil characteristics.\n\n"
            f"IMPORTANT: Make your recommendations SPECIFIC to these exact conditions. Different crops, soil types, and water levels require DIFFERENT approaches.\n"
            f"DO NOT give generic advice. Be specific about:\n"
            f"- Exact fertilizer type and NPK ratio (e.g., NPK 19:19:19, DAP, Urea, SSP, etc.)\n"
            f"- Specific quantities per acre/hectare if possible\n"
            f"- How {soil_type} soil affects the choice\n"
            f"- How {water_availability}% water availability impacts fertilizer application\n"
            f"- Crop-specific timing (e.g., for {crop_name}, apply at specific growth stages)\n\n"
            f"{lang_instruction}\n\n"
            f"Respond in JSON format:\n"
            f'{{"recommendation": "detailed 3-4 sentence explanation specific to {crop_name} in {soil_type} soil with {water_availability}% water - explain WHY these specific fertilizers are recommended", '
            f'"fertilizer_type": "specific fertilizer name and NPK ratio (e.g., NPK 19:19:19, DAP 18:46:0, Urea 46:0:0, or organic alternatives) - MUST be specific to {crop_name} and {soil_type}", '
            f'"application_method": "detailed step-by-step instructions (3-4 steps) specific to {crop_name} and {soil_type} soil conditions, including quantities if possible", '
            f'"timing": "specific timing based on {crop_name} growth stages (e.g., before planting, at 30 days, during flowering, etc.) - MUST be crop-specific", '
            f'"soil_analysis": "detailed analysis of how {soil_type} soil affects {crop_name} growth and why specific fertilizers are needed, considering {water_availability}% water availability"}}\n\n'
            f"Remember: Each crop-soil-water combination is UNIQUE. Provide recommendations that reflect these specific conditions, not generic advice."
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
    """Format text response when JSON parsing fails - provide condition-specific recommendations."""
    # Crop-specific fertilizer recommendations
    crop_fertilizers = {
        "rice": "NPK 19:19:19 or DAP + Urea",
        "wheat": "NPK 19:19:19 or DAP + Urea",
        "cotton": "NPK 19:19:19 or DAP",
        "sugarcane": "NPK 19:19:19 or DAP + Urea",
        "maize": "NPK 19:19:19 or DAP + Urea",
        "tomato": "NPK 19:19:19 or organic compost",
        "potato": "NPK 19:19:19 or DAP",
        "onion": "NPK 19:19:19 or organic compost"
    }
    
    # Get crop-specific fertilizer
    crop_lower = crop_name.lower()
    fertilizer_type = "NPK 19:19:19"
    for crop_key, fert in crop_fertilizers.items():
        if crop_key in crop_lower:
            fertilizer_type = fert
            break
    
    # Water availability adjustments
    water_note = ""
    if water_availability < 30:
        water_note = "Low water availability requires careful fertilizer application. Apply in split doses and ensure proper irrigation."
    elif water_availability < 60:
        water_note = "Moderate water availability allows for standard fertilizer application."
    else:
        water_note = "Good water availability supports optimal fertilizer uptake."
    
    # Soil type specific notes
    soil_note = ""
    if "black" in soil_type.lower():
        soil_note = "Black soil is rich in nutrients but may need phosphorus supplementation."
    elif "red" in soil_type.lower():
        soil_note = "Red soil may need organic matter and nitrogen supplementation."
    elif "clay" in soil_type.lower():
        soil_note = "Clay soil retains nutrients well but may need better drainage."
    elif "sandy" in soil_type.lower():
        soil_note = "Sandy soil requires frequent fertilizer application as nutrients leach quickly."
    
    recommendation = f"For {crop_name} in {soil_type} soil with {water_availability}% water availability: {fertilizer_type} is recommended. {soil_note} {water_note}"
    
    return {
        "recommendation": recommendation + (" " + text[:300] if len(text) > 300 else " " + text),
        "fertilizer_type": fertilizer_type,
        "application_method": f"Apply {fertilizer_type} in 2-3 split doses: before planting, during vegetative growth, and during flowering (for {crop_name}). Mix well with soil and water thoroughly.",
        "timing": f"For {crop_name}: Apply before planting, at 30-45 days after planting, and during flowering stage. Adjust based on {soil_type} soil conditions.",
        "soil_analysis": f"{soil_type} soil analysis for {crop_name}: {soil_note} Water availability at {water_availability}% affects fertilizer application timing and method."
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


@app.route('/set-language/<lang>')
def set_language(lang):
    """Set the language preference in session."""
    if lang in ['en', 'kn']:
        session['language'] = lang
        flash(f'Language changed to {"English" if lang == "en" else "ಕನ್ನಡ"}', 'success')
    else:
        flash('Invalid language selection', 'error')
    return redirect(request.referrer or url_for('index'))


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


def parse_soil_text_response(text):
    """Parse text response when JSON parsing fails."""
    text_lower = text.lower()
    
    # Check if no soil is detected
    no_soil_keywords = ["no soil", "no dirt", "not soil", "not a soil", "does not contain soil", 
                        "no soil detected", "not soil image", "doesn't contain soil"]
    if any(keyword in text_lower for keyword in no_soil_keywords):
        return {
            'soil_type': 'No Soil Detected',
            'recommended_crops': [],
            'confidence': 1.0,
            'description': 'No soil detected in this image. Please upload an image containing soil samples, dirt, or agricultural soil.',
            'crop_recommendations': 'Please upload a clear image of soil for analysis.',
            'no_soil': True
        }
    
    # Try extract information from text
    soil_type = "Unknown"
    recommended_crops = []
    
    # Simple extraction logic
    if "alluvial" in text_lower:
        soil_type = "Alluvial"
        recommended_crops = ["Rice", "Wheat", "Sugarcane", "Maize", "Cotton", "Soyabean", "Jute"]
    elif "black" in text_lower:
        soil_type = "Black"
        recommended_crops = ["Virginia", "Wheat", "Jowar", "Millets", "Linseed", "Castor", "Sunflower"]
    elif "clay" in text_lower:
        soil_type = "Clay"
        recommended_crops = ["Rice", "Lettuce", "Chard", "Broccoli", "Cabbage", "Snap Beans"]
    elif "red" in text_lower:
        soil_type = "Red"
        recommended_crops = ["Cotton", "Wheat", "Pulses", "Millets", "Oil Seeds", "Potatoes"]
    else:
        soil_type = "Unknown"
        recommended_crops = []
    
    return {
        'soil_type': soil_type,
        'recommended_crops': recommended_crops,
        'confidence': 0.75,
        'description': text[:200] if len(text) > 200 else text,
        'crop_recommendations': f"Based on {soil_type} soil, recommended crops: {', '.join(recommended_crops) if recommended_crops else 'Please consult an agricultural expert.'}",
        'no_soil': False
    }


# ---------------------------------------------
# 🔹 Flask Routes (Additional Routes)
# ---------------------------------------------

@app.route('/soil-predict', methods=['POST'])
def soil_prediction():
    """Get soil analysis and crop recommendations using Ollama."""
    title = 'Soil Analysis & Crop Recommendation'
    
    try:
        if 'soil_image' not in request.files:
            return render_template('try_again.html', title=title, error_message="No file part in request.")
        
        file = request.files.get('soil_image')
        if not file or file.filename == '':
            return render_template('try_again.html', title=title, error_message="No file selected for uploading.")
        
        if not allowed_file(file.filename):
            return render_template('try_again.html', title=title, error_message="Allowed file types are png, jpg, jpeg")
        
        # Secure and save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Get prediction from Ollama
        prediction = ollama_analyze_soil_and_recommend_crops(file_path)
        print("Soil Prediction:", prediction)
        
        # Get no_soil flag
        no_soil = prediction.get('no_soil', False)
        
        # Convert image to base64 for display
        with open(file_path, "rb") as f:
            img_bytes = f.read()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        # Format prediction for template
        formatted_prediction = {
            'label': f"{prediction.get('soil_type', 'Unknown')} Soil",
            'score': prediction.get('confidence', 0.0)
        }
        
        return render_template('crop-result.html', 
                             prediction=formatted_prediction, 
                             image_base64=img_base64, 
                             title=title,
                             soil_type=prediction.get('soil_type', 'Unknown'),
                             recommended_crops=prediction.get('recommended_crops', []),
                             description=prediction.get('description', ''),
                             crop_recommendations=prediction.get('crop_recommendations', ''),
                             no_soil=no_soil)
        
    except Exception as e:
        print(f"Error in soil_prediction: {e}")
        error = f'An error occurred during prediction: {str(e)}'
        return render_template('try_again.html', title=title, error_message=error)


def ollama_analyze_soil_and_recommend_crops(image_path):
    """Use Ollama vision model to analyze soil and recommend crops."""
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
                'soil_type': 'Error',
                'recommended_crops': [],
                'description': error_msg,
                'details': 'Please install llava model: ollama pull llava'
            }
        
        # Use the available model
        model_to_use = model_info if isinstance(model_info, str) else "llava"
        
        # Encode image to base64
        with open(image_path, "rb") as f:
            img_bytes = f.read()
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")
        
        # Get current language
        lang = get_language()
        lang_instruction = ""
        if lang == 'kn':
            lang_instruction = " IMPORTANT: Respond in Kannada (ಕನ್ನಡ) language. All text in the JSON response should be in Kannada script."
        
        # Prompt for Ollama
        prompt = (
            "You are an expert agricultural consultant. Analyze this image carefully.\n\n"
            "FIRST, check if this image contains SOIL. Look for:\n"
            "- Soil samples, dirt, earth, ground\n"
            "- Soil texture, color, composition\n"
            "- Agricultural soil, farmland soil\n\n"
            "If NO SOIL is detected (e.g., the image shows plants, animals, objects, people, buildings, or anything else that is NOT soil), "
            "respond with soil_detected: false.\n\n"
            "If SOIL IS detected, identify the soil type (Alluvial, Black, Clay, Red, Sandy, Loamy, Silt) and recommend suitable crops.\n"
            f"{lang_instruction}\n\n"
            "Respond in JSON format with these exact fields: "
            '{"soil_detected": true/false, "soil_type": "name of soil type or No Soil Detected", "recommended_crops": ["crop1", "crop2", ...], "confidence": 0.95, "description": "brief description", "crop_recommendations": "detailed crop recommendations"}\n\n'
            'If soil_detected is false, set soil_type to "No Soil Detected" and recommended_crops to an empty array.'
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
            timeout=120
        )
        
        if response.status_code == 200:
            result_data = response.json()
            
            # Extract response text
            response_text = result_data.get('response', '')
            
            # Try parse JSON from response
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
                
                # Check if soil was detected
                soil_detected = result_json.get('soil_detected', True)  # Default to True for backward compatibility
                
                if not soil_detected:
                    # No soil detected in the image
                    return {
                        'soil_type': 'No Soil Detected',
                        'recommended_crops': [],
                        'confidence': 1.0,
                        'description': 'No soil detected in this image. Please upload an image containing soil samples, dirt, or agricultural soil.',
                        'crop_recommendations': 'Please upload a clear image of soil for analysis.',
                        'no_soil': True
                    }
                
                # Format result
                soil_type = result_json.get('soil_type', 'Unknown')
                recommended_crops = result_json.get('recommended_crops', [])
                
                return {
                    'soil_type': soil_type,
                    'recommended_crops': recommended_crops,
                    'confidence': float(result_json.get('confidence', 0.85)),
                    'description': result_json.get('description', 'No description available.'),
                    'crop_recommendations': result_json.get('crop_recommendations', 'No recommendations available.'),
                    'no_soil': False
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, extract from text
                print("Failed to parse JSON, extracting from text...")
                return parse_soil_text_response(response_text)
        else:
            error_text = response.text[:200] if response.text else "Unknown error"
            print(f"Ollama Error: {response.status_code} - {error_text}")
            
            if response.status_code == 404:
                error_desc = "Model 'llava' not found. Please install it: ollama pull llava"
            elif response.status_code == 400:
                error_desc = f"Invalid request to Ollama: {error_text}"
            else:
                error_desc = f"Ollama API returned error {response.status_code}: {error_text}"
            
            return {
                'soil_type': 'Error',
                'recommended_crops': [],
                'confidence': 0.0,
                'description': error_desc,
                'crop_recommendations': 'Please ensure Ollama is running and the llava model is installed.'
            }
            
    except requests.exceptions.ConnectionError:
        print("Connection Error: Could not connect to Ollama. Is it running?")
        return {
            'soil_type': 'Error',
            'recommended_crops': [],
            'confidence': 0.0,
            'description': 'Could not connect to Ollama. Please ensure Ollama is running on localhost:11434',
            'crop_recommendations': 'Start Ollama service and ensure the llava model is installed: ollama pull llava'
        }
    except Exception as e:
        print(f"Soil Analysis Error: {e}")
        return {
            'soil_type': 'Error',
            'recommended_crops': [],
            'confidence': 0.0,
            'description': f'An error occurred: {str(e)}',
            'crop_recommendations': 'Please try again with a different image.'
        }


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
            
            # Get disease name and location for highlighting check
            disease_name = prediction.get('disease_name', 'Unknown')
            disease_location = prediction.get('disease_location', 'none')
            
            # Highlight disease area if disease is detected (not healthy, not unknown, not no flora)
            if not no_flora and disease_name and disease_name.lower() not in ['healthy', 'unknown', 'no flora detected']:
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
    print("AgroLens - Crop Disease Detection")
    print("=" * 50)
    
    # Check Ollama connection and model availability
    try:
        ollama_check = requests.get("http://localhost:11434/api/tags", timeout=3)
        if ollama_check.status_code == 200:
            print("[OK] Ollama is running on http://localhost:11434")
            model_available, model_info = check_ollama_model("llava")
            if model_available:
                print(f"[OK] llava model is available: {model_info}")
            else:
                print("[WARNING] 'llava' model is NOT installed!")
                print("   To install, run: ollama pull llava")
                print(f"   Available models: {', '.join(model_info) if isinstance(model_info, list) else 'None'}")
        else:
            print("[WARNING] Ollama responded with an error")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to Ollama!")
        print("   Please start Ollama: ollama serve")
    except Exception as e:
        print(f"[WARNING] Could not check Ollama status: {e}")
    
    print("=" * 50)
    print("Starting Flask server...")
    
    # Get configuration from environment variables
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('PORT', os.getenv('FLASK_PORT', '5000')))
    
    print(f"Server URL: http://{host}:{port}")
    print(f"Debug Mode: {debug_mode}")
    print("=" * 50)
    app.run(debug=debug_mode, host=host, port=port)
