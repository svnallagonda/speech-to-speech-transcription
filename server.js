const express = require('express');
const speech = require('@google-cloud/speech');
const multer = require('multer');
const cors = require('cors');
const play = require('play-dl');
const ffmpeg = require('fluent-ffmpeg');
const stream = require('stream');

const app = express();
const port = 3000;

app.use(cors());
app.use(express.json());

const storage = multer.memoryStorage();
const upload = multer({ storage });

const speechClient = new speech.SpeechClient();

// Convert video buffer to audio buffer (WEBM_OPUS)
function extractAudioFromVideoBuffer(videoBuffer) {
    return new Promise((resolve, reject) => {
        const passthroughStream = new stream.PassThrough();
        passthroughStream.end(videoBuffer);

        const chunks = [];
        ffmpeg(passthroughStream)
            .inputFormat('webm')
            .noVideo()
            .audioCodec('libopus')
            .format('webm')
            .on('error', (err) => reject(err))
            .on('data', (chunk) => chunks.push(chunk))
            .on('end', () => resolve(Buffer.concat(chunks)))
            .pipe();
    });
}

// Transcribe audio buffer with Google STT
async function transcribeAudioBuffer(audioBuffer, langCode) {
    const audioBytes = audioBuffer.toString('base64');
    const audio = { content: audioBytes };
    const config = {
        encoding: 'WEBM_OPUS',
        sampleRateHertz: 48000,
        languageCode: langCode,
        audioChannelCount: 2,
        model: 'video'
    };
    const request = { audio, config };
    const [response] = await speechClient.recognize(request);
    return response.results.map(r => r.alternatives[0].transcript).join('\n');
}

// Normalize YouTube Shorts URLs to standard watch URLs
function normalizeYouTubeUrl(url) {
    try {
        const u = new URL(url);
        if (u.hostname === 'www.youtube.com' && u.pathname.startsWith('/shorts/')) {
            const videoId = u.pathname.split('/')[2];
            if (videoId) {
                return `https://www.youtube.com/watch?v=${videoId}`;
            }
        }
    } catch (e) {
        // If URL invalid, return as is
    }
    return url;
}

// Route: Upload audio or video file (mic, audio, video)
app.post('/transcribe', upload.single('audio'), async (req, res) => {
    if (!req.file) {
        return res.status(400).send('No audio or video file uploaded.');
    }

    const langCode = req.body.langCode || 'en-US';

    try {
        if (req.file.mimetype.startsWith('video/')) {
            // Extract audio from video buffer then transcribe
            const audioBuffer = await extractAudioFromVideoBuffer(req.file.buffer);
            const transcript = await transcribeAudioBuffer(audioBuffer, langCode);
            res.json({ transcript });
        } else {
            // Directly transcribe uploaded audio file
            const transcript = await transcribeAudioBuffer(req.file.buffer, langCode);
            res.json({ transcript });
        }
    } catch (error) {
        console.error('Error transcribing uploaded file:', error);
        res.status(500).send('Transcription failed.');
    }
});

// Route: Transcribe YouTube link
app.post('/transcribe-youtube', async (req, res) => {
    let { url, langCode = 'en-US' } = req.body;

    console.log('Received YouTube URL:', url);

    if (!url) {
        return res.status(400).send('No YouTube URL provided.');
    }

    // Normalize shorts URLs to regular format
    url = normalizeYouTubeUrl(url);

    if (play.yt_validate(url) !== 'video') {
        return res.status(400).send('Invalid YouTube URL.');
    }

    try {
        const streamData = await play.stream(url, { discordPlayerCompatibility: true });
        const audioStream = streamData.stream;

        const chunks = [];
        audioStream.on('data', (chunk) => chunks.push(chunk));
        audioStream.on('error', (error) => {
            console.error('YouTube audio stream error:', error);
            if (!res.headersSent) res.status(500).send('Error fetching YouTube audio.');
        });
        audioStream.on('end', async () => {
            try {
                const audioBuffer = Buffer.concat(chunks);
                const transcript = await transcribeAudioBuffer(audioBuffer, langCode);
                res.json({ transcript });
            } catch (error) {
                console.error('Error during YouTube transcription:', error);
                if (!res.headersSent) res.status(500).send('Error transcribing YouTube audio.');
            }
        });
    } catch (error) {
        console.error('Setup error for YouTube transcription:', error);
        if (!res.headersSent) res.status(500).send('Error processing YouTube link.');
    }
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
