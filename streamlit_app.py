from flask import Flask, render_template, request, jsonify, session, send_file
# We'll use the standard Flask session instead of Flask-Session
# from flask_session import Session
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for matplotlib (non-interactive)
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from diagnosis_engine import DiagnosisEngine
from localization import get_translation, available_languages
import json
import os
import tempfile
from datetime import datetime
import io
import base64
import pandas as pd

app = Flask(__name__)
app.secret_key = 'diagnosis_ai_secret_key'
# Use standard Flask sessions instead of flask_session
# app.config['SESSION_TYPE'] = 'filesystem'
# Session(app)

# Initialize the diagnosis engine
engine = DiagnosisEngine()

# Get symptoms data organized by category
symptoms_data = {
    "Respiratory": ["cough", "shortness of breath", "sore throat", "loss of taste or smell", "wheezing", "chest pain"],
    "Gastrointestinal": ["nausea", "vomiting", "diarrhea", "abdominal pain", "feeling of fullness", "jaundice", "dark urine"],
    "General": ["fever", "fatigue", "body aches", "night sweats", "unexplained weight loss"],
    "Neurological": ["headache", "dizziness", "blurred vision", "sensitivity to light", "confusion", "persistent sadness"],
    "Metabolic": ["frequent urination", "increased thirst", "unexplained weight loss", "extreme hunger"],
    "Psychiatric": ["excessive worry", "restlessness", "difficulty concentrating", "loss of interest", "sleep disturbance"],
    "Musculoskeletal": ["joint pain", "joint stiffness", "swelling", "reduced range of motion"]
}

@app.route('/')
def index():
    # Set default language if not set
    if 'language' not in session:
        session['language'] = 'en'
    
    # Get available languages for the dropdown
    langs = []
    for lang in available_languages():
        langs.append({
            'code': lang,
            'name': f"{get_translation('en', f'lang_{lang}')} ({lang})"
        })
    
    return render_template('pages/home.html',
                          languages=langs,
                          current_lang=session['language'],
                          translations=get_translations_for_frontend(session['language']))

@app.route('/diagnosis_page')
def diagnosis_page():
    # Set default language if not set
    if 'language' not in session:
        session['language'] = 'en'
    
    # Get all symptoms for the form
    all_symptoms = {}
    for category, symptoms in symptoms_data.items():
        translated_category = get_translation(session['language'], category)
        all_symptoms[translated_category] = []
        for symptom in symptoms:
            translated_symptom = get_translation(session['language'], symptom)
            all_symptoms[translated_category].append({
                'id': symptom,
                'name': translated_symptom
            })
    
    # Get available languages for the dropdown
    langs = []
    for lang in available_languages():
        langs.append({
            'code': lang,
            'name': f"{get_translation('en', f'lang_{lang}')} ({lang})"
        })
    
    return render_template('pages/diagnosis.html', 
                          symptoms=all_symptoms,
                          languages=langs,
                          current_lang=session['language'],
                          translations=get_translations_for_frontend(session['language']))

@app.route('/set-language', methods=['POST'])
def set_language():
    data = request.get_json()
    lang_code = data.get('language')
    
    if lang_code and lang_code in available_languages():
        session['language'] = lang_code
        return jsonify({
            'success': True,
            'translations': get_translations_for_frontend(lang_code)
        })
    
    return jsonify({'success': False, 'message': 'Invalid language code'})

@app.route('/diagnose', methods=['POST'])
def diagnose():
    symptoms = request.get_json().get('symptoms', [])
    
    # Convert to the format expected by DiagnosisEngine
    symptom_dict = {}
    # Initialize all symptoms to False
    for category, category_symptoms in symptoms_data.items():
        for symptom in category_symptoms:
            symptom_dict[symptom] = False
    
    # Set selected symptoms to True
    for symptom_id in symptoms:
        if symptom_id in symptom_dict:
            symptom_dict[symptom_id] = True
    
    # Run diagnosis
    results = engine.run_diagnosis(symptom_dict)
    
    # Format results for the frontend
    formatted_results = []
    for disease, confidence, advice in results:
        formatted_results.append({
            'disease': get_translation(session['language'], disease),
            'confidence': confidence,
            'advice': get_translation(session['language'], advice),
            'disease_id': disease,  # Keep original ID for later reference
            'advice_id': advice     # Keep original ID for later reference
        })
    
    # Store in session for PDF export
    session['diagnosis_results'] = results
    session['selected_symptoms'] = [s for s, v in symptom_dict.items() if v]
    
    return jsonify({'success': True, 'results': formatted_results})

