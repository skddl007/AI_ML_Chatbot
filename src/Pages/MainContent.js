
import React, { useEffect, useState } from 'react';
import { FaClipboardList, FaGoogle, FaRobot, FaUsers } from 'react-icons/fa'; // Import the Google icon
import { Link, useNavigate } from 'react-router-dom';
import { auth, provider, signInWithPopup } from '../Firebase'; // Ensure Firebase is set up properly
import '../Pages/Floating.css'; // Correct path if the file is in src/Pages/
import "../components/cursor.css";
import { BackgroundLines } from '../components/ui/background-lines.tsx';
// import Particle from './Particles'; // Import the Particle component

const MainContent = () => {
  const [loading, setLoading] = useState(false);
  const [displayedText, setDisplayedText] = useState(""); // For storing the typed text
  const fullText = "Whhat is AI?🤖"; // The text we want to animate
  const typingSpeed = 150; // Speed of typing animation (in ms)
  const navigate = useNavigate();

  const signInWithGoogle = () => {
    setLoading(true);
    signInWithPopup(auth, provider)
      .then((result) => {
        console.log('User Info:', result.user);
        navigate('/upload'); // Redirect to upload page after successful sign-in
      })
      .catch((error) => {
        console.error('Error:', error);
        setLoading(false);
      });
  };

  useEffect(() => {
    let index = 0;
    const timer = setInterval(() => {
      setDisplayedText((prev) => prev + fullText[index]);
      index++;
      if (index === (fullText.length-1)) clearInterval(timer); // Stop when all letters are typed
    }, typingSpeed);

    return () => {
      clearInterval(timer); // Cleanup on component unmount
    };
  }, []); // Empty dependency array to run the effect only once

  return (
    <main className="bg-[#2C3E50] text-white py-20 relative">
      {/* Particle background */}
      {/* <Particle /> */}
      <BackgroundLines
        className="my-background"  // Custom class for background
        svgOptions={{ duration: 10 }}  // Duration for SVG animation
      />

      <section className="text-center hover:scale-105 transform transition duration-300 ease-in-out relative z-10">
        <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-6">
          {displayedText}
        </h1>
        <p className="text-lg md:text-xl mb-8 max-w-3xl mx-auto">
          AI is the simulation of human intelligence in machines designed to think and learn like humans.
        </p>
        <div className="flex justify-center space-x-6">
          {/* Link for 'Try for Free' */}
          <Link
            to="/chat"  // Ensure the '/chat' path is defined in your router setup
            className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-full text-lg transition duration-300 ease-in-out transform hover:scale-105 border-2 border-blue-600 hover:border-blue-700"
          >
            Try for Free
          </Link>

          {/* Google Sign-In Button */}
          <button
            onClick={signInWithGoogle}
            disabled={loading}
            className="bg-[#34495E] hover:bg-[#5D6D7E] text-white py-2 px-4 rounded-full text-lg transition duration-300 ease-in-out transform hover:scale-105 border-2 border-[#5D6D7E] hover:border-[#34495E] flex items-center space-x-2"
          >
            <FaGoogle size={20} /> {/* Google icon */}
            <span>{loading ? 'Signing In...' : 'Sign In with Google'}</span>
          </button>
        </div>
      </section>

      {/* Key Features Section */}
      <section className="mt-20">
        <h2 className="text-3xl font-semibold text-center mb-12 text-white">Key Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 px-6">
          <div className="flex flex-col items-center text-center p-6 bg-[#34495E] text-gray-200 rounded-lg shadow-lg min-h-[250px] border-t-4 border-b-4"
              style={{
                borderTopColor: '#5B2C6F',
                borderBottomColor: '#D2B4DE',
              }}>
            <FaRobot size={60} className="mb-4 text-blue-400" />
            <h3 className="text-xl font-semibold">AI-Powered</h3>
            <p className="text-gray-300">Our chatbot uses advanced AI to understand and respond to your queries intelligently.</p>
          </div>

          <div className="flex flex-col items-center text-center p-6 bg-[#34495E] text-gray-200 rounded-lg shadow-lg min-h-[250px] border-t-4 border-b-4"
              style={{
                borderTopColor: '#5B2C6F',
                borderBottomColor: '#D2B4DE',
              }}>
            <FaUsers size={60} className="mb-4 text-blue-400" />
            <h3 className="text-xl font-semibold">Human-like Interaction</h3>
            <p className="text-gray-300">The chatbot mimics human-like conversations for a more seamless experience.</p>
          </div>

          <div className="flex flex-col items-center text-center p-6 bg-[#34495E] text-gray-200 rounded-lg shadow-lg min-h-[250px] border-t-4 border-b-4"
              style={{
                borderTopColor: '#5B2C6F',
                borderBottomColor: '#D2B4DE',
              }}>
            <FaClipboardList size={60} className="mb-4 text-blue-400" />
            <h3 className="text-xl font-semibold">24/7 Assistance</h3>
            <p className="text-gray-300">Get answers to your questions anytime, anywhere, with our chatbot available round the clock.</p>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="mt-20 bg-[#2C3E50] py-12">
        <h2 className="text-3xl font-semibold text-center text-white mb-8">What Our Users Say</h2>
        <div className="flex flex-col md:flex-row justify-center items-center md:space-x-6 space-y-6 md:space-y-0">
          <div className="max-w-sm p-6 bg-[#34495E] text-gray-200 rounded-lg shadow-lg min-h-[200px] flex-grow border-t-4 border-b-4"
              style={{
                borderTopColor: '#5B2C6F',
                borderBottomColor: '#D2B4DE',
              }}>
            <p className="text-gray-300">"This chatbot is a game-changer. It has helped me save hours of time by answering my questions instantly."</p>
            <div className="mt-4 text-right font-semibold">- Satyam</div>
          </div>
          <div className="max-w-sm p-6 bg-[#34495E] text-gray-200 rounded-lg shadow-lg min-h-[200px] flex-grow border-t-4 border-b-4"
              style={{
                borderTopColor: '#5B2C6F',
                borderBottomColor: '#D2B4DE',
              }}>
            <p className="text-gray-300">"I love how easy it is to interact with this AI. It feels like talking to a real person!"</p>
            <div className="mt-4 text-right font-semibold">- Shubham</div>
          </div>
        </div>
      </section>
    </main>
  );
};

export default MainContent;
