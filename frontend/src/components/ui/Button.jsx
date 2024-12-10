import React from "react";
import classNames from "classnames";

export function Button({ children, variant, size, className, ...props }) {
  const variants = {
    ghost: "bg-transparent hover:bg-gray-700 text-gray-400",
    outline: "border border-gray-700 hover:bg-gray-700 text-gray-400",
    secondary: "bg-gray-700 text-white hover:bg-gray-600",
  };

  const sizes = {
    sm: "px-2 py-1 text-sm",
    icon: "p-2",
  };

  return (
    <button
      className={classNames(
        "rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
