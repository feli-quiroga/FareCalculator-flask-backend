from flask import Flask, request, jsonify
from flask_cors import CORS

# app instance
app = Flask(__name__)
CORS(app)


# /api/home
@app.route("/api/home", methods={'GET', 'POST'})
def handle_form_submission():
    try:
        # Assuming the data is sent as JSON
        form_data = request.get_json()

        # Access individual fields of the data passed
        trainLine = form_data.get('trainLine')
        stop = form_data.get('stop')
        times = form_data.get('times')
        local_transit = form_data.get('localTransit')
        ttc = form_data.get('ttc')

        # Print the data:
        print('Train Line: ', trainLine)
        print('Stop:', stop)
        print('Times:', times)
        print('Local Transit:', local_transit)
        print('TTC:', ttc)

        # Now onto the program that will process the data itself:

        # Arrays containing the Train Lines, Train Stations, Fares, and Toronto Stations
        trains = ["Lakeshore East","Lakeshore West","Barrie","Milton","Kitchener","Richmond Hill","Stouffville"]
        # Important: List containing lists containing every possible Go Train Station
        trainstations = [["Union","Danforth","Scarborough","Eglinton","Guildwood","Rouge Hill","Pickering","Ajax","Whitby","Oshawa"],["Union", "Exhibition","Mimico","Long Branch","Port Credit","Clarkson","Oakville","Bronte","Appleby","Burlington","Aldershot","Hamilton"],["Union","Downsview Park","Rutherford","Maple","King City","Aurora","Newmarket","East Gwillimbury","Bradford","Barrie South","Allandale Waterfront"],["Union","Kipling","Dixie","Cooksville","Erindale","Streetsville","Meadowvale","Lisgar","Milton"],["Union","Bloor","Weston","Etobicoke North","Malton","Bramalea","Brampton","Mount Pleasant","Georgetown","Acton","Guelph Central","Kitchener"],["Union","Old Cummer","Langstaff","Richmond Hill","Gormley","Bloomington"],["Union","Kennedy","Agincourt","Milliken","Unionville","Centennial","Markham","Mount Joy","Stouffville","Old Elm"]]
        # Important: List containing lists containing the fare for each Go Train Station, it is in the same order as list above
        fares = [[0,2.64,2.64,3.69,3.69,4.74,5.64,6.12,6.84,7.35],[0,2.64,2.64,2.85,4.29,5.31,5.82,6.66,7.23,7.38,7.89,8.16],[0,3.69,4.89,4.89,5.61,6.09,6.69,6.84,7.38,9.15,9.48],[0,3.39,4.29,4.29,5.31,5.88,6.24,6.66,7.35],[0,2.64,3.39,3.39,5.22,5.73,6.18,6.96,7.50,8.55,9.69,11.64],[0,3.69,4.83,4.89,5.61,6.03],[0,2.64,4.62,5.43,5.55,5.64,5.64,6.03,6.84,6.84]]
        # Set containing all train stations located in Toronto to account for the 2-hour ride free on TTC
        toronto = {"Union","Danforth","Scarborough","Eglinton","Guildwood","Rouge Hill","Exhibition","Mimico","Long Branch","Downsview Park","Kipling","Bloor","Weston","Etobicoke North","Old Cummer","Langstaff","Kennedy","Agincourt"}

        # Nested function that will gather the data
        def get_data():
            useTTC = False
            useLocalTransit = False
            timesInt = int(times)
            # Local temp variables to determine the fare assigned
            fareindex = 0
            fareindex2 = 0

            if (local_transit == 'yes'):
                useLocalTransit = True
            
            if (ttc == 'yes'):
                useTTC = True
            
            # Loop to determine user's appropiate fare
            for line in trainstations:
                for stationf in line:
                    if(stationf == stop): # Loop has found your train station
                        # Using the indexes previously declared it will generate a new list containing all the fares of your train line and subsequently find the fare corresponding to your station:
                        fareline = fares[fareindex]
                        fare = fareline[fareindex2]
                    fareindex2 +=1
                fareindex +=1
                fareindex2 = 0 # Reset the fareindex2 to 0 because it did not find a match in this train line
            
            # All data is gathered now return the data
            return useTTC, useLocalTransit, timesInt, fare
        
        # Function that will do all the math
        def calculate_trans():
            # variables containing data
            line = trainLine
            station = stop
            ttc, localtransit, times, fare = get_data()
            times  = (times*2)*4 # Calculate how many times a month user uses transportation based on inputted value
            ttcfare = 2.25
            monthly_cost = 0 # Monthly cost is initialized as 0
            # The three following if/else account for all possible variants(ie. User takes the subway or not, uses local transit or not)
            # The way Go Transit calculates your fare is by the number is instances you use Go Train a month
            # If you use Go Train 1 to 30 times in a month you pay full fare
            # If you use Go Train between 31 and 40 times in a month your fare drops 91.84%
            # If you use Go Train more than 40 times you ride for free
            if(ttc == True):
                if(times <= 30): # User rides less than 31 times a month so pays full fare
                    monthly_cost = fare*times + ttcfare*times
                elif(times >30 and times <=40): # User rides between 31 and 40 times so those extra rides have 91.84% discount
                    monthly_cost = fare*30 + (0.0816*fare)*(times - 30) + ttcfare*times
                else: # User rides more than 40 times so rides the rest for free
                    monthly_cost = fare*30 + (0.0816*fare)*10 + ttcfare*times
            elif(station in toronto and localtransit):
                if (times <= 30):
                    monthly_cost = fare * times + ttcfare * times
                elif (times > 30 and times <= 40):
                    monthly_cost = fare * 30 + (0.0816 * fare) * (times - 30) + ttcfare * times
                else:
                    monthly_cost = fare * 30 + (0.0816 * fare) * 10 + ttcfare * times
            elif(ttc == False):
                if (times <= 30):
                    monthly_cost = fare * times
                elif (times > 30 and times <= 40):
                    monthly_cost = fare * 30 + (0.0816 * fare)*(times - 30)
                else:
                    monthly_cost = fare * 30 + (0.0816 * fare) * 10
            # Restate the train line and station user gets on, as well as how many times a month user goes to campus
            print()
            print(f"You use the {line} line and get on {station} station.")
            print(f"You go to Ryerson a total of {times} times a month.")
            print()
            # Print final result of monthly_cost rounded to 2 decimals
            print(f"You will be spending ${round(monthly_cost, 2)} a month in transportation alone to get to campus")
            return round(monthly_cost, 2)

        monthly_cost = calculate_trans()
        
        # Finally return the data back to front-end
        return jsonify({"monthly_cost": monthly_cost})
        # Return a response
    except Exception as e:
        # Handle exceptions appropriately
        return jsonify({'error': str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True, port=8080)