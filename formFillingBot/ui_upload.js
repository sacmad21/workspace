import React, { useState } from "react";
import "./App.css";


const App = () => {

  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [file, setFile] = useState(null);

  const sendMessage = async () => {
    if (userInput.trim() === "" && !file) return;

    const userMessage = {
      sender: "user",
      text: userInput || (file ? "File uploaded" : ""),
    };

    // Add user message to chat
    setMessages((prev) => [...prev, userMessage]);

    try {
      let body = {
        entry: [
          {
            changes: [
              {
                value: {
                  messages: [],
                },
              },
            ],
          },
        ],
      };

      
      // Handle text messages
      if (userInput.trim() !== "") {
        body.entry[0].changes[0].value.messages.push({
          from: "user_id",
          text: { body: userInput },
          type: "text",
        });
      }

      // Handle file upload
      if (file) {
        // Simulate a file upload and get a media ID
        const formData = new FormData();
        formData.append("file", file);

        const uploadResponse = await fetch("http://localhost:7071/api/UploadFile", {
          method: "POST",
          body: formData,
        });

        const uploadData = await uploadResponse.json();
        const mediaId = uploadData.media_id; // Simulated media ID

        body.entry[0].changes[0].value.messages.push({
          from: "user_id",
          document: {
            id: mediaId,
            caption: "File upload simulation",
          },
          type: "document",
        });
      }

      // Simulate sending the request to the WhatsApp Bot
      const response = await fetch("http://localhost:7071/api/WhatsAppBot", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (data.status === "success") {
        // Add bot response to chat
        const botMessage = {
          sender: "bot",
          text: "Message processed successfully. Check logs for more info.",
        };
        setMessages((prev) => [...prev, botMessage]);
      } else {
        // Handle error from bot
        const errorMessage = {
          sender: "bot",
          text: `Error: ${data.message || "Something went wrong."}`,
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      // Add error message to chat
      const errorMessage = {
        sender: "bot",
        text: `Error: ${error.message}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    }

    // Clear user input and file
    setUserInput("");
    setFile(null);
  };

  return (
    <div className="App">
      <div className="chat-window">
        <div className="chat-header">WhatsApp Hook Testing</div>
        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`chat-message ${msg.sender === "bot" ? "bot" : "user"}`}
            >
              {msg.text}
            </div>
          ))}
        </div>
        <div className="chat-input">
          <input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Type your message here..."
          />
          <input
            type="file"
            onChange={(e) => setFile(e.target.files[0])}
            className="file-upload"
          />
          <button onClick={sendMessage}>Send</button>
        </div>
      </div>
    </div>
  );
};

export default App;
