// src/components/ui/dropdown-menu.jsx

import React from 'react';

export function DropdownMenu({ children }) {
  return <div className="dropdown-menu">{children}</div>;
}

export function DropdownMenuContent({ children }) {
  return <div className="dropdown-menu-content">{children}</div>;
}

export function DropdownMenuItem({ children, onClick }) {
  return (
    <div className="dropdown-menu-item" onClick={onClick}>
      {children}
    </div>
  );
}

export function DropdownMenuTrigger({ children, asChild }) {
  return <div className="dropdown-menu-trigger">{children}</div>;
}
