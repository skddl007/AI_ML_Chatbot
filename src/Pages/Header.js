import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { auth, provider, signInWithPopup } from '../Firebase';

// Import the floating CSS file
import '../Pages/Floating.css';

const Header = () => {
  const [loading, setLoading] = useState(false);
  const [isSignedIn, setIsSignedIn] = useState(false); // State to track if the user has signed in
  const navigate = useNavigate();
  const location = useLocation();

  const signInWithGoogle = () => {
    setLoading(true);
    signInWithPopup(auth, provider)
      .then((result) => {
        console.log('User Info:', result.user);
        setIsSignedIn(true); // Update state after successful sign-in
        navigate('/upload'); // Redirect to upload page after successful sign-in
      })
      .catch((error) => {
        console.error('Error:', error);
        setLoading(false);
      });
  };

  return (
    <header className="bg-gradient-to-r from-gray-700 via-gray-800 to-gray-900 p-2 flex justify-between items-center shadow-lg animate-gradient">
      <div className="flex items-center">
        <img src="../user.png" className="text-xl float-text w-14" alt="User GIF" />
      </div>
      <nav className="space-x-6 text-sm px-2">
        <Link
          to="/"
          className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
        >
          Home
        </Link>
        <Link
          to="/services"
          className={`nav-link ${location.pathname === '/services' ? 'active' : ''}`}
        >
          Services
        </Link>
        <Link
          to="/chat"
          className={`nav-link ${location.pathname === '/chat' ? 'active' : ''}`}
        >
          Try for Free
        </Link>

        {/* Sign in button with dynamic underline based on the sign-in state */}
        <button
          onClick={signInWithGoogle}
          disabled={loading}
          className={`text-gray-200 hover:text-white transition duration-300 ${isSignedIn ? 'underline' : ''}`}
        >
          {loading ? 'Signing In...' : 'Sign In with Google'}
        </button>
      </nav>
    </header>
  );
};

export default Header;
