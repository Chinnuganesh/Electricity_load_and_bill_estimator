from flask import Flask, json, request, render_template, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# Set your Gemini API key here
genai.configure(api_key='AIzaSyBcKSvunDus17twIGzMC4_slcNLYtVhGEQ')


# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

def preprocess_recommendations(recommendations):
    # Remove '**' for headings
    recommendations = recommendations.replace('**', ' ')

    # Replace '*' with a newline '\n'
    recommendations = recommendations.replace('*', ' ')
    recommendations = recommendations.replace('    ', '\n')

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

@app.route('/get_recommendations_be')
def get_recommendations_be():
    # Retrieve the JSON data from the request
    data = request.args.get('data')
    decoded_data = json.loads(data)
    
    # Extract the information from the data
    appliances = decoded_data['appliances']
    maxbudget = decoded_data['maxbudget']
    ratePerKWh = decoded_data['ratePerKWh']
    unitsConsumed = decoded_data['unitsConsumed']
    billEstimation = decoded_data['billEstimation']
    
    # Implement your logic for generating recommendations here
    prompt = generate_prompt_billestimation(appliances, maxbudget, ratePerKWh, unitsConsumed, billEstimation)
    # Call the Gemini API
    response = model.generate_content(prompt)
    # Get the text from the Gemini response and preprocess it
    recommendations = response.text.strip()
    recommendations = preprocess_recommendations(recommendations)
    # Return the recommendations as plain text
    return render_template('be_recommendations.html', recommendations=recommendations)
    

def generate_prompt_billestimation(appliances, maxbudget, ratePerKWh, unitsConsumed, billEstimation):
    # Format appliances data for inclusion in the prompt
    appliances_str = ", ".join([f"{appliance['name']} (Power: {appliance['power']} Watts, Quantity: {appliance['quantity']})" for appliance in appliances])
    
    # Format bill estimation data for inclusion in the prompt
    bill_str = f"Per Hour: ₹{billEstimation['perHour']}, Per Day: ₹{billEstimation['perDay']}, Per Month: ₹{billEstimation['perMonth']}, Per Year: ₹{billEstimation['perYear']}"

    # Construct the prompt string
    prompt = (f"I was given the following home appliances and their load details. "
              f"Provide recommendations for suitable usage of all my appliances where the monthly bill is within my maximum budget (location: India):\n"
              f"Appliances details: {appliances_str}\n"
              f"Calculated bill for appliances and usage is: {bill_str}\n"
              f"Per kWh price in India: {ratePerKWh} rupees consider it as he price in india now \n"
              f"Monthly max budget: {maxbudget} rupees\n"
              f"Based on the load and my monthly budget, suggest how to use the appliances for better utilization and to ensure the cost of the bill is under my maximum budget per month.")
    
    print(prompt)
    return prompt



# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
