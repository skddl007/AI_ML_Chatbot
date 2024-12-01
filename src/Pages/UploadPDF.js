import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BackgroundLines } from '../components/ui/background-lines.tsx';

const UploadPDF = () => {
  const [pdf, setPdf] = useState(null);
  const [bookName, setBookName] = useState('');
  const [authorName, setAuthorName] = useState('');
  const [contentStartPage, setContentStartPage] = useState('');
  const [contentEndPage, setContentEndPage] = useState('');
  const [chapterStartPage, setChapterStartPage] = useState('');
  const [chapterEndPage, setChapterEndPage] = useState('');
  const [error, setError] = useState('');

  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type === 'application/pdf') {
        setPdf(file);
        setError('');
      } else {
        setError('Please upload a valid PDF file');
        setPdf(null);
      }
    }
  };

  const handleUpload = () => {
    if (
      pdf &&
      bookName &&
      authorName &&
      contentStartPage &&
      contentEndPage &&
      chapterStartPage &&
      chapterEndPage
    ) {
      console.log('Uploading:', pdf);
      console.log('Book Name:', bookName);
      console.log('Author Name:', authorName);
      console.log('Content Start Page:', contentStartPage);
      console.log('Content End Page:', contentEndPage);
      console.log('Chapter Start Page:', chapterStartPage);
      console.log('Chapter End Page:', chapterEndPage);
      // Handle the PDF upload (e.g., upload to Firebase Storage)

      navigate('/chat');
    } else {
      setError('Please fill in all fields before uploading.');
    }
  };

  return (
    <div className="relative flex justify-center items-center min-h-screen bg-gradient-to-r from-gray-800 via-gray-900 to-black">
      {/* Background Lines */}
      <BackgroundLines
        className="my-background absolute top-0 left-0 w-full h-full"
        svgOptions={{ duration: 10 }}
      />

      <div className="relative z-10 bg-white bg-opacity-70 p-8 rounded-lg shadow-lg w-full max-w-lg">
        <h1 className="text-3xl font-bold text-center text-gray-900 mb-6">Upload PDF</h1>

        {/* File Input */}
        <input
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-700 file:py-2 file:px-4 file:mr-4 file:border-0 file:bg-blue-500 file:text-white file:rounded-md cursor-pointer mb-4"
        />

        {/* Book Name */}
        <input
          type="text"
          placeholder="Book Name"
          value={bookName}
          onChange={(e) => setBookName(e.target.value)}
          className="block w-full text-sm text-gray-700 p-2 border rounded-md mb-4"
        />

        {/* Author Name */}
        <input
          type="text"
          placeholder="Author Name"
          value={authorName}
          onChange={(e) => setAuthorName(e.target.value)}
          className="block w-full text-sm text-gray-700 p-2 border rounded-md mb-4"
        />

        {/* Content Start Page */}
        <input
          type="number"
          placeholder="Content Details Starting Page No."
          value={contentStartPage}
          onChange={(e) => setContentStartPage(e.target.value)}
          className="block w-full text-sm text-gray-700 p-2 border rounded-md mb-4"
        />

        {/* Content End Page */}
        <input
          type="number"
          placeholder="Content Details Ending Page No."
          value={contentEndPage}
          onChange={(e) => setContentEndPage(e.target.value)}
          className="block w-full text-sm text-gray-700 p-2 border rounded-md mb-4"
        />

        {/* Chapter Start Page */}
        <input
          type="number"
          placeholder="Chapter Starting Page No."
          value={chapterStartPage}
          onChange={(e) => setChapterStartPage(e.target.value)}
          className="block w-full text-sm text-gray-700 p-2 border rounded-md mb-4"
        />

        {/* Chapter End Page */}
        <input
          type="number"
          placeholder="Chapter Ending Page No."
          value={chapterEndPage}
          onChange={(e) => setChapterEndPage(e.target.value)}
          className="block w-full text-sm text-gray-700 p-2 border rounded-md mb-4"
        />

        {/* Error Message */}
        {error && <div className="text-red-500 text-sm mb-4">{error}</div>}

        {/* Display Selected PDF */}
        {pdf && (
          <div className="text-gray-700 mb-4">
            <strong>Selected PDF: </strong> {pdf.name}
          </div>
        )}

        {/* Upload Button */}
        <button
          onClick={handleUpload}
          disabled={
            !pdf ||
            !bookName ||
            !authorName ||
            !contentStartPage ||
            !contentEndPage ||
            !chapterStartPage ||
            !chapterEndPage
          }
          className={`w-full py-2 px-4 rounded-lg text-white font-semibold ${
            pdf &&
            bookName &&
            authorName &&
            contentStartPage &&
            contentEndPage &&
            chapterStartPage &&
            chapterEndPage
              ? 'bg-green-500 hover:bg-green-600'
              : 'bg-gray-400 cursor-not-allowed'
          }`}
        >
          Upload
        </button>
      </div>
    </div>
  );
};

export default UploadPDF;
