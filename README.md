# Yahoo-Finance-API-client
Salient Features of YF-API_client: 
1. Users can to select multiple stocks.
2. In each stock tab, the users are be able to select date range make request to fetch High, Low, Mean, Median stock prices. 
3. The client models the obtained data from the API and calculates the mean and variance and shows these values.
4. It also is capable of finding the times and time stamps where stock moved outside the bounded range (mean + std. deviation, mean - std. deviation) and shows the  only the first instance when it had happened.
5. Along with showing date-time stamps when it moved out of that range, the client also shows the time-stamp when it returned in the range for the first time.


* Home Page: Provides option to select from given Stock options and request for data in date range.
<p align="center"><img width="100%" height="500px" src="https://github.com/adarsh2104/Yahoo-Finance-API-client/blob/main/Visuals/Home_page.png"></img></p>


* Result Page: Shows the calculated statastical results for all requtested Stocks within the data range based on the data returned by the Yahoo-finance API.  
<p align="center"><img width="100%" height="500px" src="https://github.com/adarsh2104/Yahoo-Finance-API-client/blob/main/Visuals/Stock_search_results.png"></img></p> 

### Stacks and Libraries Used:
* Python 3.7
* Django 3.2
* Requests 2.25
* HTML/django templates

### NOTE: To test this project,Kindly visit and register at https://rapidapi.com/blog/how-to-use-the-yahoo-finance-api/ to get your own API Key.
