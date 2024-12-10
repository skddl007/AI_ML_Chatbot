// src/components/Footer.js
import React from 'react';
import { FaGithub, FaLinkedin, FaTwitter } from 'react-icons/fa';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="bg-gray-800 p-6 text-gray-300 shadow-inner">
      <div className="container mx-auto flex flex-col md:flex-row justify-between">
        <div className="mb-4 md:mb-0">
          <div className="font-bold text-white mb-2">Quick Links</div>
          <nav className="space-y-1">
            <Link to="/" className="hover:text-white block">Home</Link>
            <Link to="/services" className="hover:text-white block">Services</Link>
            <Link to="/chat" className="hover:text-white block">Try for Free</Link>
            <Link to="/signin" className="hover:text-white block">Sign In</Link>
          </nav>
        </div>
        <div className="mb-4 md:mb-0">
          <div className="font-bold text-white mb-2">Contact</div>
          <div className="space-y-1">
            <div>Name: Sandeep Kumar</div>
            <div>Mobile: 9982385483</div>
            <div>Email: ddlsandeep7@gmail.com</div>
          </div>
        </div>
        <div className="mb-4 md:mb-0">
          <div className="font-bold text-white mb-2">Follow Us</div>
          <div className="flex space-x-4">
            <a href="https://www.linkedin.com/in/skddl007" className="hover:text-white">
              <FaLinkedin size={24} />
            </a>
            <a href="https://twitter.com/skddl007" className="hover:text-white">
              <FaTwitter size={24} />
            </a>
            <a href="https://github.com/skddl007" className="hover:text-white">
              <FaGithub size={24} />
            </a>
          </div>
        </div>
      </div>
      <div className="container mx-auto mt-6 flex justify-center text-gray-400">
        <p className="text-center">Developed by Sandeep Kumar</p>
      </div>
    </footer>
  );
};

export default Footer;
