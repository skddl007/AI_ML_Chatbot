import React from 'react';
import { FaBook, FaComments, FaQuestionCircle, FaUpload } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import { auth, provider, signInWithPopup } from '../Firebase'; // Import Firebase utilities
import { BackgroundLines } from './ui/background-lines.tsx';

const Services = () => {
  const navigate = useNavigate();

  const handleUploadClick = () => {
    // Trigger Google Sign-in directly
    signInWithPopup(auth, provider)
      .then((result) => {
        console.log('User Info:', result.user);
        navigate('/upload'); // Redirect to the upload page after successful sign-in
      })
      .catch((error) => {
        console.error('Sign-in Error:', error);
      });
  };

  return (
    <main className="relative bg-[#2C3E50] text-white py-20 px-6">
      <BackgroundLines
        className="my-background absolute inset-0 z-0"
        svgOptions={{ duration: 10 }}
      />
      <section className="text-center mb-12 relative z-10">
        <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-6">
          Our AI/ML Chatbot Services
        </h1>
        <p className="text-lg md:text-xl mb-8 max-w-3xl mx-auto">
          Explore the features of our AI/ML chatbot designed to assist you with your AI/ML-related queries and provide valuable insights from your uploaded PDFs.
        </p>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-1 max-w-6xl mx-auto relative z-10">
        <div
          onClick={handleUploadClick} // Handle click to initiate sign-in and redirect
          className="flex flex-col items-center text-center p-6 bg-[#34495E] text-gray-200 rounded-lg shadow-lg border-t-4 border-b-4 border-purple-600 w-full max-w-md mx-auto mb-4 cursor-pointer"
        >
          <FaUpload size={60} className="mb-4 text-blue-400" />
          <h3 className="text-xl font-semibold">Upload Your PDF</h3>
          <p className="text-gray-300">
            Upload your AI/ML-related PDFs and ask any questions related to the content.
          </p>
        </div>

        <div className="flex flex-col items-center text-center p-6 bg-[#34495E] text-gray-200 rounded-lg shadow-lg border-t-4 border-b-4 border-purple-600 w-full max-w-md mx-auto mb-4">
          <FaBook size={60} className="mb-4 text-blue-400" />
          <h3 className="text-xl font-semibold">Get Information</h3>
          <p className="text-gray-300">
            Retrieve details such as page number, chapter name, book name, author, and more related to your query.
          </p>
        </div>

        <div className="flex flex-col items-center text-center p-6 bg-[#34495E] text-gray-200 rounded-lg shadow-lg border-t-4 border-b-4 border-purple-600 w-full max-w-md mx-auto mb-4">
          <FaQuestionCircle size={60} className="mb-4 text-blue-400" />
          <h3 className="text-xl font-semibold">Unlimited Queries</h3>
          <p className="text-gray-300">
            Ask unlimited questions to our AI/ML chatbot and get instant responses.
          </p>
        </div>

        <div className="flex flex-col items-center text-center p-6 bg-[#34495E] text-gray-200 rounded-lg shadow-lg border-t-4 border-b-4 border-purple-600 w-full max-w-md mx-auto mb-4">
          <FaComments size={60} className="mb-4 text-blue-400" />
          <h3 className="text-xl font-semibold">AI/ML Book Responses</h3>
          <p className="text-gray-300">
            Get comprehensive responses related to AI/ML books from our chatbot.
          </p>
        </div>
      </section>
    </main>
  );
};

export default Services;
