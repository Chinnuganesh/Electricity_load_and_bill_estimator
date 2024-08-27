from flask import Flask, json, request, render_template, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# Set your Gemini API key here
genai.configure(api_key='AIzaSyC_IONOCrNSOArNFs0BlnKQ_9W0UH2EqPE')


# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

def preprocess_recommendations(recommendations):
    # Remove '**' for headings
    recommendations = recommendations.replace('**', ' ')

    # Replace '*' with a newline '\n'
    recommendations = recommendations.replace('*', ' ')
    recommendations = recommendations.replace('    ', '')

    # Ensure consistent formatting with additional newlines
    recommendations = recommendations.replace('\n\n', '\n').strip()
  

    return recommendations




# Route for the home page
@app.route('/home', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def welcome():
    return render_template('index.html')

# Route for the load calculator page
@app.route('/load_calculator', methods=['GET', 'POST'])
def load_calculator():
    return render_template('lc.html')

@app.route('/get_recommendations', methods=['GET'])
def get_recommendations():
    # Get data from the GET request's query parameters
    encoded_appliances = request.args.get('appliances')
    
    # Decode the JSON data from the query parameter
    appliances = json.loads(encoded_appliances)

    # Generate the prompt for the Gemini API
    prompt = generate_recommendations(appliances)

    # Call the Gemini API
    response = model.generate_content(prompt)

    # Get the text from the Gemini response and preprocess it
    recommendations = response.text.strip()
    recommendations = preprocess_recommendations(recommendations)


    print(recommendations)

    # Return the recommendations as plain text
    return render_template('lc_recommendations.html', recommendations=recommendations)




# Helper function to generate a detailed prompt for the Gemini API
def generate_recommendations(appliances):
    # Construct a detailed prompt with the list of appliances
    prompt = "Given the following home appliances and their load details, provide recommendations for suitable kVA lines, inverters, and stabilizers:\n"
    
    for appliance in appliances:
        name = appliance['name']
        power = appliance['power']
        quantity = appliance['quantity']
        prompt += f"Appliance: {name}, Power: {power}W, Quantity: {quantity}\n"
    
    prompt += "Based on the load, what kVA line,  stabilizer , inverter and the battery capacity [ inverter runtime for 5 hours , 12 hours , 24 hours  ] , would you recommend? give response easily understandable and , dont show the load calculation part in the response but show the total load value in response . and some product recommendations which are considarable to buy "
    
    return prompt   


# Route for the bill estimator page
@app.route('/bill_estimator', methods=['GET', 'POST'])
def bill_estimator():
    return render_template('be.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
