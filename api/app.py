# Using flask to make an api
# import necessary libraries and functions
from flask import Flask, jsonify, request
from datetime import datetime
import logging
import sys
import os

# Add the parent directory to the Python path to import agent_workflow
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_workflow import AgentWorkflow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# creating a Flask app
app = Flask(__name__)

# Initialize AgentWorkflow
logger.info("Initializing AgentWorkflow...")
agent_wf = AgentWorkflow()
agent_wf.create_agents()
agent_wf.create_tasks()
agent_wf.setup_crew()
logger.info("AgentWorkflow initialized successfully")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "AI Blog Agent",
            "version": "1.0.0"
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/generate-blog', methods=['POST'])
def generate_blog():
    """Generate blog post from topic prompt"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate input
        if not data or 'topic' not in data:
            return jsonify({
                "error": "Missing required field 'topic' in request body"
            }), 400
        
        topic = data['topic'].strip()
        if not topic:
            return jsonify({
                "error": "Topic cannot be empty"
            }), 400
        
        logger.info(f"Starting blog generation for topic: {topic}")
        
        # Execute the crew with the provided topic
        result = agent_wf.kickoff_crew(topic=topic)
        
        logger.info("Blog generation completed successfully")
        
        return jsonify({
            "status": "success",
            "topic": topic,
            "blog_post": str(result),
            "timestamp": datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating blog post: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

# on the terminal type: curl http://127.0.0.1:5000/
# returns hello world when we use GET.
# returns the data that we send when we use POST.
@app.route('/', methods = ['GET', 'POST'])
def home():
    if(request.method == 'GET'):

        data = "hello world"
        return jsonify({'data': data})


# A simple function to calculate the square of a number
# the number to be squared is sent in the URL when we use GET
# on the terminal type: curl http://127.0.0.1:5000 / home / 10
# this returns 100 (square of 10)
@app.route('/home/<int:num>', methods = ['GET'])
def disp(num):

    return jsonify({'data': num**2})


# # driver function
# if __name__ == '__main__':

#     app.run(debug = True)