@app.route('/generate-chart', methods=['POST'])
def generate_chart():
    data = request.get_json()
    results = data.get('results', [])
    
    if not results:
        return jsonify({'success': False, 'message': 'No results provided'})
    
    try:
        # Extract data for chart
        diseases = [result['disease'] for result in results]
        confidences = [result['confidence'] for result in results]
        
        # Create chart
        plt.figure(figsize=(10, 6), dpi=100)
        # Use a colorful palette for bars
        colors = ['#4361EE', '#3A0CA3', '#4CC9F0', '#F72585', '#7209B7']
        bars = plt.barh(diseases, confidences, color=colors[:len(diseases)])
        
        # Add percentage labels to the end of each bar
        for i, (disease, confidence) in enumerate(zip(diseases, confidences)):
            plt.text(confidence + 1, i, f"{confidence}%", va='center', fontweight='bold')
            
        # Add title and labels with proper translation
        plt.xlabel(get_translation(session['language'], 'confidence_percent'), fontsize=12)
        plt.title(get_translation(session['language'], 'diagnosis_confidence'), fontsize=14, fontweight='bold')
        
        # Style the chart
        plt.grid(axis='x', linestyle='--', alpha=0.6)
        plt.tight_layout()
        
        # Save to memory
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png')
        img_bytes.seek(0)
        plt.close()  # Important to close the figure
        
        # Convert to base64 for embedding in HTML
        img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')
        
        return jsonify({
            'success': True, 
            'chart_data': f'data:image/png;base64,{img_base64}'
        })
    except Exception as e:
        print(f"Chart generation error: {str(e)}")
        return jsonify({'success': False, 'message': f'Error generating chart: {str(e)}'})

