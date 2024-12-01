import React from "react";

export function Avatar({ children }) {
  return <div className="inline-flex items-center justify-center rounded-full bg-gray-500 w-10 h-10">{children}</div>;
}

export function AvatarImage({ src }) {
  return <img src={src} alt="Avatar" className="rounded-full w-full h-full object-cover" />;
}

export function AvatarFallback({ children }) {
  return <span className="text-white text-sm font-medium">{children}</span>;
}
