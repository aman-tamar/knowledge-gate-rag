import { useState, useRef, useEffect } from "react";
import axios from "axios";

function App() {
  const [messages, setMessages] = useState([
    { role: "ai", content: "Upload a PDF and start chatting " },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  const chatEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // ---------------- SEND MESSAGE ----------------
  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);

    const question = input;
    setInput("");
    setLoading(true);

    // placeholder message
    let aiMessage = { role: "ai", content: "" };
    setMessages((prev) => [...prev, aiMessage]);

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let done = false;
      let fullText = "";

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;

        const chunk = decoder.decode(value);
        fullText += chunk;

        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1].content = fullText;
          return updated;
        });
      }
    } catch (error) {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1].content =
          "Error connecting to backend ";
        return updated;
      });
    }

    setLoading(false);
  };

  // ---------------- UPLOAD PDF ----------------
  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    setMessages((prev) => [
      ...prev,
      { role: "ai", content: " Processing PDF..." },
    ]);

    try {
      await axios.post("http://127.0.0.1:8000/upload_pdf", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setMessages((prev) => [
        ...prev,
        { role: "ai", content: " PDF processed! You can now ask questions." },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "ai", content: " Failed to process PDF" },
      ]);
    }

    setUploading(false);
  };

  return (
    <div className="h-screen flex bg-[#202123] text-white">

      {/* SIDEBAR */}
      <div className="w-64 bg-[#202123] border-r border-gray-700 flex flex-col p-4 gap-4">
        <button
          className="w-full bg-[#343541] p-3 rounded hover:bg-[#40414f]"
          onClick={() => window.location.reload()}
        >
          ➕ New Chat
        </button>

        <button
          className="w-full bg-green-600 p-3 rounded hover:bg-green-700"
          onClick={handleUploadClick}
          disabled={uploading}
        >
          {uploading ? "Uploading..." : " Upload PDF"}
        </button>

        <input
          type="file"
          accept="application/pdf"
          ref={fileInputRef}
          className="hidden"
          onChange={handleFileChange}
        />
      </div>

      {/* MAIN CHAT */}
      <div className="flex-1 flex flex-col bg-[#343541]">

        {/* CHAT AREA */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`w-full flex ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-3xl px-4 py-3 rounded-lg ${
                  msg.role === "user"
                    ? "bg-[#444654]"
                    : "bg-[#3e3f4b]"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        {/* INPUT AREA */}
        <div className="border-t border-gray-700 p-4">
          <div className="max-w-3xl mx-auto flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Send a message..."
              className="flex-1 p-3 rounded bg-[#40414f] text-white outline-none"
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              disabled={loading || uploading}
            />
            <button
              onClick={handleSend}
              className="bg-green-600 px-4 py-2 rounded hover:bg-green-700"
              disabled={loading || uploading}
            >
              Send
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;