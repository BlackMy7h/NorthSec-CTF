const express = require('express');
const ejs = require('ejs');

const app = express();

// Middleware to parse URL-encoded bodies (for the login form)
app.use(express.urlencoded({ extended: true }));

app.set('view engine', 'ejs');

const mamno3 = [
    "outputFunctionName",
    "outputFunctionName",
    "outputFunctionName",
    "outputFunctionName",
    "outputFunctionName",
    "outputFunctionName",
    "outputFunctionName",
    "localsName",
    "destructuredLocals"
]

app.get('/', (req, res) => {
    return res.render('index');
});

// Route to display the admin login page
app.get('/admin', (req, res) => {
    // Pass error message if redirected back here
    return res.render('admin_login', { error: req.query.error });
});

// Route to handle the admin login attempt
app.post('/admin/login', (req, res) => {
    const { username, password } = req.body;

    // --- ALWAYS FAIL LOGIN --- 
    // Intentionally incorrect password check or no check at all.
    // This ensures no one can log in, regardless of the password.
    console.log(`Admin login attempt: User='${username}' Pass='${password}' - Access Denied.`); 
    
    // Redirect back to the login page with an error message
    // We NEVER render 'admin_panel.ejs'
    return res.redirect('/admin?error=Invalid%20credentials');
    
    // Alternative: Redirect to home page silently
    // return res.redirect('/'); 
});

app.get('/dardmana', (req, res) => {
    
    const data = JSON.stringify(req.query);

    if (mamno3.find((item) => data.includes(item))) {
        return res.status(400).send('wach bghiti Zit Ziton ? , Contact Molzri3 ! ');
    }

    return res.render('dardmana', {
        ...JSON.parse(data),
        cache: false
    });
});

app.listen(3000, () => {
    console.log('Server listening on port 3000')
})