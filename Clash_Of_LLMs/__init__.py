from flask import Flask, render_template

# Initialize Flask app
app = Flask(__name__)

from Clash_Of_LLMs import routes, plot

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
