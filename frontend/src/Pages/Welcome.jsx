import React from "react";
import { Link } from "react-router-dom";

const Welcome = () => {
  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-100">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">
          Welcome to My App
        </h1>
        <div className="space-x-4">
          <Link
            to="/login"
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md transition"
          >
            Login
          </Link>
          <Link
            to="/signup"
            className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg shadow-md transition"
          >
            Sign Up
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Welcome;
