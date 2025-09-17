'use client';
import { useState } from "react";
import Link from 'next/link';

export default function UploadCV() {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [status, setStatus] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] || null);
    setStatus("");
    setMessage("");
    setError("");
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragActive(true);
  };
  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragActive(false);
  };
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setStatus("");
      setMessage("");
      setError("");
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("cv", file);

    setStatus("Processing...");
    setMessage("");
    setError("");

    const res = await fetch("/api/upload-cv", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    if (res.ok && data.success) {
      setStatus("Complete!");
      setMessage(data.message || "Job search completed successfully.");
    } else {
      setStatus("Failed");
      setError(data.error || "An unknown error occurred.");
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-8">
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Upload CV to Start a New Job Search</h2>
        <p className="text-gray-600 mb-4">Upload your CV, and we'll use a local AI model to determine the best job title to search for, then automatically import relevant jobs.</p>
        <div
          className={`border-2 border-dashed rounded-lg p-6 flex flex-col items-center justify-center transition-colors duration-200 cursor-pointer mb-4 ${dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => document.getElementById('cv-upload-input')?.click()}
        >
          <input
            id="cv-upload-input"
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            className="hidden"
          />
          <span className="text-gray-500">Drag & drop your PDF here, or <span className="text-blue-600 underline">choose file</span></span>
          {file && <span className="mt-2 text-green-600">{file.name}</span>}
        </div>
        <button
          onClick={handleUpload}
          disabled={!file || status === "Processing..."}
          className={`w-full py-2 px-4 rounded font-semibold transition-colors duration-200 ${
            file && status !== "Processing..."
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {status === "Processing..." ? "Processing..." : "Upload and Search"}
        </button>
      </div>

      {status && status !== "Processing..." && (
        <div className={`bg-white shadow rounded-lg p-6 mb-6 ${error ? 'border-red-500' : 'border-green-500'} border-l-4`}>
          <h3 className="text-lg font-semibold mb-2">{status}</h3>
          {message && <p className="text-gray-700">{message}</p>}
          {error && <p className="text-red-700">{error}</p>}
          {message && (
            <Link href="/" className="inline-block mt-4 bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700">
              View Imported Jobs
            </Link>
          )}
        </div>
      )}
    </div>
  );
}
