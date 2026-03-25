const express = require('express');
const app = express();
const port = process.env.PORT || 3000;
const Cloudant = require('@cloudant/cloudant');

// Initialize Cloudant connection with IAM authentication
async function dbCloudantConnect() {
    try {
        const cloudant = Cloudant({
            plugins: { iamauth: { iamApiKey: "FA83yCzfYzrd0XRoNkHYpyqoX_L_jEIFjYoQmbUX97Dk" } }, // Replace with your IAM API key
            url: "https://7aa5ee38-cc9d-4038-8268-a931081002b2-bluemix.cloudantnosqldb.appdomain.cloud", // Replace with your Cloudant URL
        });

        const db = cloudant.use('dealerships');
        console.info('Connect success! Connected to DB');
        return db;
    } catch (err) {
        console.error('Connect failure: ' + err.message + ' for Cloudant DB');
        throw err;
    }
}

let db;

(async () => {
    db = await dbCloudantConnect();
})();

app.use(express.json());

// Define a route to get all dealerships with optional state and ID filters
app.get('/api/dealership', (req, res) => {
    const { state, id } = req.query;
    // Create a selector object based on query parameters
    const selector = {};
    
    if (state) {
        selector.state = state;
        const queryOptions = {
            selector,
            limit: 10, // Adjust the limit as needed
        };
        db.find(queryOptions, (err, body) => {
            if (err) {
                console.error('Error fetching state:', err);
                res.status(500).json({ error: 'An error occurred while fetching dealerships from a particular state.' });
            } else {
                const dealershipstate = body.docs;
                if (dealershipstate.length > 0) {
                    res.json(dealershipstate);   
                } else{
                    res.status(404).json({ error: "State doesn't exist"});    
                }
                }});
            } 

    
    else if (id) {
        selector.id = parseInt(id, 10); // Filter by "id" with a value of 1
        const queryOptions = {
            selector,
            limit: 10, // Adjust the limit as needed
        };
        db.find(queryOptions, (err, body) => {
            if (err) {
                console.error('Error fetching dealership ID:', err);
                res.status(500).json({ error: 'An error occurred while fetching dealerships with a particular ID.' });
            } else {
                const dealershipid = body.docs;
                if (dealershipid.length > 0) {
                    res.json(dealershipid);
                } else{
                    res.status(404).json({ error: "Dealership with such ID does not exist"});    
                }
                }});
            }
    else {
        const queryOptions = {
        selector,
        limit: 10, // Limit the number of documents returned to 10
        };

        db.find(queryOptions, (err, body) => {
        if (err) {
        console.error('Error fetching dealerships:', err);
        res.status(500).json({ error: 'An error occurred while fetching dealerships.' });
        } 
        else {
        const dealerships = body.docs;
            if (dealerships.length > 0) {
            res.json(dealerships);
        }
            else{
            res.status(404).json({ error: 'Database is empty'});    
        }
        }
    });
}
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});