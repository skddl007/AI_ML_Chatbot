import React from "react";

export const Modal = ({ children, onClose }) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black opacity-50" onClick={onClose}></div>
      <div className="relative bg-gray-800 rounded-lg p-4">{children}</div>
    </div>
  );
};
