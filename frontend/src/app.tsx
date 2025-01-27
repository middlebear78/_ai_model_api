import React, { useState } from "react";
import axios from "axios";
import { PredictionResult } from "./types";
import "./App.css";

function App() {
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [image, setImage] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<string | null>(null);

  const handleDrag = (e: React.DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true);
    } else if (e.type === "dragleave") {
      setIsDragging(false);
    }
  };

  const handleDrop = async (
    e: React.DragEvent<HTMLDivElement>
  ): Promise<void> => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    const allowedTypes = ["image/jpeg", "image/png", "image/gif"];

    if (!allowedTypes.includes(file.type)) {
      alert("Please drop a valid image file (JPEG, PNG, or GIF)");
      return;
    }

    // Display the image
    setImage(URL.createObjectURL(file));

    // Upload to server
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post<PredictionResult>(
        "http://localhost:5000/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      setPrediction(response.data.prediction);
    } catch (error) {
      console.error("Error:", error);
      alert("Upload failed");
    }
  };

  return (
    <div className="App">
      <div className="content">
        <div className="header">
          <h1>Image Recognition API</h1>
        </div>

        <div
          className={`dropzone ${isDragging ? "dragging" : ""}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          {image ? (
            <div className="preview-container">
              <img src={image} alt="Uploaded" className="preview-image" />
              {prediction && (
                <div className="prediction-container">
                  <h3>Prediction: {prediction}</h3>
                </div>
              )}
            </div>
          ) : (
            <p>Drag and drop an image here</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
