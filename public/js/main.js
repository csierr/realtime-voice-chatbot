const ws           = new WebSocket("ws://localhost:8000/ws");
const chatbox      = document.getElementById("chatbox");
const audioElement = new Audio();
let mediaSource    = new MediaSource();
audioElement.src   = URL.createObjectURL(mediaSource);

let sourceBuffer;
let queue = [];
let isBufferUpdating = false;
let readyToPlay = false;

audioElement.addEventListener("ended", () => {
    // When the audio finishes, restart the pipeline to receive another MediaSource
    console.log("🔁 Reproduction completed, restarting pipeline...");
    resetAudioPipeline();
});

mediaSource.addEventListener("sourceopen", () => {
    // Create buffer for MPEG data
    console.log("📡 MediaSource open");
    sourceBuffer = mediaSource.addSourceBuffer('audio/mpeg');

    // Process buffer when updating
    sourceBuffer.addEventListener("updateend", () => {
        console.log("🧩 Buffer updated, processing queue...");
        isBufferUpdating = false;
        processQueue();
        playAudioIfReady();
    });

    sourceBuffer.addEventListener("error", (e) => {
        console.error("❌ Error in sourceBuffer:", e);
    });
});

ws.onmessage = async (event) => {
    const msg = JSON.parse(event.data);

    if (msg.type === "audio") {
        // Receive base64 audio chunk, convert to ArrayBuffer and add to queue
        console.log("🎧 Audio chunk received");
        const base64 = msg.data;
        const binaryString = atob(base64);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);

        for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        if (sourceBuffer) {
            queue.push(bytes.buffer);
            console.log("📥 Audio added to queue");
            processQueue();
        } else {
            console.warn("⚠️ sourceBuffer is not ready yet");
        }

    } else if (msg.type === "audio_done") {
        // Signal that all audio has been sent → mark MediaSource as completed
        console.log("✅ Full audio received, waiting for the queue to empty...");
        readyToPlay = true;

        if (mediaSource.readyState === "open") {
            try {
            if (!mediaSource.sourceBuffers[0].updating) {
                mediaSource.endOfStream();
            }
            console.log("🔚 MediaSource marked as completed...");
            } catch (e) {
            console.warn("⚠️ Error closing MediaSource:", e);
            }
        }
        playAudioIfReady();
    
    } else if (msg.text) {
        // Show text answer from the model
        const div = document.createElement("div");
        div.className = "msg bot";
        div.innerText = "🤖 " + msg.text;
        chatbox.appendChild(div);
        chatbox.scrollTop = chatbox.scrollHeight;
    }
};

ws.onerror = (e) => {
    console.error("⚠️ WebSocket error:", e);
};

ws.onclose = () => {
    console.warn("🔌 WebSocket disconnected");
};

/**
 * Processes and plays back audio chunks received from backend via WebSocket
 * Queues the data in the sourceBuffer
 */
function processQueue() {
    if (sourceBuffer && !sourceBuffer.updating && queue.length > 0) {
        console.log(`📦 Processing buffered, queued items: ${queue.length}`);
        isBufferUpdating = true;
    try {
        sourceBuffer.appendBuffer(queue.shift());
    } catch (e) {
        console.error("❌ Error using appendBuffer:", e);
    }
    }
}

/**
 * Resets the entire audio pipeline for a new playback
 */
function resetAudioPipeline() {
    console.log("♻️ Restarting audio pipeline...");

    // Pause and clear current audio
    audioElement.pause();
    audioElement.src = "";
    mediaSource = new MediaSource();
    audioElement.src = URL.createObjectURL(mediaSource);

    // Clear references and statuses
    sourceBuffer = null;
    queue = [];
    isBufferUpdating = false;
    readyToPlay = false;

    mediaSource.addEventListener("sourceopen", () => {
    console.log("📡 New MediaSource open");
    try {
        sourceBuffer = mediaSource.addSourceBuffer('audio/mpeg');
        sourceBuffer.addEventListener("updateend", () => {
        console.log("🧩 Buffer updated, processing queue...");
        isBufferUpdating = false;
        processQueue();
        playAudioIfReady();
        });
        sourceBuffer.addEventListener("error", (e) => {
        console.error("❌ Error in sourceBuffer:", e);
        });
    } catch (err) {
        console.error("⚠️ Error creating sourceBuffer:", err);
    }
    });
}

/**
 * If the audio_done signal was received, play back audio
 */
function playAudioIfReady() {
    if (readyToPlay) {
        console.log("Calling audioElement.play()");
        audioElement.play().then(() => {
            console.log("▶️ Reproduction started");
        }).catch((err) => {
            console.warn("⚠️ Error playing audio:", err);
        });
        readyToPlay = false;
    }
}

/**
 * Send text message to backend via WebSocket
 */
function sendText() {
    const input = document.getElementById("textInput");
    const message = input.value;
    ws.send(JSON.stringify({ type: "text", data: message }));
    const div = document.createElement("div");
    div.className = "msg user";
    div.innerText = "🧑 " + message;
    chatbox.appendChild(div);
    input.value = "";
    chatbox.scrollTop = chatbox.scrollHeight;
}


function startRecording() {
    // Future: Use MediaRecorder and send the audio in base64 to the WebSocket
    alert("🎤 Recording not yet implemented here");
}

document.getElementById("sendBtn").addEventListener("click", sendText);
document.getElementById("talkBtn").addEventListener("click", startRecording);