@app.route('/export-pdf', methods=['POST'])
def export_pdf():
    if 'diagnosis_results' not in session or 'selected_symptoms' not in session:
        return jsonify({'success': False, 'message': 'No diagnosis results to export'})
    
    try:
        # Create a temporary PDF file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(temp_fd)
        
        c = canvas.Canvas(temp_path, pagesize=letter)
        c.setTitle(get_translation(session['language'], "diagnosis_report"))
        
        # Add report title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, get_translation(session['language'], "diagnosis_report"))
        c.setFont("Helvetica", 12)
        
        # Add date
        c.drawString(100, 730, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Add selected symptoms
        c.drawString(100, 700, get_translation(session['language'], "selected_symptoms_label"))
        symptoms_list = session['selected_symptoms']
        translated_symptoms = [get_translation(session['language'], s) for s in symptoms_list]
        symptoms_text = ", ".join(translated_symptoms) if translated_symptoms else get_translation(session['language'], "none")
        
        # Wrap text if too long
        if len(symptoms_text) > 70:
            c.drawString(120, 680, symptoms_text[:70])
            c.drawString(120, 660, symptoms_text[70:])
            y_position = 640
        else:
            c.drawString(120, 680, symptoms_text)
            y_position = 660
        
        # Add diagnosis results
        c.drawString(100, y_position, get_translation(session['language'], "diagnosis_results_label"))
        y_position -= 20
        
        for disease, confidence, advice in session['diagnosis_results']:
            trans_disease = get_translation(session['language'], disease)
            trans_advice = get_translation(session['language'], advice)
            
            c.drawString(120, y_position, f"- {trans_disease} ({confidence}%)")
            y_position -= 20
            
            # Wrap advice text if needed
            advice_lines = wrap_text(f"{get_translation(session['language'], 'advice_label')}: {trans_advice}", 60)
            for line in advice_lines:
                c.drawString(140, y_position, line)
                y_position -= 20
            
            y_position -= 10
            
            # Check if we need a new page
            if y_position < 100:
                c.showPage()
                c.setFont("Helvetica", 12)
                y_position = 750
        
        c.save()
        
        return send_file(
            temp_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name="diagnosis_report.pdf",
            max_age=0
        )
    except Exception as e:
        print(f"PDF Export Error: {str(e)}")
        return jsonify({'success': False, 'message': f'PDF export failed: {str(e)}'})

@app.route('/save-results', methods=['POST'])
def save_results():
    if 'diagnosis_results' not in session or 'selected_symptoms' not in session:
        return jsonify({'success': False, 'message': 'No diagnosis results to save'})
    
    data = {
        "selected_symptoms": session['selected_symptoms'],
        "results": session['diagnosis_results'],
        "timestamp": datetime.now().isoformat()
    }
    
    # Create a JSON response for download
    response = jsonify(data)
    response.headers.set('Content-Disposition', 'attachment', filename='diagnosis_results.json')
    return response

def get_translations_for_frontend(lang):
    """Get common translations needed on the frontend"""
    keys = [
        "title", "diagnose", "export", "chart", "clear", "save", "close", 
        "language_select", "search_symptoms", "warning", "error", "success",
        "info", "no_symptoms_selected", "result", "no_disease_match",
        "diagnosis_result", "diagnosis_result_header", "run_diagnosis_first",
        "confidence_percent", "diagnosis_confidence", "diagnosis_chart_title",
        "reportlab_missing", "no_results_to_export", "advice_label",
        "selected_symptoms_label"
    ]
    
    translations = {}
    for key in keys:
        translations[key] = get_translation(lang, key)
    
    return translations

def wrap_text(text, width):
    """Wrap text to fit within a given width"""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        if len(" ".join(current_line + [word])) <= width:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(" ".join(current_line))
    
    return lines

@app.route('/findings_page')
def findings_page():
    # Set default language if not set
    if 'language' not in session:
        session['language'] = 'en'
    
    # Get available languages for the dropdown
    langs = []
    for lang in available_languages():
        langs.append({
            'code': lang,
            'name': f"{get_translation('en', f'lang_{lang}')} ({lang})"
        })
    
    # Check if we have diagnosis results in the session
    has_diagnosis = 'diagnosis_results' in session and session['diagnosis_results']
    
    # Translate selected symptoms
    translated_symptoms = []
    if 'selected_symptoms' in session:
        for symptom in session['selected_symptoms']:
            translated_symptoms.append(get_translation(session['language'], symptom))

    # Pass translated symptoms to the template
    return render_template('pages/findings.html', 
                          languages=langs,
                          current_lang=session['language'],
                          has_diagnosis=has_diagnosis,
                          translations=get_translations_for_frontend(session['language']),
                          translated_symptoms=translated_symptoms)

@app.route('/conclusions_page')
def conclusions_page():
    # Set default language if not set
    if 'language' not in session:
        session['language'] = 'en'
    
    # Get available languages for the dropdown
    langs = []
    for lang in available_languages():
        langs.append({
            'code': lang,
            'name': f"{get_translation('en', f'lang_{lang}')} ({lang})"
        })
    
    # Check if we have diagnosis results in the session
    has_diagnosis = 'diagnosis_results' in session and session['diagnosis_results']
    
    return render_template('pages/conclusions.html', 
                          languages=langs,
                          current_lang=session['language'],
                          has_diagnosis=has_diagnosis,
                          translations=get_translations_for_frontend(session['language']))

@app.route('/questions_page')
def questions_page():
    # Set default language if not set
    if 'language' not in session:
        session['language'] = 'en'
    
    # Get available languages for the dropdown
    langs = []
    for lang in available_languages():
        langs.append({
            'code': lang,
            'name': f"{get_translation('en', f'lang_{lang}')} ({lang})"
        })
    
    # Get FAQ data
    faqs = [
        {
            "question": "What should I do if the diagnosis shows a high confidence for a serious condition?",
            "answer": "If the diagnosis shows a high confidence level for any serious condition, you should consult with a healthcare professional as soon as possible. This system is meant to provide preliminary insights but is not a replacement for professional medical advice."
        },
        {
            "question": "How accurate is this diagnosis system?",
            "answer": "This system provides a probability-based assessment based on the symptoms you enter. Its accuracy is limited by the information provided and should be used as an informational tool only, not as a definitive diagnosis."
        },
        {
            "question": "Can I trust the advice given by this system?",
            "answer": "The advice provided is general in nature and based on common medical knowledge. It should be used as a starting point for understanding your symptoms, but specific medical advice should always come from a qualified healthcare provider."
        },
        {
            "question": "How does the confidence percentage work?",
            "answer": "The confidence percentage is calculated based on how closely your reported symptoms match known symptom patterns for various conditions. A higher percentage means more of your symptoms are typically associated with the identified condition."
        },
        {
            "question": "What should I do if none of the suggested conditions seem correct?",
            "answer": "If none of the suggested conditions seem accurate, it could mean that your symptoms don't strongly match our database patterns, or that you might have a less common condition. In either case, consulting with a healthcare provider is recommended."
        }
    ]
    
    return render_template('pages/questions.html', 
                          languages=langs,
                          current_lang=session['language'],
                          faqs=faqs,
                          translations=get_translations_for_frontend(session['language']))

@app.route('/about_page')
def about_page():
    # Set default language if not set
    if 'language' not in session:
        session['language'] = 'en'
    
    # Get available languages for the dropdown
    langs = []
    for lang in available_languages():
        langs.append({
            'code': lang,
            'name': f"{get_translation('en', f'lang_{lang}')} ({lang})"
        })
    
    return render_template('pages/about.html', 
                          languages=langs,
                          current_lang=session['language'],
                          translations=get_translations_for_frontend(session['language']))

@app.route('/save-diagnosis-session', methods=['POST'])
def save_diagnosis_session():
    data = request.get_json()
    results = data.get('results', [])
    
    if not results:
        return jsonify({'success': False, 'message': 'No results provided'})
    
    # Store formatted results in session
    session['formatted_results'] = results
    
    return jsonify({'success': True})

@app.route('/get-diagnosis-data')
def get_diagnosis_data():
    if 'formatted_results' not in session or not session['formatted_results']:
        return jsonify({'success': False, 'message': 'No diagnosis data found'})
    
    if 'selected_symptoms' not in session:
        selected_symptoms = []
    else:
        # Get translated symptom names
        selected_symptoms = [get_translation(session['language'], s) for s in session['selected_symptoms']]
    
    return jsonify({
        'success': True, 
        'results': session['formatted_results'],
        'symptoms': selected_symptoms
    })

@app.route('/generate-chart-from-session')
def generate_chart_from_session():
    if 'formatted_results' not in session or not session['formatted_results']:
        return jsonify({'success': False, 'message': 'No diagnosis results to chart'})
    
    try:
        # Extract data for chart
        results = session['formatted_results']
        diseases = [result['disease'] for result in results]
        confidences = [result['confidence'] for result in results]
        
        # Create chart
        plt.figure(figsize=(10, 6), dpi=100)
        # Use a colorful palette for bars
        colors = ['#4361EE', '#3A0CA3', '#4CC9F0', '#F72585', '#7209B7']
        bars = plt.barh(diseases, confidences, color=colors[:len(diseases)])
        
        # Add percentage labels to the end of each bar
        for i, (disease, confidence) in enumerate(zip(diseases, confidences)):
            plt.text(confidence + 1, i, f"{confidence}%", va='center', fontweight='bold')
            
        # Add title and labels with proper translation
        plt.xlabel(get_translation(session['language'], 'confidence_percent'), fontsize=12)
        plt.title(get_translation(session['language'], 'diagnosis_confidence'), fontsize=14, fontweight='bold')
        
        # Style the chart
        plt.grid(axis='x', linestyle='--', alpha=0.6)
        plt.tight_layout()
        
        # Save to memory
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png')
        img_bytes.seek(0)
        plt.close()  # Important to close the figure
        
        # Convert to base64 for embedding in HTML
        img_base64 = base64.b64encode(img_bytes.read()).decode('utf-8')
        
        return jsonify({
            'success': True, 
            'chart_data': f'data:image/png;base64,{img_base64}'
        })
    except Exception as e:
        print(f"Chart generation error: {str(e)}")
        return jsonify({'success': False, 'message': f'Error generating chart: {str(e)}'})

@app.route('/answer-question', methods=['POST'])
def answer_question():
    data = request.get_json()
    question = data.get('question', '')
    
    if not question:
        return jsonify({'success': False, 'message': 'No question provided'})
    
    # Get diagnosis context if available
    if 'formatted_results' in session and session['formatted_results']:
        # Get primary condition (highest confidence)
        primary_condition = sorted(session['formatted_results'], key=lambda x: x['confidence'], reverse=True)[0]
        context = f"Based on your diagnosis of {primary_condition['disease']}: "
    else:
        context = "Based on general medical knowledge: "
    
    # Simple canned responses - in a real app, this would use a more sophisticated system
    responses = {
        "treatment": f"{context}For treatment options, it's important to consult with a healthcare provider who can provide personalized advice based on your specific situation.",
        "symptoms": f"{context}Symptoms can vary between individuals. If you're experiencing new or worsening symptoms, it's recommended to seek medical attention.",
        "duration": f"{context}The duration of recovery depends on many factors including your overall health, the severity of the condition, and how well you respond to treatment.",
        "prevention": f"{context}Preventive measures often include maintaining a healthy lifestyle, regular check-ups, and following your doctor's recommendations.",
        "serious": f"{context}If you're concerned about the seriousness of your symptoms, it's always best to err on the side of caution and consult a healthcare professional.",
        "contagious": f"{context}Whether this condition is contagious depends on its specific nature. Some medical conditions are transmissible while others are not."
    }
    
    # Very simple keyword matching
    answer = f"{context}I don't have enough information to answer your question specifically. Please consult with a healthcare professional for personalized advice."
    
    question_lower = question.lower()
    for key, response in responses.items():
        if key in question_lower:
            answer = response
            break
    
    return jsonify({'success': True, 'answer': answer})

# Streamlit interface
import streamlit as st
import subprocess
from threading import Thread
import time
import socket

def find_free_port():
    """Find a free port on the local machine"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def run_flask():
    """Run the Flask app in a separate thread"""
    # Ensure directories exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
        os.makedirs('templates/pages', exist_ok=True)
    if not os.path.exists('static'):
        os.makedirs('static')
        os.makedirs('static/css', exist_ok=True)
        os.makedirs('static/js', exist_ok=True)
        os.makedirs('static/images', exist_ok=True)
    
    # Use WSGI server with Flask
    from waitress import serve
    port = st.session_state.get("flask_port", find_free_port())
    st.session_state.flask_port = port
    serve(app, host='127.0.0.1', port=port)

def start_flask_server():
    """Start the Flask server in a separate thread"""
    if "flask_thread" not in st.session_state or not st.session_state.flask_thread.is_alive():
        flask_thread = Thread(target=run_flask, daemon=True)
        flask_thread.start()
        st.session_state.flask_thread = flask_thread
        # Allow time for server to start
        time.sleep(1)

# Streamlit interface
def main():
    st.title("Medical Diagnosis System")
    st.write("This application provides medical diagnosis based on symptoms.")
    
    # Start Flask in a separate thread
    start_flask_server()
    
    # Get Flask app URL
    flask_url = f"http://localhost:{st.session_state.flask_port}"
    st.write(f"Your diagnosis application is running at: {flask_url}")
    
    # Display an iframe with the Flask app
    st.components.v1.iframe(flask_url, height=800, scrolling=True)
    
    st.write("Note: This is a demo application and not meant for real medical diagnosis.")

if __name__ == '__main__':
    main()