const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const multer = require('multer');
const session = require('express-session');
const http = require('http');
const socketIO = require('socket.io');


const sdk = require("microsoft-cognitiveservices-speech-sdk");

require('dotenv').config();

const speechConfig = sdk.SpeechConfig.fromSubscription(process.env.API_KEY, "eastus");
speechConfig.speechRecognitionLanguage = "en-US";


const app = express();
const server = http.createServer(app);
const io = socketIO(server);

app.use(session({
  secret: 'your-secret-key', // Change this to a random secret key
  resave: false,
  saveUninitialized: false
}));  

const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

const PORT = process.env.PORT || 3000;

// Middleware
app.use(bodyParser.json({ limit: '50mb' })); // Adjust the limit as per your requirement
app.use(bodyParser.urlencoded({ extended: true }));


const audioDirectory = path.join(__dirname, 'audio');
console.log(audioDirectory);
if (!fs.existsSync(audioDirectory)) {
  fs.mkdirSync(audioDirectory);
}


app.use(express.static(path.join(__dirname, 'public')));


// Set up your view engine and views directory
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));



app.post('/upload', upload.single('audio'), async (req, res) => {
  try {
      // Check if a file is uploaded
      if (!req.file) {
          return res.status(400).send('No audio file uploaded');
      }

      // Save the audio file to the server
      const filePath = path.join(audioDirectory, `sampleaudio.wav`);

      fs.writeFileSync(filePath, req.file.buffer);


      console.log('Audio saved successfully:', filePath);

      // Call the fromFile function with the correct file path
      //fromFile(filePath);

      res.sendStatus(200);
  } catch (error) {
      console.error('Error saving audio to the server:', error);
      res.status(500).send('Internal Server Error');
  }
});


io.on('connection', (socket) => {
  console.log('Client connected');

  socket.on('audio', (audioData) => {
      // Handle audio data (e.g., broadcast to other clients, etc.)
      socket.broadcast.emit('audio', audioData);
  });

  socket.on('disconnect', () => {
      console.log('Client disconnected');
  });
});




async function fromFile() {
  console.log('processing');
  //let audioConfig = sdk.AudioConfig.fromWavFileInput(fs.readFileSync('D:\Users\surya\Desktop\face - Copy\server\audio\audiosample.wav'));
  
  let audioFilePath = path.join(__dirname,'audio', 'sampleaudio.wav');
  let audioConfig = sdk.AudioConfig.fromWavFileInput(fs.readFileSync(audioFilePath));

  let speechRecognizer = new sdk.SpeechRecognizer(speechConfig, audioConfig);
  console.log('processing 1 ');

  return new Promise((resolve, reject) => {
    speechRecognizer.recognizeOnceAsync(result => {
      switch (result.reason) {
        case sdk.ResultReason.RecognizedSpeech:
          console.log('processing 2 ');
          console.log(`RECOGNIZED: Text=${result.text}`);
          resolve(result.text); // Resolve the promise with the recognized text
          break;
        case sdk.ResultReason.NoMatch:
          console.log('processing 3 ');
          console.log("NOMATCH: Speech could not be recognized.");
          resolve(null); // Resolve with null if no match
          break;
        case sdk.ResultReason.Canceled:
          const cancellation = sdk.CancellationDetails.fromResult(result);
          console.log(`CANCELED: Reason=${cancellation.reason}`);

          if (cancellation.reason == sdk.CancellationReason.Error) {
            console.log(`CANCELED: ErrorCode=${cancellation.ErrorCode}`);
            console.log(`CANCELED: ErrorDetails=${cancellation.errorDetails}`);
            console.log("CANCELED: Did you set the speech resource key and region values?");
            reject('Speech recognition error'); // Reject the promise with an error
          }
          break;
      }
      speechRecognizer.close();
    });
  });
}




// Routes
app.get('/', (req, res) => {
  res.render('index');
});

// Save image route
const request = require('request');
const { Console } = require('console');


