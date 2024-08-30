const express = require('express');
const { execFile } = require('child_process');
const app = express();
const port = 8080;

const cors = require('cors');
app.use(cors());

app.use(express.json()); // Middleware to parse JSON bodies

app.post('/get-path', (req, res) => {
    const { origin, destination, travelMode } = req.body;

    // Assuming the corrected script path
    const scriptPath = '../orchestrator/shade_combination.py';

    // Prepare arguments to pass to the Python script
    const args = [origin.join(','), destination.join(','), travelMode];

    execFile('python3', [scriptPath, ...args], (error, stdout, stderr) => {
        if (error) {
            console.error('stderr', stderr);
            return res.status(500).send('Error running Python script');
        }

        try {
            // Parse the JSON output from the Python script
            // console.log(stdout)
            const pathsObject = JSON.parse(stdout);
            const response = Object.entries(pathsObject).map(([typeOfPath, data]) => ({
                typeOfPath: typeOfPath.toLowerCase(), // Convert "Shortest" to "shortest", etc.
                path: data.path, // This is a list of lists of coordinates
                length: data.length // Total length of the path
            }));

            // Send the structured response
            res.json(response);
        } catch (error) {
            console.error('Error parsing Python script output:', error);
            res.status(500).send('Error parsing Python script output');
        }
    });
});



app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
});
