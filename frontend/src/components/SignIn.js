import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { auth, provider, signInWithPopup } from '../Firebase';

const SignIn = () => {
  const [loading, setLoading] = useState(false);
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

  return (
    <div className="flex justify-center items-center h-screen">
      <button
        onClick={signInWithGoogle}
        disabled={loading}
        className="flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
      >
        {loading ? (
          'Signing In...'
        ) : (
          <>
            <img
              src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Google_2015_logo.svg/512px-Google_2015_logo.svg.png"
              alt="Google logo"
              className="w-6 h-6 mr-2"
            />
            Sign in with Google
          </>
        )}
      </button>
    </div>
  );
};

export default SignIn;