app.post('/save-image', (req, res) => {
    const base64Data = req.body.image.replace(/^data:image\/png;base64,/, '');
    const fileName = `image_user.png`; // Use counter in filename
    const filePath = path.join(__dirname, 'images', fileName);
  
    fs.writeFile(filePath, base64Data, 'base64', err => {
      if (err) {
        console.error('Error saving image:', err);
        res.status(500).json({ error: 'Failed to save image' });
      } else {
        console.log('Image saved successfully');
        // Increment counter for next image
        //const detectedNames = null;
        // Make HTTP request to the detection URL
        // const detectionURL = `http://127.0.0.1:5000/detect/${fileName}`;
        // request(detectionURL, (error, response, body) => {
        //   if (!error && response.statusCode == 200) {
        //     const detectedNames = JSON.parse(body);
        //     console.log('Detected Names:', detectedNames);
        //     res.render('voice', { detectedNames  });
        //   } else {
        //     console.error('Error calling detection URL:', error);
        //     res.status(500).json({ error: 'Failed to get detection result' });
        //   }
        // });


        

      }
    });

  });







app.post('/save-audio', upload.single('audio'), (req, res) => {
  // File uploaded successfully
  console.log('Audio file uploaded successfully')
  res.send('Audio file uploaded successfully');
});



app.get('/detect' , (req , res)=>{

  const fileName = `image_user.png`; // Use counter in filename
    const filePath = path.join(__dirname, 'images', fileName);
    const detectionURL = `http://127.0.0.1:5000/detect/image/${fileName}`;
        request(detectionURL, (error, response, body) => {
          if (!error && response.statusCode == 200) {
            const detectedNames = JSON.parse(body);
            req.session.photoname = detectedNames;
            console.log('Detected Names:', detectedNames);
            res.render('voice' , {detectedNames}) ;

          } else {
            console.error('Error calling detection URL:', error);
            res.status(500).json({ error: 'Failed to get detection result' });
          }
        })
})
  


app.get('/validate', async (req, res) => {
  try {
    const recognizedText = await fromFile();
    req.session.voicetext = recognizedText;
    console.log('Recognized Text:', recognizedText);
    console.log(req.session.photoname + " " + req.session.voicetext);

    //http://127.0.0.1:5000/detect/audio
    var detectedvoice = "";

    const detectionURL = `http://127.0.0.1:5000/detect/audio`;
    request(detectionURL, (error, response, body) => {
      if (!error && response.statusCode == 200) {
        detectedvoice = JSON.parse(body);
        console.log('Detected voice name :', detectedvoice);
        console.log("deteted :  Name - "+  req.session.photoname + " ; Voicetext -  " + req.session.voicetext + " ; Detected VOice - " + detectedvoice);
        req.session.voicename = detectedvoice;

        // Redirect to /checkAuth after setting req.session.voicename
        res.redirect('/checkAuth');
      } else {
        console.error('Error calling detection URL:', error);
        res.status(500).json({ error: 'Failed to get detection result' });
      }
    });

  } catch (error) {
    console.error('Speech recognition error:', error);
    res.status(500).send('Speech recognition error');
  }
});

function processString(inputString) {
  // Remove spaces and full stops
  inputString = String(inputString).replace(/[.\s]/g, '').toLowerCase();
  
  // Convert to uppercase
  
  
  return inputString;
}


function compareWords(word1, word2) {
  // Remove dots and spaces, and convert to lowercase
  const cleanWord1 = String(word1).replace(/[.\s]/g, '').toLowerCase();
  const cleanWord2 = String(word2).replace(/[.\s]/g, '').toLowerCase();
  
  // Check if the two cleaned words are the same
  return cleanWord1 === cleanWord2;
}
var surya = "i ate chicken yesterday";
  var rattan = "strongest avenger";
  var praki = "I am from chennai";


  var variableMap = {
    'surya': surya,
    'rattan': rattan,
    'praki': praki
  };

app.get('/checkAuth', (req, res) => {

  var ninde = req.session.photoname;
  
  console.log("expected :  "+ninde + "     pass :   "+ variableMap[ninde] + "       " );
  console.log("uhdjf   " + compareWords(processString(req.session.voicetext) , processString(variableMap[ninde])));
  //res.send(req.session.photoname + "  " + req.session.voicetext + "  " + req.session.voicename + "     " + compareWords(req.session.photoname ,req.session.voicename ));
  if(compareWords(req.session.photoname ,req.session.voicename ) && compareWords(processString(req.session.voicetext) , processString(variableMap[ninde])) )
  {
    res.send("Authenticated - Valid Credintials");
  }
  else{
    res.send("Invalid  Credintials Please try again");
  }
   
  

});



// Start server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
