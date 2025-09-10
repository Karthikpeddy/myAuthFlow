import React from "react";
import { Link } from "react-router-dom";
import logo from "../assets/logo.svg"; // update with your image path

const Welcome = () => {
  return (
    <div className="relative min-h-screen bg-gray-100 flex flex-col">
      {/* logo in top-left */}
      <div className="absolute top-4 left-4">
        <img
          src={logo}
          alt="App logo"
          className="w-34 h-auto object-contain"
        />
      </div>

      {/* Centered Buttons */}
      <div className="flex flex-1 justify-center items-center">
        <div className="space-x-6">
          <Link
            to="/login"
            className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md transition"
          >
            Login
          </Link>
          <Link
            to="/signup"
            className="px-8 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg shadow-md transition"
          >
            Sign Up
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Welcome;

