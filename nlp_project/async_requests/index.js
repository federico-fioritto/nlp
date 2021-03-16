var express = require('express');
var app = express();
const bodyParser = require('body-parser');

app.use(bodyParser.json({limit: '50mb'}));
app.use(bodyParser.urlencoded({limit: '50mb', extended: false}));

app.use('/', require('./route.js'));

var server = require('http').Server(app);
var port = process.env.PORT || 5111
server.listen(port, function() {
  console.log('Running server on', port)
});