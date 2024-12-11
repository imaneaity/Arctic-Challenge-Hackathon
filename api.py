from flask import Flask, request, jsonify
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'

# Load the RDF data
rdf_file = "buildings_energy.ttl"
graph = Graph()
graph.parse(rdf_file, format="turtle")

# Define API endpoint to query the RDF graph
@app.route('/query', methods=['POST'])
def sparql_query():
    """
    Execute a SPARQL query on the RDF graph.
    Example Query (POST Body):
    {
        "query": "SELECT ?building WHERE { ?building a <https://brickschema.org/schema/1.1/Brick#Building> . }"
    }
    """
    try:
        # Get the SPARQL query from the request body
        data = request.get_json()
        query = data.get('query', None)
        if not query:
            return jsonify({"error": "SPARQL query not provided"}), 400

        # Execute the query
        prepared_query = prepareQuery(query)
        results = graph.query(prepared_query)

        # Convert results to JSON
        output = []
        for row in results:
            output.append({str(var): str(row[var]) for var in row.labels})

        return jsonify({"results": output}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/buildings', methods=['GET'])
def get_buildings():
    """
    Retrieve all buildings in the RDF graph.
    """
    try:
        query = """
        SELECT ?building ?address WHERE {
            ?building a <https://brickschema.org/schema/1.1/Brick#Building> ;
                      <https://brickschema.org/schema/1.1/Brick#hasAddress> ?address .
        }
        """
        results = graph.query(query)
        output = [{"building": str(row.building), "address": str(row.address)} for row in results]
        return jsonify(output), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Additional SPARQL Queries
@app.route('/energy_usage', methods=['GET'])
def get_energy_usage():
    """
    Retrieve total energy usage for each building.
    """
    try:
        query = """
        SELECT ?building ?totalEnergy WHERE {
            ?building a <https://brickschema.org/schema/1.1/Brick#Building> ;
                      <https://brickschema.org/schema/1.1/Brick#hasPart> ?energyUsage .
            ?energyUsage a <https://brickschema.org/schema/1.1/Brick#Energy_Usage> ;
                         <https://brickschema.org/schema/1.1/Brick#totalEnergy> ?totalEnergy .
        }
        """
        results = graph.query(query)
        output = [{"building": str(row.building), "totalEnergy": str(row.totalEnergy)} for row in results]
        return jsonify(output), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500





@app.route('/activity_types', methods=['GET'])
def get_activity_types():
    """
    Retrieve activity types for all buildings.
    """
    try:
        query = """
        SELECT ?building ?activityType WHERE {
            ?building a <https://brickschema.org/schema/1.1/Brick#Building> ;
                      <https://brickschema.org/schema/1.1/Brick#hasActivityType> ?activityType .
        }
        """
        results = graph.query(query)
        output = [{"building": str(row.building), "activityType": str(row.activityType)} for row in results]
        return jsonify(output), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/normalized_energy', methods=['GET'])
def get_normalized_energy():
    """
    Retrieve normalized energy consumption for all buildings.
    """
    try:
        query = """
        SELECT ?building ?normalizedConsumption WHERE {
            ?building a <https://brickschema.org/schema/1.1/Brick#Building> ;
                      <https://brickschema.org/schema/1.1/Brick#normalizedEnergyConsumption> ?normalizedConsumption .
        }
        """
        results = graph.query(query)
        output = [{"building": str(row.building), "normalizedConsumption": str(row.normalizedConsumption)} for row in results]
        return jsonify(output), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/recent_buildings', methods=['GET'])
def get_recent_buildings():
    """
    Retrieve buildings constructed after a given year.
    Use the query parameter 'year' (e.g., /recent_buildings?year=2000).
    """
    try:
        year = request.args.get('year', None)
        if not year:
            return jsonify({"error": "Please provide a 'year' query parameter"}), 400

        query = f"""
        SELECT ?building ?yearBuilt WHERE {{
            ?building a <https://brickschema.org/schema/1.1/Brick#Building> ;
                      <https://brickschema.org/schema/1.1/Brick#yearBuilt> ?yearBuilt .
            FILTER(?yearBuilt > {year})
        }}
        """
        results = graph.query(query)
        output = [{"building": str(row.building), "yearBuilt": str(row.yearBuilt)} for row in results]
        return jsonify(output), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500







@app.route('/', methods=['GET'])
def index():
    """
    Root endpoint to provide API information.
    """
    return jsonify({
        "message": "Welcome to the Building Energy API",
        "endpoints": {
            "/query": "POST endpoint to execute SPARQL queries",
            "/buildings": "GET endpoint to retrieve all buildings",
            "/energy_usage": "GET endpoint to retrieve total energy usage per building",
            "/ventilation_systems": "GET endpoint to retrieve ventilation systems",
            "/activity_types": "GET endpoint to retrieve activity types of buildings",
            "/normalized_energy": "GET endpoint to retrieve normalized energy consumption",
            "/recent_buildings?year=<year>": "GET endpoint to retrieve buildings constructed after a given year"
        }
    }), 200


## http://127.0.0.1:5000/building_energy?building=Bureskolan_%26_Bure%C3%A5_Badhus
@app.route('/building_energy', methods=['GET'])
def get_building_energy():
    """
    Retrieve total energy consumption for a specific building.
    Query parameter: ?building=<BuildingName>
    Example: /building_energy?building=Bureskolan_&_Bureå_Badhus
    """
    try:
        # Get the building name from query parameters
        building_name = request.args.get('building', None)
        if not building_name:
            return jsonify({"error": "Please provide a building name using the 'building' query parameter"}), 400

        # Construct SPARQL query to fetch total energy
        query = f"""
        PREFIX brick: <https://brickschema.org/schema/1.1/Brick#>
        PREFIX ex: <http://example.org/building#>

        SELECT ?totalEnergy WHERE {{
          <http://example.org/building#{building_name}> a <https://brickschema.org/schema/1.1/Brick#Building> ;
                             <https://brickschema.org/schema/1.1/Brick#hasPart> ?energyUsage .
          ?energyUsage a <https://brickschema.org/schema/1.1/Brick#Energy_Usage> ;
                       <https://brickschema.org/schema/1.1/Brick#totalEnergy> ?totalEnergy .
        }}
        """

        # Execute the SPARQL query
        results = graph.query(query)

        # Parse the results
        output = [{"building": building_name, "totalEnergy": float(row.totalEnergy)} for row in results]

        # If no results found
        if not output:
            return jsonify({"error": f"No energy data found for building '{building_name}'"}), 404

        return jsonify(output), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500





if __name__ == '__main__':
    app.run(debug=True)
