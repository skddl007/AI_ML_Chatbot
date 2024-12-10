import React from "react";

export function Card({ children, className }) {
  return <div className={`bg-gray-800 p-4 rounded-lg shadow-md ${className}`}>{children}</div>;
}
