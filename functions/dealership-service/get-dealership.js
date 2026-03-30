const path = require('path');
require('dotenv').config({
    path: process.env.DOTENV_PATH || path.resolve(__dirname, '..', '..', '.env'),
});

const express = require('express');
const { MongoClient } = require('mongodb');

const app = express();
const port = process.env.PORT || 3000;

function sanitizeMongoUri(uri) {
    if (!uri) {
        return uri;
    }

    const match = uri.match(/^(mongodb(?:\+srv)?:\/\/[^/]+\/[^?]*)(\?.*)?$/);
    if (!match || !match[2]) {
        return uri;
    }

    const base = match[1];
    const params = new URLSearchParams(match[2].slice(1));
    const appNames = params.getAll('appName');
    if (appNames.length > 1) {
        params.delete('appName');
        params.set('appName', appNames[0]);
    }

    const query = params.toString();
    return query ? `${base}?${query}` : base;
}

const mongoUri = sanitizeMongoUri(process.env.MONGODB_URI);
const dbName = process.env.MONGODB_DB_NAME || 'dealerships_db';
const dealershipsCollectionName =
    process.env.MONGODB_DEALERS_COLLECTION || 'dealerships';

if (!mongoUri) {
    throw new Error('Missing MongoDB configuration. Set MONGODB_URI in .env.');
}

const client = new MongoClient(mongoUri);
let dealershipsCollection;

function normalizeDealershipDocuments(documents) {
    const normalized = [];
    for (const document of documents) {
        if (document && Array.isArray(document.dealerships)) {
            normalized.push(...document.dealerships);
        } else {
            normalized.push(document);
        }
    }
    return normalized.filter((document) => document && typeof document === 'object');
}

async function connectMongo() {
    try {
        await client.connect();
        const db = client.db(dbName);
        dealershipsCollection = db.collection(dealershipsCollectionName);
        console.info('Connected to MongoDB');
    } catch (error) {
        console.error('Failed to connect to MongoDB:', error);
    }
}

app.use(express.json());

app.get('/api/dealership', async (req, res) => {
    if (!dealershipsCollection) {
        return res.status(503).json({ error: 'Database connection not ready' });
    }

    const { state, id } = req.query;
    let numericId = null;
    if (id) {
        numericId = parseInt(id, 10);
        if (Number.isNaN(numericId)) {
            return res.status(400).json({ error: "'id' must be an integer" });
        }
    }

    try {
        const rawDocuments = await dealershipsCollection
            .find({}, { projection: { _id: 0 } })
            .toArray();
        const dealerships = normalizeDealershipDocuments(rawDocuments).filter(
            (dealership) => {
                if (state && dealership.state !== state) {
                    return false;
                }
                if (numericId !== null && dealership.id !== numericId) {
                    return false;
                }
                return true;
            }
        );

        if (dealerships.length === 0) {
            return res.status(404).json({ error: 'No dealerships found' });
        }

        return res.json(dealerships.slice(0, 10));
    } catch (error) {
        console.error('Error fetching dealerships:', error);
        return res
            .status(500)
            .json({ error: 'An error occurred while fetching dealerships.' });
    }
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
    connectMongo();
});
