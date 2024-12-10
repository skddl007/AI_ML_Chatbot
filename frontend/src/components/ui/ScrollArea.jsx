import React from "react";

export function ScrollArea({ children, className }) {
  return (
    <div
      className={`overflow-y-auto scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-gray-900 ${className}`}
    >
      {children}
    </div>
  );
}
